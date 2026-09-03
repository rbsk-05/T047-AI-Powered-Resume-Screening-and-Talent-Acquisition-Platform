from fastapi import APIRouter

from app.schemas.match import MatchRequest, MatchResult
from app.services.matching import CandidateMatcher

router = APIRouter(prefix="/matches", tags=["candidate matching"])
matcher = CandidateMatcher()


@router.post("/score", response_model=MatchResult)
def score_candidate(payload: MatchRequest) -> MatchResult:
    """Return a transparent ATS-style score for a candidate and job profile."""
    return matcher.score(payload)
