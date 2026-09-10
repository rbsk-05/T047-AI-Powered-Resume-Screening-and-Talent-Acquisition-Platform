from app.services.resume_parser import ResumeParser


class _FakeResumeLLM:
    def __init__(self, extraction: dict | None = None):
        self.available = True
        self._extraction = extraction or {
            "name": "Candidate A",
            "role": "Cloud Developer",
            "email": "candidate@example.com",
            "phone": "+91 98765 43210",
            "skills": ["Python", "SQL", "AWS", "Docker"],
            "experience": "3 years",
            "education": ["B.E Computer Science"],
            "projects": ["Cloud E-commerce Application"],
            "certifications": ["AWS Cloud Practitioner"],
        }

    def extract_candidate_profile(self, text: str) -> dict | None:
        return self._extraction


def test_parser_extracts_profile_from_resume_text() -> None:
    profile = ResumeParser(llm_provider=_FakeResumeLLM()).parse_text(
        "Candidate A\ncandidate@example.com | +91 98765 43210\n"
        "Python, SQL, AWS, Docker\n3 years of experience\n"
        "Education\nB.E Computer Science\nProjects\nCloud E-commerce Application\n"
        "Certifications\nAWS Cloud Practitioner"
    )

    assert profile.name == "Candidate A"
    assert profile.role == "Cloud Developer"
    assert profile.email == "candidate@example.com"
    assert profile.skills == ["Python", "SQL", "AWS", "Docker"]
    assert profile.experience == "3 years"
    assert profile.projects == ["Cloud E-commerce Application"]
