import logging
import os
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

from services.vector_service import EMBEDDING_DIMENSION


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "resumes")

_qdrant_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _qdrant_client

    if _qdrant_client is None:
        try:
            _qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        except Exception as exc:
            logger.exception("Failed to initialize Qdrant client.")
            raise RuntimeError("Qdrant client initialization failed.") from exc

    return _qdrant_client


def init_collection() -> None:
    try:
        client = _get_client()
        collection_exists = client.collection_exists(collection_name=QDRANT_COLLECTION_NAME)

        if not collection_exists:
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'.", QDRANT_COLLECTION_NAME)

        client.create_payload_index(
            collection_name=QDRANT_COLLECTION_NAME,
            field_name="profile.skills",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                lowercase=True,
            ),
        )
    except Exception as exc:
        logger.exception("Failed to initialize Qdrant collection.")
        raise RuntimeError("Qdrant collection initialization failed.") from exc


def upsert_resume_record(candidate_profile: dict, text: str, embedding: list[float]) -> str:
    if not candidate_profile:
        raise ValueError("Candidate profile is required for Qdrant upsert.")
    if not text or not text.strip():
        raise ValueError("Resume text is required for Qdrant upsert.")
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding size must be {EMBEDDING_DIMENSION}, got {len(embedding)}."
        )

    record_id = str(uuid.uuid4())

    try:
        client = _get_client()
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=record_id,
                    vector=embedding,
                    payload={
                        "profile": candidate_profile,
                        "raw_text": text,
                    },
                )
            ],
        )
        return record_id
    except Exception as exc:
        logger.exception("Failed to upsert resume record into Qdrant.")
        raise RuntimeError("Qdrant upsert failed.") from exc


def search_resumes(
    query_vector: list[float],
    limit: int = 5,
    min_experience: float | None = None,
    required_skills: list[str] | None = None,
) -> list[dict]:
    if len(query_vector) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Query vector size must be {EMBEDDING_DIMENSION}, got {len(query_vector)}."
        )
    if limit < 1:
        raise ValueError("Search limit must be at least 1.")
    if min_experience is not None and min_experience < 0:
        raise ValueError("Minimum experience filter cannot be negative.")
    if required_skills is not None and not isinstance(required_skills, list):
        raise ValueError("Required skills must be a list of strings.")

    try:
        client = _get_client()
        query_filter = None
        must_conditions: list[models.FieldCondition] = []

        if min_experience is not None:
            must_conditions.append(
                models.FieldCondition(
                    key="profile.years_experience",
                    range=models.Range(gte=min_experience),
                )
            )

        if required_skills:
            for skill in required_skills:
                if not isinstance(skill, str):
                    continue
                normalized_skill = skill.strip()
                if not normalized_skill:
                    continue
                must_conditions.append(
                    models.FieldCondition(
                        key="profile.skills",
                        match=models.MatchText(text=normalized_skill.lower()),
                    )
                )

        if must_conditions:
            query_filter = models.Filter(must=must_conditions)

        search_results = client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )

        parsed_results: list[dict] = []
        for point in search_results:
            payload = point.payload or {}
            parsed_results.append(
                {
                    "id": str(point.id),
                    "score": float(point.score),
                    "profile": payload.get("profile", {}),
                }
            )
        return parsed_results
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to search resumes in Qdrant.")
        raise RuntimeError("Qdrant search failed.") from exc


def get_all_resumes(limit: int = 100):
    try:
        client = _get_client()
        if not client.collection_exists(QDRANT_COLLECTION_NAME):
            return []
        records = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=limit,
            with_payload=True,
        )[0]
        return [
            {"id": record.id, "profile": (record.payload or {}).get("profile", {})}
            for record in records
        ]
    except Exception as exc:
        logger.exception("Failed to fetch resumes from Qdrant.")
        raise RuntimeError("Failed to fetch candidate records.") from exc


def delete_resumes(point_ids: list):
    try:
        client = _get_client()
        if not client.collection_exists(QDRANT_COLLECTION_NAME):
            return
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=models.PointIdsList(points=point_ids),
        )
    except Exception as exc:
        logger.exception("Failed to delete selected resumes from Qdrant.")
        raise RuntimeError("Failed to delete selected candidate records.") from exc


def delete_all_resumes():
    try:
        client = _get_client()
        if not client.collection_exists(QDRANT_COLLECTION_NAME):
            return
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter()
            )
        )
    except Exception as exc:
        logger.exception("Failed to delete all resumes from Qdrant collection.")
        raise RuntimeError("Failed to delete all candidate records.") from exc

