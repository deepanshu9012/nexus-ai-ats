import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.responses import UploadResumeResponse
from services.llm_service import extract_candidate_profile
from services.parser_service import extract_text_from_file
from services.qdrant_service import upsert_resume_record
from services.resume_service import calculate_total_experience
from services.vector_service import generate_embedding


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


router = APIRouter(tags=["upload"])


@router.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(file: UploadFile = File(...)) -> UploadResumeResponse:
    try:
        file_bytes = await file.read()
        extracted_text = extract_text_from_file(file_bytes, file.filename or "")

        candidate_profile = extract_candidate_profile(extracted_text)
        candidate_profile["years_experience"] = calculate_total_experience(
            candidate_profile.get("work_history", [])
        )
        candidate_profile["experience_details"] = candidate_profile.get("experience_details", "")

        embedding = generate_embedding(extracted_text)
        record_id = upsert_resume_record(
            candidate_profile=candidate_profile,
            text=extracted_text,
            embedding=embedding,
        )
        resume_record = {"id": record_id, "profile": candidate_profile}
    except ValueError as exc:
        logger.exception("Resume upload failed due to invalid input.")
        if "GROQ_API_KEY" in str(exc):
            raise HTTPException(
                status_code=500,
                detail={"message": "Server is missing GROQ API configuration."},
            ) from exc
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    except RuntimeError as exc:
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
        database_id=resume_record["id"],
        candidate_profile=resume_record["profile"],
    )
