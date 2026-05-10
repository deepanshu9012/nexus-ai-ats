import logging

from fastapi import APIRouter, HTTPException

from schemas.requests import SearchRequest
from schemas.responses import SearchMatch, SearchResponse
from services.search_service import SearchInputError, SearchProcessingError, search_candidates


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search_resumes(request: SearchRequest) -> SearchResponse:
    try:
        matches = search_candidates(query=request.query, limit=request.limit)
    except SearchInputError as exc:
        logger.exception("Search request failed due to invalid input.")
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    except SearchProcessingError as exc:
        logger.exception("Search request failed during processing.")
        raise HTTPException(status_code=500, detail={"message": str(exc)}) from exc
    except Exception as exc:
        logger.exception("Unexpected error while searching resumes.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error while searching resumes."},
        ) from exc

    return SearchResponse(
        results=[
            SearchMatch(
                score=match["score"],
                database_id=match["id"],
                candidate_profile=match["profile"],
            )
            for match in matches
        ]
    )
