from app.schemas.gap import SkillGapResult
from app.schemas.recommendation import RecommendationRequest, RecommendationResult
from app.services.recommendations import LearningRecommendationService


class RecommendationAgent:
    """Agent 5: Specialized Recommendation & Career Path Agent.
    
    Responsibilities:
    - Provides candidate improvement guidance based on missing skills.
    - Generates actionable, ordered learning milestones (1. Fundamentals -> 2. Concepts -> 3. Project).
    - Avoids fake courses, certifications, or URLs.
    """

    def __init__(self) -> None:
        self.service = LearningRecommendationService()

    def process(self, skill_gap_result: SkillGapResult) -> RecommendationResult:
        """Generate structured learning path recommendations from analyzed skill gaps."""
        return self.service.generate(RecommendationRequest(skill_gap_result=skill_gap_result))
