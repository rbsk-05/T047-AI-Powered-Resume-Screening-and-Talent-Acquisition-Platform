from app.schemas.evaluation import EvaluationRequest
from app.schemas.gap import SkillGapRequest
from app.schemas.match import MatchRequest
from app.schemas.recommendation import RecommendationRequest
from app.schemas.workflow import CandidateWorkflowRequest, CandidateWorkflowResult
from app.services.evaluation import EvaluationService
from app.services.matching import CandidateMatcher
from app.services.recommendations import LearningRecommendationService
from app.services.skill_gap import SkillGapAnalyzer


class CandidateAnalysisWorkflow:
    """Backend orchestration of independently testable candidate-analysis services."""

    def __init__(self) -> None:
        self.matcher = CandidateMatcher()
        self.evaluator = EvaluationService()
        self.gap_analyzer = SkillGapAnalyzer()
        self.recommender = LearningRecommendationService()

    def run(self, request: CandidateWorkflowRequest) -> CandidateWorkflowResult:
        match_request = MatchRequest(job_profile=request.job_profile, candidate_profile=request.candidate_profile)
        match = self.matcher.score(match_request)
        evaluation = self.evaluator.evaluate(EvaluationRequest(match_request=match_request))
        skill_gap = self.gap_analyzer.analyze(SkillGapRequest(job_profile=request.job_profile, candidate_profile=request.candidate_profile))
        recommendations = self.recommender.generate(RecommendationRequest(skill_gap_result=skill_gap))
        return CandidateWorkflowResult(match=match, evaluation=evaluation, skill_gap=skill_gap, recommendations=recommendations)
