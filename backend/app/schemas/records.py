from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateEvaluation
from app.schemas.job import JobCreateRequest, JobProfile
from app.schemas.match import MatchResult


class StoredJob(BaseModel):
    id: UUID
    title: str
    description: str
    company_name: str | None = None
    location: str | None = None
    employment_type: str | None = None
    experience_required: str | None = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    education: list[str] = []
    status: str = "published"
    profile: JobProfile
    created_at: datetime



class StoredCandidate(BaseModel):
    id: UUID
    profile: CandidateProfile
    resume_filename: str | None
    created_at: datetime


class ApplicationCreate(BaseModel):
    job_id: UUID
    candidate_id: UUID


class StoredApplication(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    status: str
    match: MatchResult
    evaluation: CandidateEvaluation
    created_at: datetime
    # Added for UI display
    job_title: str | None = None
    company_name: str | None = None

