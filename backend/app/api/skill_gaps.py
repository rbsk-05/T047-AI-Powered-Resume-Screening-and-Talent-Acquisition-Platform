from fastapi import APIRouter

from app.schemas.gap import SkillGapRequest, SkillGapResult
from app.services.skill_gap import SkillGapAnalyzer

router = APIRouter(prefix="/skill-gaps", tags=["skill gap analysis"])
analyzer = SkillGapAnalyzer()


@router.post("/analyze", response_model=SkillGapResult)
def analyze_skill_gaps(payload: SkillGapRequest) -> SkillGapResult:
    """Find missing role skills and classify their priority."""
    return analyzer.analyze(payload)
