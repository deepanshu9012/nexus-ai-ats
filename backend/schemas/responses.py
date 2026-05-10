from pydantic import BaseModel, Field


class JobResponse(BaseModel):
    title: str
    start_date: str
    end_date: str


class CandidateProfileResponse(BaseModel):
    name: str
    email: str
    work_history: list[JobResponse] = Field(default_factory=list)
    skills: list[str]
    years_experience: float
    education: str


class UploadResumeResponse(BaseModel):
    filename: str
    database_id: str
    candidate_profile: CandidateProfileResponse


class SearchMatch(BaseModel):
    score: float
    database_id: str
    candidate_profile: CandidateProfileResponse


class SearchResponse(BaseModel):
    results: list[SearchMatch]


class HealthResponse(BaseModel):
    status: str
