from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest, RecommendationResult
from app.services.recommendations import LearningRecommendationService

router = APIRouter(prefix="/recommendations", tags=["skill recommendations"])
service = LearningRecommendationService()


@router.post("/generate", response_model=RecommendationResult)
def generate_recommendations(payload: RecommendationRequest) -> RecommendationResult:
    """Generate personalized learning paths from an analyzed skill gap."""
    return service.generate(payload)
