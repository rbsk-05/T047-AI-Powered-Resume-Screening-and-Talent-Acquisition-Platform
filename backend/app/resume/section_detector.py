"""Section detector and boundary isolation helper."""

import re

# Standard section heading vocabulary
_SECTION_TITLES: frozenset[str] = frozenset({
    "skills", "technical skills", "core competencies", "areas of expertise",
    "tech stack", "tools", "technologies", "technical proficiencies",
    "experience", "work experience", "professional experience",
    "employment history", "career history", "work history",
    "education", "academic background", "qualifications",
    "academic history", "degrees",
    "projects", "project experience", "key projects",
    "academic projects", "personal projects", "technical projects",
    "certifications", "certificates", "licenses",
    "achievements", "awards",
    "summary", "professional summary", "profile", "objective",
    "about me", "about",
    "languages", "interests", "hobbies", "references",
    "volunteering", "volunteer experience", "social service",
})

# Patterns that indicate a standard resume section heading
_RESUME_SECTION_PATTERNS: tuple[str, ...] = (
    r"\b(?:skills|technical skills|technologies|core competencies|areas of expertise|tech stack|tools)\b",
    r"\b(?:experience|work experience|employment history|professional experience|career history|work history)\b",
    r"\b(?:education|academic background|qualifications|academic history|degrees|university|college|school)\b",
    r"\b(?:projects|key projects|academic projects|personal projects|technical projects)\b",
    r"\b(?:certifications|certificates|licenses|achievements|awards|summary|professional summary|profile|objective)\b",
)


class SectionDetector:
    """Detect section headings and extract isolated section text blocks."""

    SECTION_TITLES = _SECTION_TITLES

    @staticmethod
    def clean_lines(text: str) -> list[str]:
        """Return non-empty, whitespace-normalised lines."""
        return [
            re.sub(r"\s+", " ", line).strip()
            for line in text.splitlines()
            if line.strip()
        ]

    @classmethod
    def validate_resume_structure(cls, text: str, has_contact: bool = False, has_skills: bool = False) -> bool:
        """Sanity check if text looks like a valid resume."""
        if not text or len(text.strip()) < 80:
            return False

        section_hits = sum(
            1
            for pattern in _RESUME_SECTION_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)
        )
        return (section_hits >= 2) or (has_contact and (section_hits >= 1 or has_skills))

    @classmethod
    def extract_section_lines(
        cls, lines: list[str], target_headings: tuple[str, ...], max_items: int = 20
    ) -> list[str]:
        """Extract lines under the first matching target heading.

        Stops immediately when any known section title (e.g. VOLUNTEERING, EDUCATION) is encountered.
        """
        targets = {h.lower() for h in target_headings}
        for index, line in enumerate(lines):
            line_clean = line.lower().strip(":").strip()
            if line_clean in targets:
                section: list[str] = []
                for candidate in lines[index + 1 :]:
                    cand_clean = candidate.lower().strip(":").strip()
                    if cand_clean in _SECTION_TITLES and cand_clean not in targets:
                        break
                    section.append(candidate)
                    if len(section) >= max_items:
                        break
                return section
        return []
