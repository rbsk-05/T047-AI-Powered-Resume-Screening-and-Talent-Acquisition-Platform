from fastapi import APIRouter

from app.schemas.workflow import CandidateWorkflowRequest, CandidateWorkflowResult
from app.services.workflow import CandidateAnalysisWorkflow

router = APIRouter(prefix="/workflows", tags=["analysis orchestration"])
workflow = CandidateAnalysisWorkflow()


@router.post("/candidate-analysis", response_model=CandidateWorkflowResult)
def run_candidate_analysis(payload: CandidateWorkflowRequest) -> CandidateWorkflowResult:
    """Run matching, explanation, skill-gap, and recommendation services in order."""
    return workflow.run(payload)
