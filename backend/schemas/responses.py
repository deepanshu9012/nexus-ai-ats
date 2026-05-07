from pydantic import BaseModel


class CandidateProfileResponse(BaseModel):
    skills: list[str]
    years_experience: int
    education: str


class UploadResumeResponse(BaseModel):
    filename: str
    candidate_profile: CandidateProfileResponse


class HealthResponse(BaseModel):
    status: str
