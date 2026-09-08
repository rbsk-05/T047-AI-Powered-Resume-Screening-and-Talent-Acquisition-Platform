"""Unit and component tests for the modular Resume Analysis system."""

import pytest
from unittest.mock import MagicMock

from app.resume import (
    CandidateProfileAdapter,
    FallbackProvider,
    GeminiProvider,
    ResumeAnalysisAgent,
    ResumeData,
    ResumeParser,
)
from app.resume.experience import ExperienceCalculator
from app.resume.normalizer import Normalizer
from app.resume.schemas import WorkExperience
from app.schemas.candidate import CandidateProfile


class TestSkillNormalizer:
    def test_skill_aliases(self) -> None:
        assert Normalizer.normalize_skill("NodeJS") == "Node.js"
        assert Normalizer.normalize_skill("ExpressJS") == "Express.js"
        assert Normalizer.normalize_skill("ReactNative") == "React Native"
        assert Normalizer.normalize_skill("ReactJs") == "React.js"
        assert Normalizer.normalize_skill("Github") == "GitHub"
        assert Normalizer.normalize_skill("VanillaJS") == "Vanilla JS"

    def test_normalize_skills_deduplication(self) -> None:
        raw_skills = ["Python", "python", "NodeJS", "Node.js", "ReactJs", "React.js", "GitHub", "Github"]
        normalized = Normalizer.normalize_skills(raw_skills)
        assert normalized == ["Python", "Node.js", "React.js", "GitHub"]


class TestExperienceCalculator:
    def test_single_date_range(self) -> None:
        exp = [WorkExperience(company="Devs", start_date="2024-08", end_date="2025-09")]
        years = ExperienceCalculator.calculate_total_experience_years(exp)
        assert 1.0 <= years <= 1.2

    def test_overlapping_date_ranges_merged(self) -> None:
        # IDP IELTS (MAR 2026 - OCT 2026) and PwC (FEB 2026 - JUL 2026) overlap
        exp = [
            WorkExperience(company="IDP IELTS", duration_text="MAR 2026 - OCT 2026"),
            WorkExperience(company="PwC", duration_text="FEB 2026 - JUL 2026"),
        ]
        years = ExperienceCalculator.calculate_total_experience_years(exp)
        # Feb 2026 to Oct 2026 = 9 months = 0.8 years
        assert 0.7 <= years <= 0.9

    def test_present_job_calculation(self) -> None:
        exp = [WorkExperience(company="Tech Corp", start_date="2024-01", end_date="Present")]
        years = ExperienceCalculator.calculate_total_experience_years(exp)
        assert years >= 2.0


class TestCandidateProfileAdapter:
    def test_adapter_conversion(self) -> None:
        data = ResumeData(
            name="Darshan M",
            email="mdarshan0505@gmail.com",
            phone="+919361465734",
            linkedin="https://linkedin.com/in/darshan",
            github="https://github.com/darshan",
            skills=["Python", "Node.js", "React.js"],
            work_experience=[
                WorkExperience(company="IDP IELTS", role="Project Intern", duration_text="MAR 2026 - OCT 2026")
            ],
            total_experience_years=1.8,
            education=[],
            projects=[],
            certifications=["AWS Practitioner"],
            analysis_method="hybrid",
        )
        profile = CandidateProfileAdapter.to_candidate_profile(data)
        assert isinstance(profile, CandidateProfile)
        assert profile.name == "Darshan M"
        assert profile.email == "mdarshan0505@gmail.com"
        assert profile.experience == "1.8 years"
        assert len(profile.experience_entries) == 1
        assert profile.experience_entries[0].company == "IDP IELTS"


class TestGeminiProviderAndFallback:
    def test_fallback_provider_when_no_api_key(self) -> None:
        provider = GeminiProvider(api_key="")
        res, method = provider.extract("Sample text", {"name": "Test User", "skills": ["Python"]})
        assert method == "deterministic_fallback"
        assert res["name"] == "Test User"

    def test_mocked_gemini_provider_success(self) -> None:
        mock_provider = MagicMock()
        mock_provider.extract.return_value = (
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+919876543210",
                "skills": ["Python", "FastAPI"],
                "work_experience": [{"company": "Tech Corp", "role": "Engineer", "duration_text": "2023-2025"}],
            },
            "hybrid",
        )
        agent = ResumeAnalysisAgent(provider=mock_provider)
        resume_data = agent.analyze("Jane Doe \n jane@example.com \n Skills: Python")
        assert resume_data.name == "Jane Doe"
        assert resume_data.analysis_method == "hybrid"
        assert "FastAPI" in resume_data.skills
