from fastapi import APIRouter

from app.schemas.ranking import ComparisonResult, RankingRequest, RankingResult
from app.services.ranking import RankingService

router = APIRouter(prefix="/rankings", tags=["candidate ranking"])
service = RankingService()


@router.post("/rank", response_model=RankingResult)
def rank_candidates(payload: RankingRequest) -> RankingResult:
    """Rank candidates for one job from highest to lowest transparent match score."""
    return service.rank(payload)


@router.post("/compare", response_model=ComparisonResult)
def compare_candidates(payload: RankingRequest) -> ComparisonResult:
    """Compare candidate strengths and gaps against the same job profile."""
    return service.compare(payload)
