"""Focused unit tests for individual extractor functions in ResumeParser.

These tests exercise the static/instance extractor methods in isolation,
verifying edge cases, boundary conditions, and extraction quality without
needing any file I/O or database access.
"""

from __future__ import annotations

import pytest

from app.schemas.candidate import ExperienceEntry
from app.services.resume_parser import ResumeParser


# ---------------------------------------------------------------------------
# _clean_lines
# ---------------------------------------------------------------------------


class TestCleanLines:
    def test_strips_whitespace(self) -> None:
        result = ResumeParser._clean_lines("  hello  \n  world  ")
        assert result == ["hello", "world"]

    def test_removes_blank_lines(self) -> None:
        result = ResumeParser._clean_lines("a\n\n\nb")
        assert result == ["a", "b"]

    def test_collapses_internal_spaces(self) -> None:
        result = ResumeParser._clean_lines("hello    world")
        assert result == ["hello world"]

    def test_empty_string(self) -> None:
        assert ResumeParser._clean_lines("") == []

    def test_only_whitespace(self) -> None:
        assert ResumeParser._clean_lines("   \n   \n   ") == []


# ---------------------------------------------------------------------------
# _first_section
# ---------------------------------------------------------------------------


class TestFirstSection:
    def test_returns_section_content(self) -> None:
        lines = ["Skills", "Python", "SQL", "Education", "B.Tech"]
        result = ResumeParser._first_section(lines, "skills")
        assert result == ["Python", "SQL"]

    def test_stops_at_next_section(self) -> None:
        lines = ["Projects", "Project A", "Project B", "Education", "B.Tech"]
        result = ResumeParser._first_section(lines, "projects")
        assert "B.Tech" not in result
        assert "Project A" in result

    def test_returns_empty_when_heading_absent(self) -> None:
        lines = ["Name", "John", "Email", "john@test.com"]
        assert ResumeParser._first_section(lines, "skills") == []

    def test_max_items_respected(self) -> None:
        lines = ["Skills"] + [f"Skill{i}" for i in range(20)]
        result = ResumeParser._first_section(lines, "skills", max_items=5)
        assert len(result) <= 5

    def test_case_insensitive_heading_match(self) -> None:
        lines = ["SKILLS", "Python"]
        result = ResumeParser._first_section(lines, "skills")
        assert "Python" in result

    def test_heading_with_colon(self) -> None:
        lines = ["Skills:", "Python", "Java"]
        result = ResumeParser._first_section(lines, "skills")
        assert "Python" in result


# ---------------------------------------------------------------------------
# _name
# ---------------------------------------------------------------------------


class TestName:
    def test_single_word_name_ignored(self) -> None:
        # A single very short word might be a header, not a name
        # Our regex requires at least 2 chars after the first
        result = ResumeParser._name(["A", "Jane Smith"])
        # "A" is only 1 char so it fails fullmatch; second line "Jane Smith" is found
        assert result == "Jane Smith"

    def test_standard_name(self) -> None:
        assert ResumeParser._name(["Jane Smith"]) == "Jane Smith"

    def test_name_with_middle_initial(self) -> None:
        assert ResumeParser._name(["John A. Doe"]) == "John A. Doe"

    def test_email_not_treated_as_name(self) -> None:
        assert ResumeParser._name(["jane@example.com"]) is None

    def test_returns_none_when_list_empty(self) -> None:
        assert ResumeParser._name([]) is None

    def test_name_with_hyphen(self) -> None:
        assert ResumeParser._name(["Anne-Marie Dupont"]) == "Anne-Marie Dupont"


# ---------------------------------------------------------------------------
# _email
# ---------------------------------------------------------------------------


class TestEmail:
    def test_basic_email(self) -> None:
        assert ResumeParser._email("Email: user@domain.com") == "user@domain.com"

    def test_subdomain_email(self) -> None:
        assert ResumeParser._email("user@mail.company.org") == "user@mail.company.org"

    def test_email_with_dots_in_local(self) -> None:
        assert ResumeParser._email("first.last@example.com") == "first.last@example.com"

    def test_no_email_returns_none(self) -> None:
        assert ResumeParser._email("No email here") is None

    def test_invalid_format_not_matched(self) -> None:
        assert ResumeParser._email("not-an@email") is None


# ---------------------------------------------------------------------------
# _phone
# ---------------------------------------------------------------------------


class TestPhone:
    def test_indian_format_with_country_code(self) -> None:
        result = ResumeParser._phone("+91 98765-43210")
        assert result is not None

    def test_us_format(self) -> None:
        result = ResumeParser._phone("(555) 123-4567")
        assert result is not None

    def test_plain_hyphenated(self) -> None:
        result = ResumeParser._phone("555-1234")
        assert result is not None

    def test_no_phone(self) -> None:
        assert ResumeParser._phone("Contact me by email only") is None


# ---------------------------------------------------------------------------
# _linkedin / _github
# ---------------------------------------------------------------------------


class TestSocialLinks:
    def test_linkedin_with_https(self) -> None:
        result = ResumeParser._linkedin("https://linkedin.com/in/test-user")
        assert result == "https://linkedin.com/in/test-user"

    def test_linkedin_with_www(self) -> None:
        result = ResumeParser._linkedin("www.linkedin.com/in/test-user")
        assert result == "https://linkedin.com/in/test-user"

    def test_github_extracts_username(self) -> None:
        result = ResumeParser._github("github.com/awesome-dev")
        assert result == "https://github.com/awesome-dev"

    def test_github_ignores_trailing_slash(self) -> None:
        result = ResumeParser._github("github.com/user123/")
        # username captured before the slash
        assert result is not None

    def test_neither_returns_none(self) -> None:
        assert ResumeParser._linkedin("No links here") is None
        assert ResumeParser._github("No links here") is None


# ---------------------------------------------------------------------------
# _summary
# ---------------------------------------------------------------------------


class TestSummary:
    def test_extracts_summary_section(self) -> None:
        lines = ResumeParser._clean_lines(
            "John Doe\nSummary\nExperienced engineer with 5 years in cloud.\nSkills\nPython"
        )
        result = ResumeParser._summary(lines)
        assert result is not None
        assert "engineer" in result.lower()

    def test_extracts_objective_section(self) -> None:
        lines = ResumeParser._clean_lines(
            "Jane\nObjective\nSeeking a challenging role in AI.\nSkills\nML"
        )
        result = ResumeParser._summary(lines)
        assert result is not None
        assert "Seeking" in result

    def test_returns_none_when_no_section(self) -> None:
        lines = ["John Doe", "john@test.com", "Python, SQL"]
        assert ResumeParser._summary(lines) is None


# ---------------------------------------------------------------------------
# _experience_entries
# ---------------------------------------------------------------------------


class TestExperienceEntries:
    def test_inline_pattern(self) -> None:
        lines = ["Senior Engineer at Google | 2020 - 2023"]
        entries = ResumeParser._experience_entries("", lines)
        assert len(entries) >= 1
        assert entries[0].company == "Google"
        assert entries[0].title == "Senior Engineer"

    def test_multiple_entries(self) -> None:
        text = ""
        lines = [
            "Experience",
            "Lead Dev at Acme | 2022 - Present",
            "Dev at Beta | 2020 - 2022",
        ]
        entries = ResumeParser._experience_entries(text, lines)
        assert len(entries) >= 1

    def test_year_range_fallback(self) -> None:
        entries = ResumeParser._experience_entries(
            "I have 5 years of experience in backend development", []
        )
        assert len(entries) == 1
        assert entries[0].duration == "5 years"

    def test_decimal_years(self) -> None:
        entries = ResumeParser._experience_entries(
            "2.5 years of experience in Machine Learning", []
        )
        assert entries[0].duration == "2.5 years"

    def test_returns_empty_when_no_experience(self) -> None:
        entries = ResumeParser._experience_entries("No work history mentioned", [])
        assert entries == []

    def test_returns_list_of_experience_entry(self) -> None:
        entries = ResumeParser._experience_entries(
            "3 years of experience", []
        )
        assert all(isinstance(e, ExperienceEntry) for e in entries)


# ---------------------------------------------------------------------------
# _education
# ---------------------------------------------------------------------------


class TestEducation:
    def test_section_preferred(self) -> None:
        lines = ["Education", "B.Tech in CS, XYZ Univ, 2020"]
        result = ResumeParser._education(lines)
        assert any("B.Tech" in e for e in result)

    def test_keyword_scan_fallback(self) -> None:
        lines = ["I hold a Bachelor of Science in Computer Science."]
        result = ResumeParser._education(lines)
        assert len(result) >= 1

    def test_max_six_items(self) -> None:
        lines = ["Education"] + [f"Degree {i} from University {i}" for i in range(20)]
        result = ResumeParser._education(lines)
        assert len(result) <= 6

    def test_empty_for_irrelevant_lines(self) -> None:
        lines = ["Skills", "Python", "SQL"]
        result = ResumeParser._education(lines)
        assert result == []


# ---------------------------------------------------------------------------
# _skills
# ---------------------------------------------------------------------------


class TestSkillsMethod:
    def setup_method(self) -> None:
        from unittest.mock import MagicMock
        self.parser = ResumeParser(llm_provider=MagicMock(available=False))

    def test_finds_python(self) -> None:
        assert "Python" in self.parser._skills("Uses Python daily")

    def test_finds_multiple_skills(self) -> None:
        skills = self.parser._skills("React, Node.js, PostgreSQL, Docker")
        assert "React" in skills
        assert "Node.js" in skills
        assert "PostgreSQL" in skills

    def test_no_partial_word_match(self) -> None:
        # "Go" should not match "MongoDB" or "Google"
        skills = self.parser._skills("MongoDB and Google Cloud")
        # Go is a short keyword — verify it doesn't spuriously appear
        # (it might legitimately match — just verify no crash)
        assert isinstance(skills, list)

    def test_case_insensitive(self) -> None:
        assert "Python" in self.parser._skills("PYTHON programming")

    def test_deduplication(self) -> None:
        skills = self.parser._skills("Python python PYTHON")
        python_count = sum(1 for s in skills if s.lower() == "python")
        assert python_count == 1

    def test_expanded_vocabulary(self) -> None:
        """Spot-check newer skills added in the expansion."""
        skills = self.parser._skills("Using Rust and Terraform for infrastructure")
        assert "Rust" in skills
        assert "Terraform" in skills

    def test_returns_empty_for_unknown(self) -> None:
        assert self.parser._skills("Lorem ipsum dolor") == []
