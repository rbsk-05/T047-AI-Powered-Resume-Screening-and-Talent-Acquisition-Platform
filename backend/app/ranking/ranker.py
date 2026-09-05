from app.schemas.match import MatchRequest
from app.schemas.ranking import CandidateComparison, ComparisonResult, RankedCandidate, RankingRequest, RankingResult
from app.matching.matcher import CandidateMatcher


class RankingService:
    """Rank and compare candidate profiles using the shared transparent scoring model."""

    def __init__(self, matcher: CandidateMatcher | None = None) -> None:
        self.matcher = matcher or CandidateMatcher()

    def _scored_candidates(self, request: RankingRequest):
        scored = []
        for index, candidate in enumerate(request.candidates, start=1):
            name = candidate.name or f"Candidate {index}"
            match = self.matcher.score(MatchRequest(job_profile=request.job_profile, candidate_profile=candidate))
            scored.append((name, match))
        return sorted(scored, key=lambda item: item[1].overall_match_score, reverse=True)

    def rank(self, request: RankingRequest) -> RankingResult:
        return RankingResult(ranked_candidates=[
            RankedCandidate(rank=index, candidate_name=name, match=match)
            for index, (name, match) in enumerate(self._scored_candidates(request), start=1)
        ])

    def compare(self, request: RankingRequest) -> ComparisonResult:
        return ComparisonResult(candidates=[
            CandidateComparison(
                candidate_name=name,
                overall_match_score=match.overall_match_score,
                matched_skills=match.matched_skills,
                missing_required_skills=match.missing_required_skills,
                missing_preferred_skills=match.missing_preferred_skills,
            )
            for name, match in self._scored_candidates(request)
        ])
