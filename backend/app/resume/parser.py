"""Resume parsing pipeline facade."""

import re
from typing import Any

from app.schemas.candidate import CandidateProfile, ExperienceEntry
from app.resume.adapter import CandidateProfileAdapter
from app.resume.agent.providers import BaseResumeProvider, GeminiProvider, FallbackProvider
from app.resume.agent.resume_agent import ResumeAnalysisAgent
from app.resume.regex_extractor import RegexExtractor
from app.resume.section_detector import SectionDetector
from app.resume.schemas import ResumeData
from app.resume.text_extractor import TextExtractor


class LegacyLLMAdapterProvider(BaseResumeProvider):
    """Adapter for legacy tests passing custom mock llm_provider."""

    def __init__(self, legacy_llm: Any) -> None:
        self.legacy_llm = legacy_llm
        self.fallback = FallbackProvider()

    def extract(self, resume_text: str, deterministic_context: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        if not getattr(self.legacy_llm, "available", False):
            return self.fallback.extract(resume_text, deterministic_context)
        extracted = self.legacy_llm.extract_candidate_profile(resume_text)
        if isinstance(extracted, dict):
            return extracted, "hybrid"
        return self.fallback.extract(resume_text, deterministic_context)


class ResumeParser:
    """Facade for the modular Resume Analysis pipeline."""

    ALLOWED_SUFFIXES: frozenset[str] = TextExtractor.ALLOWED_SUFFIXES
    SKILLS = RegexExtractor.SKILLS
    SECTION_TITLES = SectionDetector.SECTION_TITLES

    def __init__(self, provider: BaseResumeProvider | None = None, llm_provider: Any = None) -> None:
        if provider is not None:
            self.provider = provider
        elif isinstance(llm_provider, BaseResumeProvider):
            self.provider = llm_provider
        elif llm_provider is not None:
            self.provider = LegacyLLMAdapterProvider(llm_provider)
        else:
            self.provider = GeminiProvider()
        self.agent = ResumeAnalysisAgent(provider=self.provider)

    def extract_text(self, filename: str, content: bytes) -> str:
        """Validate file and extract raw plain text."""
        return TextExtractor.extract_text(filename, content)

    def validate_resume_structure(self, text: str) -> bool:
        """Check if document structure resembles a resume."""
        has_contact = bool(self._email(text) or self._phone(text))
        has_skills = bool(self._skills(text))
        return SectionDetector.validate_resume_structure(text, has_contact=has_contact, has_skills=has_skills)

    def parse_text_to_resume_data(self, text: str) -> ResumeData:
        """Parse raw text into internal rich ResumeData."""
        if not self.validate_resume_structure(text):
            raise ValueError(
                "The uploaded document does not appear to be a valid resume. "
                "Please ensure your file contains standard resume sections "
                "such as Skills, Experience, Education, or Projects."
            )
        return self.agent.analyze(text)

    def parse_text(self, text: str) -> CandidateProfile:
        """Parse raw text into public CandidateProfile expected by AI Core."""
        resume_data = self.parse_text_to_resume_data(text)
        return CandidateProfileAdapter.to_candidate_profile(resume_data)

    def parse(self, filename: str, content: bytes) -> CandidateProfile:
        """End-to-end convenience method: bytes -> CandidateProfile."""
        text = self.extract_text(filename, content)
        return self.parse_text(text)

    # ---------------------------------------------------------------------------
    # Static method delegators for legacy unit tests compatibility
    # ---------------------------------------------------------------------------

    @staticmethod
    def _clean_lines(text: str) -> list[str]:
        return SectionDetector.clean_lines(text)

    @staticmethod
    def _first_section(lines: list[str], heading: str, max_items: int = 8) -> list[str]:
        return SectionDetector.extract_section_lines(lines, (heading,), max_items=max_items)

    @staticmethod
    def _name(lines: list[str]) -> str | None:
        return RegexExtractor.extract_name(lines)

    @staticmethod
    def _email(text: str) -> str | None:
        return RegexExtractor.extract_email(text)

    @staticmethod
    def _phone(text: str) -> str | None:
        return RegexExtractor.extract_phone(text)

    @staticmethod
    def _linkedin(text: str) -> str | None:
        return RegexExtractor.extract_linkedin(text)

    @staticmethod
    def _github(text: str) -> str | None:
        return RegexExtractor.extract_github(text)

    @staticmethod
    def _summary(lines: list[str]) -> str | None:
        return RegexExtractor.extract_summary(lines)

    def _skills(self, text: str) -> list[str]:
        return RegexExtractor.extract_skills(text)

    @staticmethod
    def _education(lines: list[str]) -> list[str]:
        return RegexExtractor.extract_education_lines(lines)

    @staticmethod
    def _experience_entries(text: str, lines: list[str]) -> list[ExperienceEntry]:
        section_lines = (
            SectionDetector.extract_section_lines(lines, ("experience", "work experience", "professional experience", "employment history"), max_items=30)
        )
        entries: list[ExperienceEntry] = []
        inline_re = re.compile(r"^(.+?)\s+(?:at|@|,)\s+(.+?)\s*[|–\-]\s*(.+)$", re.IGNORECASE)
        date_re = re.compile(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(?:\d{4}|Present|Current|Now)",
            re.IGNORECASE,
        )
        year_range_re = re.compile(r"\b\d{4}\s*[-–]\s*(?:\d{4}|Present|Current|Now)\b", re.IGNORECASE)

        if section_lines:
            i = 0
            while i < len(section_lines):
                line = section_lines[i]
                m = inline_re.match(line)
                if m:
                    entries.append(ExperienceEntry(title=m.group(1).strip(), company=m.group(2).strip(), duration=m.group(3).strip()))
                    i += 1
                    continue
                if i + 1 < len(section_lines):
                    next_line = section_lines[i + 1]
                    if date_re.search(next_line) or year_range_re.search(next_line):
                        entries.append(ExperienceEntry(company=line, duration=next_line))
                        i += 2
                        continue
                if date_re.search(line) or year_range_re.search(line):
                    if entries and entries[-1].duration is None:
                        entries[-1] = entries[-1].model_copy(update={"duration": line})
                    i += 1
                    continue
                i += 1
        if not entries:
            years_m = re.search(r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", text, re.IGNORECASE)
            if years_m:
                entries.append(ExperienceEntry(duration=f"{years_m.group(1)} years"))
        return entries
