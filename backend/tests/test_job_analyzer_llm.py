from app.schemas.job import JobDescriptionAnalysisRequest
from app.services.job_analyzer import JobDescriptionAnalyzer


class _FakeLLM:
    def __init__(self, available: bool, extraction: dict | None):
        self.available = available
        self._extraction = extraction

    def extract_job_requirements(self, job_title: str, job_description: str) -> dict | None:
        return self._extraction


REQUEST = JobDescriptionAnalysisRequest(
    job_title="Backend Developer",
    job_description=(
        "Develop REST API services using Python, FastAPI, SQL and AWS. "
        "Candidates need 3+ years of experience and a Computer Science degree. "
        "Docker and Kubernetes are preferred."
    ),
)


def test_llm_unavailable_returns_clean_baseline() -> None:
    analyzer = JobDescriptionAnalyzer(llm_provider=_FakeLLM(available=False, extraction=None))
    profile = analyzer.analyze(REQUEST)
    assert profile.job_title == "Backend Developer"
    assert profile.required_skills == []


def test_llm_failure_returns_clean_baseline() -> None:
    analyzer = JobDescriptionAnalyzer(llm_provider=_FakeLLM(available=True, extraction=None))
    profile = analyzer.analyze(REQUEST)
    assert profile.job_title == "Backend Developer"
    assert profile.required_skills == []


def test_valid_llm_extraction_is_used() -> None:
    analyzer = JobDescriptionAnalyzer(llm_provider=_FakeLLM(available=True, extraction={
        "required_skills": ["Python", "AWS"],
        "preferred_skills": ["Docker"],
        "experience": "3+ years",
        "education": ["Computer Science"],
        "responsibilities": ["Develop backend services"],
    }))

    profile = analyzer.analyze(REQUEST)

    assert profile.required_skills == ["Python", "AWS"]
    assert profile.preferred_skills == ["Docker"]
    assert profile.responsibilities == ["Develop backend services"]


def test_job_title_always_comes_from_the_request() -> None:
    analyzer = JobDescriptionAnalyzer(llm_provider=_FakeLLM(available=True, extraction={
        "required_skills": ["Python"], "preferred_skills": [], "experience": None,
        "education": [], "responsibilities": [],
    }))

    profile = analyzer.analyze(REQUEST)

    assert profile.job_title == "Backend Developer"

