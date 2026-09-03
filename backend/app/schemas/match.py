from pydantic import BaseModel, Field

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile


class MatchRequest(BaseModel):
    job_profile: JobProfile
    candidate_profile: CandidateProfile


class ScoreBreakdown(BaseModel):
    required_skills: float = Field(ge=0, le=100)
    experience: float = Field(ge=0, le=100)
    education: float = Field(ge=0, le=100)
    projects: float = Field(ge=0, le=100)
    semantic_similarity: float = Field(ge=0, le=100)
    certifications: float = Field(ge=0, le=100)


class MatchResult(BaseModel):
    overall_match_score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    matched_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
