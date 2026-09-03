from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import EvaluationRequest
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest
from app.services.evaluation import EvaluationService


def test_evaluation_explains_missing_required_skill() -> None:
    result = EvaluationService().evaluate(EvaluationRequest(match_request=MatchRequest(
        job_profile=JobProfile(job_title="Backend Developer", required_skills=["Python", "AWS"], preferred_skills=["Docker"], experience="2 years", education=[], responsibilities=[]),
        candidate_profile=CandidateProfile(name="Candidate A", email=None, phone=None, skills=["Python"], experience="2 years", education=[], projects=[], certifications=[]),
    )))

    assert result.recommendation == "Review required skill gaps before progressing"
    assert result.match.missing_required_skills == ["AWS"]
    assert result.evidence[1].status == "missing"
