from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile


class MatchLevel(str, Enum):
    EXACT = "EXACT"
    RELATED = "RELATED"
    MISSING = "MISSING"


class SkillMatchDetail(BaseModel):
    skill_name: str
    match_level: MatchLevel
    matched_candidate_skill: str | None = None
    relationship_type: str = "EXACT"
    score_weight: float = 1.0
    explanation: str = ""


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
    matched_skills: list[str] = Field(default_factory=list)
    exact_matched_skills: list[str] = Field(default_factory=list)
    related_matched_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    match_details: list[SkillMatchDetail] = Field(default_factory=list)
    confidence_level: str = "HIGH"
    evidence_coverage_pct: float = 100.0

