from app.services.resume_parser import ResumeParser


def test_parser_extracts_profile_from_resume_text() -> None:
    profile = ResumeParser().parse_text(
        "Candidate A\ncandidate@example.com | +91 98765 43210\n"
        "Python, SQL, AWS, Docker\n3 years of experience\n"
        "Education\nB.E Computer Science\nProjects\nCloud E-commerce Application\n"
        "Certifications\nAWS Cloud Practitioner"
    )

    assert profile.email == "candidate@example.com"
    assert profile.skills == ["Python", "SQL", "AWS", "Docker"]
    assert profile.experience == "3 years"
    assert profile.projects == ["Cloud E-commerce Application"]
