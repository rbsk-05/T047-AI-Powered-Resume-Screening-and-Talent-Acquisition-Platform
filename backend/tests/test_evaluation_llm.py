from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import EvaluationRequest
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest
from app.services.evaluation import EvaluationService


class _FakeLLM:
    def __init__(self, available: bool, summary: str | None):
        self.available = available
        self._summary = summary

    def generate_summary(self, **kwargs) -> str | None:
        return self._summary


REQUEST = EvaluationRequest(match_request=MatchRequest(
    job_profile=JobProfile(job_title="Backend Developer", required_skills=["Python", "AWS"], preferred_skills=["Docker"], experience="2 years", education=[], responsibilities=[]),
    candidate_profile=CandidateProfile(name="Candidate A", email=None, phone=None, skills=["Python"], experience="2 years", education=[], projects=[], certifications=[]),
))


def test_llm_unavailable_uses_templated_summary() -> None:
    service = EvaluationService(llm_provider=_FakeLLM(available=False, summary=None))

    result = service.evaluate(REQUEST)

    assert "Candidate A" in result.summary
    assert result.recommendation == "Review required skill gaps before progressing"


def test_llm_failure_falls_back_to_templated_summary() -> None:
    service = EvaluationService(llm_provider=_FakeLLM(available=True, summary=None))

    result = service.evaluate(REQUEST)

    assert "Candidate A" in result.summary


def test_valid_llm_summary_is_used_verbatim() -> None:
    service = EvaluationService(llm_provider=_FakeLLM(
        available=True,
        summary="Candidate A shows strong Python skills but has not demonstrated AWS experience.",
    ))

    result = service.evaluate(REQUEST)

    assert result.summary == "Candidate A shows strong Python skills but has not demonstrated AWS experience."
    # Deterministic fields must be unaffected by the LLM summary.
    assert result.recommendation == "Review required skill gaps before progressing"
    assert result.match.missing_required_skills == ["AWS"]
