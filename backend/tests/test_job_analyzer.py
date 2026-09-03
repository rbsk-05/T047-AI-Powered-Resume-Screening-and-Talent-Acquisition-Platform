from app.schemas.job import JobDescriptionAnalysisRequest
from app.services.job_analyzer import JobDescriptionAnalyzer


def test_analyzer_extracts_core_job_requirements() -> None:
    profile = JobDescriptionAnalyzer().analyze(
        JobDescriptionAnalysisRequest(
            job_title="Backend Developer",
            job_description=(
                "Develop REST API services using Python, FastAPI, SQL and AWS. "
                "Candidates need 3+ years of experience and a Computer Science degree. "
                "Docker and Kubernetes are preferred."
            ),
        )
    )

    assert profile.required_skills == ["Python", "SQL", "FastAPI", "AWS", "REST API"]
    assert profile.preferred_skills == ["Docker", "Kubernetes"]
    assert profile.experience == "3+ years"
    assert profile.education == ["Computer Science"]
