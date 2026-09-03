from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile
from app.schemas.ranking import RankingRequest
from app.services.ranking import RankingService


def candidate(name: str, skills: list[str]) -> CandidateProfile:
    return CandidateProfile(name=name, email=None, phone=None, skills=skills, experience="3 years", education=[], projects=[], certifications=[])


def test_ranking_orders_candidates_by_match_score() -> None:
    result = RankingService().rank(RankingRequest(
        job_profile=JobProfile(job_title="Backend Developer", required_skills=["Python", "SQL", "AWS"], preferred_skills=[], experience=None, education=[], responsibilities=[]),
        candidates=[candidate("Candidate B", ["Python"]), candidate("Candidate A", ["Python", "SQL", "AWS"])],
    ))
    assert result.ranked_candidates[0].candidate_name == "Candidate A"
    assert result.ranked_candidates[0].rank == 1
