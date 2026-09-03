from app.schemas.recommendation import LearningRecommendation, RecommendationRequest, RecommendationResult


class LearningRecommendationService:
    """Produce focused learning paths from prioritized skill gaps."""

    PATHS = {
        "docker": ["Docker fundamentals", "Images and containers", "Docker Compose", "Dockerize a Python application"],
        "kubernetes": ["Kubernetes basics", "Pods and deployments", "Services and networking", "Deploy an application"],
        "aws": ["AWS cloud fundamentals", "IAM and security", "Compute and storage", "Deploy a backend service"],
        "python": ["Python fundamentals", "Functions and data structures", "Testing and packaging", "Build an API"],
        "sql": ["Relational database fundamentals", "Queries and joins", "Indexes and performance", "Design a database schema"],
        "fastapi": ["FastAPI fundamentals", "Request validation", "Database integration", "Deploy a production API"],
    }

    def generate(self, request: RecommendationRequest) -> RecommendationResult:
        recommendations = []
        for gap in request.skill_gap_result.gaps:
            path = self.PATHS.get(gap.skill.lower(), [f"Learn {gap.skill} fundamentals", f"Practice core {gap.skill} concepts", f"Build a small {gap.skill} project", "Document the project in your portfolio"])
            recommendations.append(LearningRecommendation(skill=gap.skill, priority=gap.priority, reason=gap.reason, learning_path=path))
        return RecommendationResult(recommendations=recommendations)
