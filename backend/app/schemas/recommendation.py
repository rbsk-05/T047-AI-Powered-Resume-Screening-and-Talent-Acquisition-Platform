from pydantic import BaseModel

from app.schemas.gap import SkillGapResult


class RecommendationRequest(BaseModel):
    skill_gap_result: SkillGapResult


class LearningRecommendation(BaseModel):
    skill: str
    priority: str
    reason: str
    learning_path: list[str]


class RecommendationResult(BaseModel):
    recommendations: list[LearningRecommendation]
