from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest
from app.services.matching import CandidateMatcher


def test_matching_scores_qualified_candidate_and_identifies_gap() -> None:
    result = CandidateMatcher().score(MatchRequest(
        job_profile=JobProfile(
            job_title="Backend Developer", required_skills=["Python", "SQL", "AWS"],
            preferred_skills=["Docker"], experience="3+ years", education=["Computer Science"],
            responsibilities=["Develop REST API services."],
        ),
        candidate_profile=CandidateProfile(
            name="Candidate A", email=None, phone=None, skills=["Python", "SQL", "AWS"],
            experience="3 years", education=["B.E Computer Science"], projects=["Built Python REST API services"],
            certifications=["AWS Cloud Practitioner"],
        ),
    ))

    assert result.score_breakdown.required_skills == 100
    assert result.missing_preferred_skills == ["Docker"]
    assert result.overall_match_score > 80
