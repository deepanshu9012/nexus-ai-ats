import logging

from sentence_transformers import SentenceTransformer


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model

    if _embedding_model is None:
        try:
            _embedding_model = SentenceTransformer(MODEL_NAME)
        except Exception as exc:
            logger.exception("Failed to initialize sentence transformer model.")
            raise RuntimeError("Embedding model initialization failed.") from exc

    return _embedding_model


def generate_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding from empty text.")

    try:
        model = _get_embedding_model()
        embedding = model.encode(text)
        vector = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)

        if len(vector) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Unexpected embedding size: {len(vector)}. Expected {EMBEDDING_DIMENSION}."
            )

        return [float(value) for value in vector]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to generate embedding from resume text.")
        raise RuntimeError("Embedding generation failed.") from exc
