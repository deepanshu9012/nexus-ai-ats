import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.qdrant_service import delete_all_resumes, delete_resumes, get_all_resumes


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Candidates"])


class DeleteRequest(BaseModel):
    ids: list


@router.get("/api/candidates")
def list_candidates():
    try:
        return get_all_resumes()
    except Exception as exc:
        logger.exception("Failed to list candidate records.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to fetch candidate records."},
        ) from exc


@router.delete("/api/candidates")
def remove_candidates(payload: DeleteRequest):
    try:
        delete_resumes(payload.ids)
        return {"message": "Selected candidates deleted."}
    except Exception as exc:
        logger.exception("Failed to delete selected candidate records.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to delete selected candidate records."},
        ) from exc


@router.delete("/api/candidates/all")
def remove_all_candidates():
    try:
        delete_all_resumes()
        return {"message": "All candidates deleted."}
    except Exception as exc:
        logger.exception("Failed to delete all candidate records.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to delete all candidate records."},
        ) from exc
