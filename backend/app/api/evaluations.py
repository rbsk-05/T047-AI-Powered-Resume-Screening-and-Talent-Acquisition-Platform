from fastapi import APIRouter

from app.agents.explanation_agent import ExplanationAgent
from app.schemas.evaluation import CandidateEvaluation, EvaluationRequest

router = APIRouter(prefix="/evaluations", tags=["explainable evaluation"])
agent = ExplanationAgent()


@router.post("/explain", response_model=CandidateEvaluation)
def explain_candidate_evaluation(payload: EvaluationRequest) -> CandidateEvaluation:
    """Explain a candidate score with evidence, gaps, and a recommendation."""
    return agent.explain_evaluation(payload.match_request)
