from app.schemas.job import JobDescriptionAnalysisRequest
from app.services.job_analyzer import JobDescriptionAnalyzer


class _FakeJDLLM:
    def __init__(self, extraction: dict | None = None):
        self.available = True
        self._extraction = extraction or {
            "required_skills": ["Python", "FastAPI", "SQL", "AWS"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "experience": "3+ years",
            "education": ["Computer Science"],
            "responsibilities": ["Develop REST API services"],
        }

    def extract_job_requirements(self, job_title: str, job_description: str) -> dict | None:
        return self._extraction


def test_analyzer_extracts_core_job_requirements() -> None:
    profile = JobDescriptionAnalyzer(llm_provider=_FakeJDLLM()).analyze(
        JobDescriptionAnalysisRequest(
            job_title="Backend Developer",
            job_description=(
                "Develop REST API services using Python, FastAPI, SQL and AWS. "
                "Candidates need 3+ years of experience and a Computer Science degree. "
                "Docker and Kubernetes are preferred."
            ),
        )
    )

    assert {"Python", "SQL", "FastAPI", "AWS"}.issubset(set(profile.required_skills))
    assert set(profile.preferred_skills) == {"Docker", "Kubernetes"}
    assert profile.experience == "3+ years"
    assert profile.education == ["Computer Science"]


def test_analyzer_extracts_from_long_paragraph_jd() -> None:
    paragraph_jd = (
        "We are looking for an experienced DevOps Engineer to join our growing team. "
        "In this role, you will be architecting and managing our cloud infrastructure on Microsoft Azure, "
        "writing Infrastructure as Code using Terraform and Ansible, and setting up CI/CD pipelines with GitHub Actions. "
        "The ideal candidate must have deep hands-on expertise with Docker containers, Kubernetes cluster management, "
        "and Python scripting for system automation. Candidates should possess at least 4+ years of professional experience "
        "and a degree in Computer Science or a related engineering discipline. Experience with Prometheus and Grafana is a plus."
    )

    fake_llm = _FakeJDLLM(extraction={
        "job_title": "DevOps Engineer",
        "required_skills": ["Microsoft Azure", "Terraform", "Ansible", "CI/CD", "Docker", "Kubernetes", "Python"],
        "preferred_skills": ["Prometheus", "Grafana"],
        "experience": "4+ years",
        "education": ["Computer Science"],
        "responsibilities": ["Architecting and managing cloud infrastructure", "Writing Infrastructure as Code"],
    })

    profile = JobDescriptionAnalyzer(llm_provider=fake_llm).analyze(
        JobDescriptionAnalysisRequest(job_title="DevOps Engineer", job_description=paragraph_jd)
    )

    assert "Microsoft Azure" in profile.required_skills
    assert "Terraform" in profile.required_skills
    assert "Kubernetes" in profile.required_skills
    assert "Prometheus" in profile.preferred_skills
    assert profile.experience == "4+ years"



