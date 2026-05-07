import json
import os
from typing import List

from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"
MAX_PARSE_RETRIES = 3


class CandidateProfile(BaseModel):
    skills: List[str]
    years_experience: int
    education: str


def extract_candidate_profile(resume_text: str) -> dict:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    client = _build_groq_client()
    last_error: Exception | None = None

    for attempt in range(1, MAX_PARSE_RETRIES + 1):
        response_text = _request_profile_json(
            client=client,
            resume_text=resume_text,
            retry_context=str(last_error) if last_error else None,
        )

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


def _build_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def _request_profile_json(
    client: Groq, resume_text: str, retry_context: str | None = None
) -> str:
    system_prompt = (
        "You are a resume parser. Extract structured candidate data and respond with a "
        "single valid JSON object only. No markdown, no extra text."
    )

    user_prompt = (
        "Extract the candidate profile from this resume text.\n"
        "Return exactly one JSON object with keys: skills (array of strings), "
        "years_experience (integer), education (string).\n\n"
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
