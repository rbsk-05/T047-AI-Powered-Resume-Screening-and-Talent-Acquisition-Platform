from fastapi import APIRouter

from app.agents.recommendation_agent import RecommendationAgent
from app.schemas.recommendation import RecommendationRequest, RecommendationResult

router = APIRouter(prefix="/recommendations", tags=["skill recommendations"])
agent = RecommendationAgent()


@router.post("/generate", response_model=RecommendationResult)
def generate_recommendations(payload: RecommendationRequest) -> RecommendationResult:
    """Generate personalized learning paths from an analyzed skill gap."""
    return agent.process(payload.skill_gap)
