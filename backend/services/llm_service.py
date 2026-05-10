import json
import os
import time
from typing import List

from groq import Groq
try:
    from groq import RateLimitError
except Exception:  # pragma: no cover
    RateLimitError = None
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"
MAX_PARSE_RETRIES = 3


class Job(BaseModel):
    title: str
    start_date: str
    end_date: str


class CandidateProfile(BaseModel):
    work_history: List[Job] = Field(default_factory=list)
    name: str
    email: str
    skills: List[str]
    years_experience: float = 0
    education: str
    experience_details: str = Field(
        default="",
        description=(
            "Locate the specific section in the resume explicitly titled "
            "'EXPERIENCE', 'WORK EXPERIENCE', or 'EMPLOYMENT'. Extract the "
            "chronological list of job titles, companies, dates, and the bullet "
            "points of responsibilities found in that section. Do NOT extract the "
            "candidate's 'Profile', 'Summary', or 'Objective' paragraph from the "
            "top of the resume. Return the extracted jobs as a clearly formatted "
            "string with line breaks. If no Experience section exists, return an "
            "empty string."
        ),
    )


class SearchFilters(BaseModel):
    min_experience: float | None = None
    required_skills: list[str] = Field(default_factory=list)


def extract_candidate_profile(resume_text: str) -> dict:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    client = _build_groq_client()
    last_error: Exception | None = None

    for attempt in range(1, MAX_PARSE_RETRIES + 1):
        try:
            response_text = _request_profile_json(
                client=client,
                resume_text=resume_text,
                retry_context=str(last_error) if last_error else None,
            )
        except Exception as exc:
            is_rate_limit = (
                (RateLimitError is not None and isinstance(exc, RateLimitError))
                or "429" in str(exc)
            )
            if is_rate_limit:
                last_error = exc
                print("Rate limit reached. Sleeping for 20 seconds...")
                time.sleep(20)
                continue
            raise

        try:
            payload = _parse_json_object(response_text)
            profile = CandidateProfile.model_validate(payload)
            return profile.model_dump()
        except (json.JSONDecodeError, ValueError, ValidationError) as exc:
            last_error = exc
            if attempt == MAX_PARSE_RETRIES:
                raise RuntimeError(
                    "Failed to parse a valid structured profile from Groq response."
                ) from exc

    raise RuntimeError("Failed to extract structured profile.")


def parse_search_query(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Search query is empty.")

    client = _build_groq_client()
    last_error: Exception | None = None

    for attempt in range(1, MAX_PARSE_RETRIES + 1):
        try:
            response_text = _request_search_filters_json(
                client=client,
                query=query,
                retry_context=str(last_error) if last_error else None,
            )
        except Exception as exc:
            is_rate_limit = (
                (RateLimitError is not None and isinstance(exc, RateLimitError))
                or "429" in str(exc)
            )
            if is_rate_limit:
                last_error = exc
                print("Rate limit reached. Sleeping for 20 seconds...")
                time.sleep(20)
                continue
            raise

        try:
            payload = _parse_json_object(response_text)
            filters = SearchFilters.model_validate(payload)
            return filters.model_dump()
        except (json.JSONDecodeError, ValueError, ValidationError) as exc:
            last_error = exc
            if attempt == MAX_PARSE_RETRIES:
                raise RuntimeError(
                    "Failed to parse valid search filters from Groq response."
                ) from exc

    raise RuntimeError("Failed to parse search query filters.")


def _build_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def _request_profile_json(
    client: Groq, resume_text: str, retry_context: str | None = None
) -> str:
    system_prompt = (
        "You are an expert ATS resume parser. Extract structured candidate data and respond with a "
        "single valid JSON object only. No markdown, no extra text."
    )

    user_prompt = (
        "Extract the candidate profile from this resume text.\n"
        "Return exactly one JSON object with keys: name (string), email (string), "
        "skills (array of strings), education (string), experience_details (string), "
        "and work_history (array of objects).\n"
        "Each work_history item must have: title (string), start_date (YYYY-MM), "
        "end_date (YYYY-MM or Present).\n"
        "CRITICAL INSTRUCTION FOR experience_details:\n"
        "Locate the specific section in the resume explicitly titled 'EXPERIENCE', 'WORK EXPERIENCE', or 'EMPLOYMENT'. "
        "Extract the chronological list of job titles, companies, dates, and the bullet points of responsibilities found in that section. "
        "Do NOT extract the candidate's 'Profile', 'Summary', or 'Objective' paragraph from the top of the resume. "
        "Return the extracted jobs as a clearly formatted string with line breaks. If no Experience section exists, return an empty string.\n\n"
        "Do not calculate years_experience.\n\n"
        f"Resume text:\n{resume_text}"
    )

    if retry_context:
        user_prompt += (
            "\n\nYour previous response could not be parsed or validated. "
            f"Validation issue: {retry_context}\n"
            "Fix the response and return strict JSON only."
        )

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = completion.choices[0].message.content
    if not content:
        raise RuntimeError("Groq returned an empty response.")
    return content.strip()


def _request_search_filters_json(
    client: Groq, query: str, retry_context: str | None = None
) -> str:
    system_prompt = (
        "You extract strict filters from candidate search queries. "
        "Return a single valid JSON object only, with no markdown or extra text."
    )

    user_prompt = (
        "Extract strict search filters from this candidate search query.\n"
        "Return exactly one JSON object with keys:\n"
        "- min_experience (number or null)\n"
        "- required_skills (array of strings)\n"
        "Set min_experience to null if no explicit minimum years of experience is requested.\n"
        "Set required_skills to an empty array if no explicit technologies, tools, or "
        "programming languages are requested.\n\n"
        f"Search query:\n{query}"
    )

    if retry_context:
        user_prompt += (
            "\n\nYour previous response could not be parsed or validated. "
            f"Validation issue: {retry_context}\n"
            "Fix the response and return strict JSON only."
        )

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = completion.choices[0].message.content
    if not content:
        raise RuntimeError("Groq returned an empty response.")
    return content.strip()


def _parse_json_object(text: str) -> dict:
    stripped = text.strip()

    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip().startswith("```"):
            stripped = "\n".join(lines[1:-1]).strip()
            if stripped.lower().startswith("json"):
                stripped = stripped[4:].strip()

    parsed = json.loads(stripped)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")
    return parsed
