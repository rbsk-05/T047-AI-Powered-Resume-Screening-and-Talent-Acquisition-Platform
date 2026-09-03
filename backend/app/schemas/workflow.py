from pydantic import BaseModel

from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateEvaluation
from app.schemas.gap import SkillGapResult
from app.schemas.job import JobProfile
from app.schemas.match import MatchResult
from app.schemas.recommendation import RecommendationResult


class CandidateWorkflowRequest(BaseModel):
    job_profile: JobProfile
    candidate_profile: CandidateProfile


class CandidateWorkflowResult(BaseModel):
    match: MatchResult
    evaluation: CandidateEvaluation
    skill_gap: SkillGapResult
    recommendations: RecommendationResult
