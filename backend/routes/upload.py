import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.responses import UploadResumeResponse
from services.resume_service import (
    ResumeConfigError,
    ResumeInputError,
    ResumeProcessingError,
    extract_candidate_profile_from_pdf,
)


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


router = APIRouter(tags=["upload"])


@router.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(file: UploadFile = File(...)) -> UploadResumeResponse:
    try:
        pdf_bytes = await file.read()
        candidate_profile = extract_candidate_profile_from_pdf(pdf_bytes)
    except ResumeInputError as exc:
        logger.exception("Resume upload failed due to invalid input.")
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    except ResumeConfigError as exc:
        logger.exception("Resume upload failed due to server configuration.")
        raise HTTPException(status_code=500, detail={"message": str(exc)}) from exc
    except ResumeProcessingError as exc:
        logger.exception("Resume upload failed during downstream processing.")
        raise HTTPException(status_code=502, detail={"message": str(exc)}) from exc
    except Exception as exc:
        logger.exception("Unexpected error while processing resume upload.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error while processing resume."},
        ) from exc

    return UploadResumeResponse(
        filename=file.filename or "uploaded_resume.pdf",
        candidate_profile=candidate_profile,
    )
