"""Tests for the resume parsing pipeline.

Covers:
- Individual field extractors (name, email, phone, linkedin, github,
  summary, skills, education, experience entries)
- validate_resume_structure
- parse_text (happy-path, invalid document, partial extraction)
- extract_text for PDF and DOCX (using in-memory fixtures)
- Error paths: unsupported extension, corrupted bytes, empty file
- LLM merge logic (mocked provider)
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest
from docx import Document

from app.schemas.candidate import CandidateProfile, ExperienceEntry
from app.services.resume_parser import ResumeParser

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FULL_RESUME_TEXT = """\
Jane Smith
jane.smith@example.com | +91 98765 43210
linkedin.com/in/janesmith | github.com/janesmith

Summary
Experienced software engineer with 4 years building scalable cloud services.

Skills
Python, FastAPI, AWS, Docker, PostgreSQL, React, Git

Experience
Software Engineer at TechCorp | Jan 2021 - Dec 2023
Built REST APIs using FastAPI and deployed on AWS ECS.

Junior Developer at StartupXYZ | Jun 2019 - Dec 2020
Maintained Django-based web applications.

Education
B.Tech Computer Science, XYZ University, 2019

Projects
Cloud E-commerce Platform
AI-powered Resume Screener

Certifications
AWS Certified Cloud Practitioner
"""

MINIMAL_RESUME_TEXT = """\
Alex Dev
alex@test.com
Skills
Python, SQL
"""


@pytest.fixture()
def parser() -> ResumeParser:
    return ResumeParser(llm_provider=MagicMock(available=False))


@pytest.fixture()
def sample_docx_bytes() -> bytes:
    doc = Document()
    doc.add_paragraph("John Doe")
    doc.add_paragraph("john@example.com | +91 98765 43210")
    doc.add_paragraph("linkedin.com/in/johndoe | github.com/johndoe")
    doc.add_paragraph("")
    doc.add_paragraph("Skills")
    doc.add_paragraph("Python, FastAPI, AWS, Docker, PostgreSQL")
    doc.add_paragraph("")
    doc.add_paragraph("Experience")
    doc.add_paragraph("Software Engineer at TechCorp | Jan 2021 - Dec 2023")
    doc.add_paragraph("")
    doc.add_paragraph("Education")
    doc.add_paragraph("B.Tech Computer Science, ABC University, 2021")
    doc.add_paragraph("")
    doc.add_paragraph("Projects")
    doc.add_paragraph("Cloud E-commerce Platform")
    doc.add_paragraph("")
    doc.add_paragraph("Certifications")
    doc.add_paragraph("AWS Cloud Practitioner")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Field extractor unit tests
# ---------------------------------------------------------------------------


class TestNameExtractor:
    def test_extracts_standard_name(self) -> None:
        assert ResumeParser._name(["Jane Smith", "jane@test.com"]) == "Jane Smith"

    def test_skips_non_name_first_line(self) -> None:
        # Email on line 0 fails the name regex; _name scans the first 3 lines
        # so "Jane Smith" on line 1 IS returned — that is the correct behaviour.
        result = ResumeParser._name(["jane@test.com", "Jane Smith"])
        assert result == "Jane Smith"

    def test_returns_none_for_empty_lines(self) -> None:
        assert ResumeParser._name([]) is None

    def test_handles_unicode_names(self) -> None:
        assert ResumeParser._name(["Rámon García"]) == "Rámon García"

    def test_rejects_too_long_string(self) -> None:
        long_str = "A" * 100
        assert ResumeParser._name([long_str]) is None


class TestEmailExtractor:
    def test_standard_email(self) -> None:
        assert ResumeParser._email("Contact: user@example.com") == "user@example.com"

    def test_email_with_plus_alias(self) -> None:
        assert ResumeParser._email("user+filter@gmail.com") == "user+filter@gmail.com"

    def test_returns_none_when_absent(self) -> None:
        assert ResumeParser._email("No email here") is None

    def test_only_returns_first_email(self) -> None:
        result = ResumeParser._email("a@a.com and b@b.com")
        assert result == "a@a.com"


class TestPhoneExtractor:
    def test_indian_mobile(self) -> None:
        result = ResumeParser._phone("+91 98765 43210")
        assert result is not None
        assert "98765" in result

    def test_plain_number(self) -> None:
        result = ResumeParser._phone("555-1234")
        assert result is not None

    def test_returns_none_when_absent(self) -> None:
        assert ResumeParser._phone("No phone here at all") is None


class TestLinkedInExtractor:
    def test_full_url(self) -> None:
        result = ResumeParser._linkedin("https://www.linkedin.com/in/janesmith")
        assert result == "https://linkedin.com/in/janesmith"

    def test_bare_domain(self) -> None:
        result = ResumeParser._linkedin("linkedin.com/in/john-doe")
        assert result == "https://linkedin.com/in/john-doe"

    def test_returns_none_when_absent(self) -> None:
        assert ResumeParser._linkedin("No social links here") is None


class TestGitHubExtractor:
    def test_full_url(self) -> None:
        result = ResumeParser._github("https://github.com/janecoder")
        assert result == "https://github.com/janecoder"

    def test_bare_domain(self) -> None:
        result = ResumeParser._github("github.com/john-dev")
        assert result == "https://github.com/john-dev"

    def test_returns_none_when_absent(self) -> None:
        assert ResumeParser._github("No github link") is None


class TestSkillsExtractor:
    def test_extracts_known_skills(self, parser: ResumeParser) -> None:
        skills = parser._skills("I use Python, FastAPI, AWS, and Docker daily.")
        assert "Python" in skills
        assert "FastAPI" in skills
        assert "AWS" in skills
        assert "Docker" in skills

    def test_deduplicates_skills(self, parser: ResumeParser) -> None:
        skills = parser._skills("Python python PYTHON")
        assert skills.count("Python") == 1

    def test_does_not_partial_match(self, parser: ResumeParser) -> None:
        # "SQL" should not match inside "NoSQL"
        skills = parser._skills("Uses NoSQL databases")
        assert "SQL" not in skills

    def test_returns_empty_for_unknown_text(self, parser: ResumeParser) -> None:
        skills = parser._skills("Lorem ipsum dolor sit amet")
        assert skills == []


class TestExperienceExtractor:
    def test_inline_pattern(self) -> None:
        # _experience_entries first looks for a section heading; pass the
        # heading so the inline line falls inside the detected section.
        lines = [
            "Experience",
            "Software Engineer at Google | Jan 2021 - Dec 2023",
        ]
        entries = ResumeParser._experience_entries("", lines)
        assert len(entries) >= 1
        assert any(e.company == "Google" for e in entries)

    def test_fallback_years(self) -> None:
        entries = ResumeParser._experience_entries(
            "3 years of experience in software development", []
        )
        assert len(entries) == 1
        assert entries[0].duration == "3 years"

    def test_returns_empty_list_when_nothing_found(self) -> None:
        entries = ResumeParser._experience_entries("No experience here", [])
        assert entries == []

    def test_multiple_inline_entries(self) -> None:
        lines = [
            "Experience",
            "Senior Dev at Acme | 2022 - Present",
            "Junior Dev at Beta Corp | 2020 - 2022",
        ]
        entries = ResumeParser._experience_entries("", lines)
        assert len(entries) >= 1


class TestEducationExtractor:
    def test_extracts_from_section(self) -> None:
        lines = ["Education", "B.Tech Computer Science, XYZ Univ, 2020"]
        result = ResumeParser._education(lines)
        assert any("B.Tech" in e for e in result)

    def test_keyword_fallback(self) -> None:
        lines = ["My B.E in Computer Science from ABC College"]
        result = ResumeParser._education(lines)
        assert len(result) >= 1


# ---------------------------------------------------------------------------
# validate_resume_structure
# ---------------------------------------------------------------------------


class TestValidateResumeStructure:
    def test_valid_full_resume(self, parser: ResumeParser) -> None:
        assert parser.validate_resume_structure(FULL_RESUME_TEXT) is True

    def test_too_short(self, parser: ResumeParser) -> None:
        assert parser.validate_resume_structure("Hi") is False

    def test_empty_string(self, parser: ResumeParser) -> None:
        assert parser.validate_resume_structure("") is False

    def test_random_text(self, parser: ResumeParser) -> None:
        assert parser.validate_resume_structure(
            "The quick brown fox jumps over the lazy dog. " * 5
        ) is False

    def test_contact_plus_one_section(self, parser: ResumeParser) -> None:
        text = "Jane jane@test.com\nSkills\nPython, SQL\n" * 3
        assert parser.validate_resume_structure(text) is True


# ---------------------------------------------------------------------------
# parse_text
# ---------------------------------------------------------------------------


class TestParseText:
    def test_full_parse_happy_path(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert isinstance(profile, CandidateProfile)
        assert profile.email == "jane.smith@example.com"
        assert "Python" in profile.skills
        assert profile.linkedin == "https://linkedin.com/in/janesmith"
        assert profile.github == "https://github.com/janesmith"

    def test_experience_is_list(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert isinstance(profile.experience, list)
        # At least one entry should be found
        assert len(profile.experience) >= 1
        for entry in profile.experience:
            assert isinstance(entry, ExperienceEntry)

    def test_education_extracted(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert len(profile.education) >= 1

    def test_projects_extracted(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert "Cloud E-commerce Platform" in profile.projects

    def test_certifications_extracted(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert any("AWS" in c for c in profile.certifications)

    def test_invalid_document_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError, match="does not appear to be a valid resume"):
            parser.parse_text("Hello world, this is not a resume at all.")

    def test_empty_text_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError):
            parser.parse_text("")

    def test_candidate_id_defaults_to_none(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        assert profile.candidate_id is None

    def test_skills_deduplicated(self, parser: ResumeParser) -> None:
        profile = parser.parse_text(FULL_RESUME_TEXT)
        lower_skills = [s.lower() for s in profile.skills]
        assert len(lower_skills) == len(set(lower_skills))

    def test_partial_resume_does_not_crash(self, parser: ResumeParser) -> None:
        """A resume with contact info + skills section passes validation."""
        text = (
            "Alex Dev\nalex@test.com | +91 99999 88888\n"
            "Skills\nPython, SQL, Docker\n"
            "Education\nB.Tech Computer Science\n"
        )
        profile = parser.parse_text(text)
        assert isinstance(profile, CandidateProfile)
        assert profile.email == "alex@test.com"
        assert "Python" in profile.skills


# ---------------------------------------------------------------------------
# extract_text (file I/O layer)
# ---------------------------------------------------------------------------


class TestExtractText:
    def test_unsupported_extension_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            parser.extract_text("resume.txt", b"some content")

    def test_empty_content_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError, match="empty"):
            parser.extract_text("resume.pdf", b"")

    def test_no_extension_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            parser.extract_text("resumenoext", b"data")

    def test_corrupted_pdf_raises(self, parser: ResumeParser) -> None:
        with pytest.raises(ValueError, match="corrupted or unreadable"):
            parser.extract_text("resume.pdf", b"this is not a pdf at all!!")

    def test_docx_extraction(
        self, parser: ResumeParser, sample_docx_bytes: bytes
    ) -> None:
        text = parser.extract_text("resume.docx", sample_docx_bytes)
        assert "John Doe" in text
        assert "john@example.com" in text
        assert "Python" in text

    def test_docx_parse_round_trip(
        self, parser: ResumeParser, sample_docx_bytes: bytes
    ) -> None:
        profile = parser.parse("resume.docx", sample_docx_bytes)
        assert profile.email == "john@example.com"
        assert "Python" in profile.skills
        assert isinstance(profile.experience, list)


# ---------------------------------------------------------------------------
# LLM merge
# ---------------------------------------------------------------------------


class TestLLMMerge:
    def _make_parser_with_llm(self, llm_response: dict | None) -> ResumeParser:
        mock_llm = MagicMock()
        mock_llm.available = True
        mock_llm.extract_candidate_profile.return_value = llm_response
        return ResumeParser(llm_provider=mock_llm)

    def test_llm_skills_merged_with_baseline(self) -> None:
        p = self._make_parser_with_llm(
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": None,
                "linkedin": None,
                "github": None,
                "summary": None,
                "skills": ["Kubernetes", "Terraform"],
                "experience": [],
                "education": [],
                "projects": [],
                "certifications": [],
            }
        )
        profile = p.parse_text(FULL_RESUME_TEXT)
        # LLM-only skill should be present
        assert "Kubernetes" in profile.skills or "Terraform" in profile.skills
        # Baseline skills should also survive
        assert "Python" in profile.skills

    def test_llm_structured_experience_preferred(self) -> None:
        p = self._make_parser_with_llm(
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": None,
                "linkedin": None,
                "github": None,
                "summary": None,
                "skills": [],
                "experience": [
                    {
                        "company": "Acme Corp",
                        "title": "Senior Engineer",
                        "duration": "2020-2023",
                        "description": "Led backend team",
                    }
                ],
                "education": [],
                "projects": [],
                "certifications": [],
            }
        )
        profile = p.parse_text(FULL_RESUME_TEXT)
        assert len(profile.experience) >= 1
        assert any(e.company == "Acme Corp" for e in profile.experience)

    def test_llm_failure_returns_baseline(self) -> None:
        p = self._make_parser_with_llm(None)
        profile = p.parse_text(FULL_RESUME_TEXT)
        assert isinstance(profile, CandidateProfile)
        assert profile.email == "jane.smith@example.com"

    def test_llm_malformed_experience_falls_back(self) -> None:
        """If LLM returns experience as a string instead of list, baseline is kept."""
        p = self._make_parser_with_llm(
            {
                "name": None,
                "email": None,
                "phone": None,
                "linkedin": None,
                "github": None,
                "summary": None,
                "skills": [],
                "experience": "3 years",  # wrong type — should be list
                "education": [],
                "projects": [],
                "certifications": [],
            }
        )
        profile = p.parse_text(FULL_RESUME_TEXT)
        assert isinstance(profile.experience, list)
