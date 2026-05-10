import logging

from services.llm_service import parse_search_query
from services.qdrant_service import search_resumes
from services.vector_service import generate_embedding


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class SearchServiceError(Exception):
    """Base exception for search processing errors."""


class SearchInputError(SearchServiceError):
    """Raised when search input is invalid."""


class SearchProcessingError(SearchServiceError):
    """Raised when search processing fails."""


def search_candidates(query: str, limit: int) -> list[dict]:
    if not query or not query.strip():
        raise SearchInputError("Search query cannot be empty.")
    if limit < 1:
        raise SearchInputError("Search limit must be at least 1.")

    try:
        filters = parse_search_query(query)
        min_experience = filters.get("min_experience")
        required_skills = filters.get("required_skills", [])
    except ValueError as exc:
        logger.exception("Invalid input while parsing search query filters.")
        raise SearchInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error while parsing search query filters.")
        raise SearchProcessingError("Failed to parse search query filters.") from exc

    try:
        query_embedding = generate_embedding(query)
    except ValueError as exc:
        logger.exception("Invalid input while generating query embedding.")
        raise SearchInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error while generating query embedding.")
        raise SearchProcessingError("Failed to generate search query embedding.") from exc

    try:
        return search_resumes(
            query_vector=query_embedding,
            limit=limit,
            min_experience=min_experience,
            required_skills=required_skills,
        )
    except ValueError as exc:
        logger.exception("Invalid search inputs for vector database query.")
        raise SearchInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error while retrieving search results from Qdrant.")
        raise SearchProcessingError("Failed to retrieve candidate matches.") from exc
