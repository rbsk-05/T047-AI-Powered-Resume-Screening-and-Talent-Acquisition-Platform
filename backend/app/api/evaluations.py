from fastapi import APIRouter

from app.schemas.evaluation import CandidateEvaluation, EvaluationRequest
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["explainable evaluation"])
service = EvaluationService()


@router.post("/explain", response_model=CandidateEvaluation)
def explain_candidate_evaluation(payload: EvaluationRequest) -> CandidateEvaluation:
    """Explain a candidate score with evidence, gaps, and a recommendation."""
    return service.evaluate(payload)
