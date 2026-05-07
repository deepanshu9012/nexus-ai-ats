import logging

from services.llm_service import extract_candidate_profile
from services.parser_service import extract_text_from_pdf


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class ResumeServiceError(Exception):
    """Base exception for resume processing errors."""


class ResumeInputError(ResumeServiceError):
    """Raised when the uploaded input is invalid."""


class ResumeConfigError(ResumeServiceError):
    """Raised when server configuration is invalid."""


class ResumeProcessingError(ResumeServiceError):
    """Raised when processing fails due to downstream/runtime errors."""


def extract_candidate_profile_from_pdf(pdf_bytes: bytes) -> dict:
    try:
        extracted_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as exc:
        logger.exception("Resume input validation failed during PDF text extraction.")
        raise ResumeInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error while extracting text from PDF.")
        raise ResumeProcessingError("Failed to extract text from the uploaded PDF.") from exc

    try:
        return extract_candidate_profile(extracted_text)
    except ValueError as exc:
        logger.exception("Validation/configuration error during candidate profile extraction.")
        if "GROQ_API_KEY" in str(exc):
            raise ResumeConfigError("Server is missing GROQ API configuration.") from exc
        raise ResumeInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error during candidate profile extraction.")
        raise ResumeProcessingError(
            "Failed to generate a structured candidate profile from resume text."
        ) from exc
