import logging
import re
from datetime import datetime

from services.llm_service import extract_candidate_profile
from services.parser_service import extract_text_from_pdf
from services.qdrant_service import upsert_resume_record
from services.vector_service import generate_embedding


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


def calculate_total_experience(work_history: list[dict]) -> float:
    if not isinstance(work_history, list):
        return 0.0

    try:
        current_month = datetime.utcnow().replace(day=1)
        intervals: list[tuple[int, int]] = []

        for job in work_history:
            if not isinstance(job, dict):
                continue

            start_raw = str(job.get("start_date", "")).strip()
            end_raw = str(job.get("end_date", "")).strip()

            start = _parse_year_month(start_raw, current_month)
            end = _parse_year_month(end_raw, current_month)
            if start is None or end is None or end < start:
                continue

            start_index = start.year * 12 + start.month
            end_index = end.year * 12 + end.month
            intervals.append((start_index, end_index))

        if not intervals:
            return 0.0

        intervals.sort(key=lambda interval: interval[0])
        merged: list[list[int]] = [[intervals[0][0], intervals[0][1]]]

        for start_idx, end_idx in intervals[1:]:
            last_start, last_end = merged[-1]
            if start_idx <= last_end + 1:
                merged[-1][1] = max(last_end, end_idx)
            else:
                merged.append([start_idx, end_idx])

        total_months = sum((end_idx - start_idx + 1) for start_idx, end_idx in merged)
        return round(total_months / 12.0, 1)
    except Exception:
        return 0.0


def _parse_year_month(value: str, current_month: datetime) -> datetime | None:
    if not value:
        return None
        
    normalized = value.strip().lower()
    if "present" in normalized or "current" in normalized:
        return current_month

    # Safely extract a 4-digit year
    year_match = re.search(r"(\d{4})", normalized)
    if not year_match:
        return None
    year = int(year_match.group(1))

    # Safely extract a month (either digit or text)
    month = 1  # Default to January if the AI only gave us a year
    month_match = re.search(r"\b(0?[1-9]|1[0-2]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", normalized)
    
    if month_match:
        m_str = month_match.group(1)
        if m_str.isdigit():
            month = int(m_str)
        else:
            month_map = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}
            month = month_map.get(m_str[:3], 1)

    return datetime(year=year, month=month, day=1)


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
        candidate_profile = extract_candidate_profile(extracted_text)
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

    calculated_years = calculate_total_experience(
        candidate_profile.get("work_history", [])
    )
    candidate_profile["years_experience"] = calculated_years

    try:
        embedding = generate_embedding(extracted_text)
        record_id = upsert_resume_record(
            candidate_profile=candidate_profile,
            text=extracted_text,
            embedding=embedding,
        )
    except ValueError as exc:
        logger.exception("Validation error while generating embedding or storing resume.")
        raise ResumeInputError(str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Runtime error while generating embedding or storing resume.")
        raise ResumeProcessingError("Failed to persist resume record in vector storage.") from exc

    return {
        "id": record_id,
        "profile": candidate_profile,
    }
