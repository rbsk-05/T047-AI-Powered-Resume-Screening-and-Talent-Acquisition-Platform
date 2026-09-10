from fastapi import APIRouter

from app.agents.orchestrator import MultiAgentOrchestrator
from app.schemas.workflow import CandidateWorkflowRequest, CandidateWorkflowResult

router = APIRouter(prefix="/workflows", tags=["analysis orchestration"])
orchestrator = MultiAgentOrchestrator()


@router.post("/candidate-analysis", response_model=CandidateWorkflowResult)
def run_candidate_analysis(payload: CandidateWorkflowRequest) -> CandidateWorkflowResult:
    """Run matching, explanation, skill-gap, and recommendation agents in multi-agent pipeline."""
    return orchestrator.run_candidate_pipeline(payload)
