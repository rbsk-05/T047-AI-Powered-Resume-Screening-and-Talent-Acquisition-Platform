from fastapi import APIRouter

from app.agents.skill_agent import SkillAgent
from app.schemas.gap import SkillGapRequest, SkillGapResult

router = APIRouter(prefix="/skill-gaps", tags=["skill gap analysis"])
agent = SkillAgent()


@router.post("/analyze", response_model=SkillGapResult)
def analyze_skill_gaps(payload: SkillGapRequest) -> SkillGapResult:
    """Find missing role skills and classify their priority."""
    return agent.process(payload.job_profile, payload.candidate_profile)
