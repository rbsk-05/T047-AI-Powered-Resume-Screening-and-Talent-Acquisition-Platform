from app.schemas.evaluation import CandidateEvaluation, EvaluationRequest
from app.schemas.match import MatchRequest
from app.services.evaluation import EvaluationService
from app.services.llm_provider import LLMProvider, get_llm_provider


class ExplanationAgent:
    """Agent 4: Specialized Explainability & Rationale Agent.
    
    Responsibilities:
    - Explains why the candidate received their specific ATS score.
    - Highlights candidate strengths, evidence, and missing requirements.
    - Explains side-by-side differentiators when comparing multiple candidates.
    - Never hallucinates facts not present in the extracted candidate profile.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()
        self.evaluator = EvaluationService(llm_provider=self.llm_provider)

    def explain_evaluation(self, match_request: MatchRequest) -> CandidateEvaluation:
        """Produce an explainable evaluation with strengths, gaps, and rationale."""
        return self.evaluator.evaluate(EvaluationRequest(match_request=match_request))

    def explain_comparison(self, job_title: str, candidates_data: list[dict]) -> str | None:
        """Generate a comparative summary explaining differentiators between candidates."""
        return self.llm_provider.generate_comparison_summary(job_title, candidates_data)
