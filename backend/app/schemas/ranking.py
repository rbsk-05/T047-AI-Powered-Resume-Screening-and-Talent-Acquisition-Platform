from pydantic import BaseModel, Field

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile
from app.schemas.match import MatchResult


class RankingRequest(BaseModel):
    job_profile: JobProfile
    candidates: list[CandidateProfile] = Field(min_length=2, max_length=200)


class RankedCandidate(BaseModel):
    rank: int
    candidate_name: str
    match: MatchResult


class CandidateComparison(BaseModel):
    candidate_name: str
    overall_match_score: float
    matched_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]


class RankingResult(BaseModel):
    ranked_candidates: list[RankedCandidate]


class ComparisonResult(BaseModel):
    candidates: list[CandidateComparison]
