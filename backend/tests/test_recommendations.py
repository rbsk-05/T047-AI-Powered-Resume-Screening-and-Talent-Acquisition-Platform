from app.schemas.gap import SkillGap, SkillGapResult
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendations import LearningRecommendationService


def test_docker_recommendation_has_learning_path() -> None:
    result = LearningRecommendationService().generate(RecommendationRequest(skill_gap_result=SkillGapResult(
        matched_skills=[], gaps=[SkillGap(skill="Docker", priority="critical", reason="Required skill missing")],
    )))
    assert result.recommendations[0].learning_path[-1] == "Dockerize a Python application"
