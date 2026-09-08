"""Resume parsing pipeline.

Responsibility chain
--------------------
1. ``extract_text``       – file-type validation + PDF/DOCX → raw text
2. ``validate_resume_structure`` – sanity-check: is this actually a resume?
3. ``parse_text``         – regex-based baseline extraction → ``CandidateProfile``
4. LLM enrichment (optional, falls back silently)
5. ``parse``              – convenience wrapper for bytes → ``CandidateProfile``

The module owns steps 1-5 entirely.  It does **not** perform any AI matching,
ranking, or scoring — those are Person 1's responsibility.
"""

from __future__ import annotations

import io
import re

import fitz
from docx import Document

from app.schemas.candidate import CandidateProfile, ExperienceEntry
from app.services.llm_provider import LLMProvider, get_llm_provider

# ---------------------------------------------------------------------------
# Skill vocabulary — broad, de-duplicated, case-insensitive at match time
# ---------------------------------------------------------------------------
_SKILLS: tuple[str, ...] = (
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "C",
    "Rust", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
    "MATLAB", "Bash", "Shell", "Perl", "Dart", "Elixir",
    # Frontend
    "React", "Angular", "Vue", "Next.js", "Nuxt.js", "Svelte",
    "HTML", "CSS", "SASS", "Bootstrap", "Tailwind",
    # Backend / frameworks
    "Node.js", "Express.js", "Nest.js", "FastAPI", "Django", "Flask",
    "Spring Boot", "Laravel", "Rails", ".NET", "ASP.NET",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Nginx", "Apache", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "ArgoCD", "Helm", "CI/CD", "Linux",
    # Data & databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "SQLite", "Oracle", "SQL Server",
    "Firebase", "Supabase", "Snowflake", "BigQuery", "Redshift",
    "Kafka", "RabbitMQ", "Celery", "Airflow", "dbt",
    # ML / AI
    "TensorFlow", "PyTorch", "scikit-learn", "Keras", "XGBoost",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV", "spaCy",
    "NLTK", "Hugging Face", "LangChain", "MLflow", "Spark", "Hadoop",
    # APIs & protocols
    "REST API", "GraphQL", "gRPC", "WebSockets", "OAuth", "JWT",
    # Practices / tools
    "Git", "SQL", "Microservices", "Agile", "Scrum", "TDD",
    "Prometheus", "Grafana", "Stripe", "Twilio", "SendGrid",
)

# ---------------------------------------------------------------------------
# Section heading vocabulary used by the section extractor and validator
# ---------------------------------------------------------------------------
_SECTION_TITLES: frozenset[str] = frozenset({
    "skills", "technical skills", "core competencies", "areas of expertise",
    "tech stack", "tools", "technologies",
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
    "volunteering", "volunteer experience",
})

# Patterns that strongly indicate a standard resume section
_RESUME_SECTION_PATTERNS: tuple[str, ...] = (
    r"\b(?:skills|technical skills|technologies|core competencies|areas of expertise|tech stack|tools)\b",
    r"\b(?:experience|work experience|employment history|professional experience|career history|work history)\b",
    r"\b(?:education|academic background|qualifications|academic history|degrees|university|college|school)\b",
    r"\b(?:projects|key projects|academic projects|personal projects|technical projects)\b",
    r"\b(?:certifications|certificates|licenses|achievements|awards|summary|professional summary|profile|objective)\b",
)


class ResumeParser:
    """Extract text and a structured ``CandidateProfile`` from a PDF or DOCX resume.

    The parser always produces a result — partial extraction is preferred over a
    hard failure.  Fields that cannot be extracted are ``None`` or empty lists.

    Two-layer extraction
    --------------------
    * **Baseline** — regex / heuristic extraction, zero external dependencies.
    * **LLM enrichment** — optional Groq-backed pass that can fill or improve
      fields the regex layer missed.  Falls back silently if unavailable.
    """

    ALLOWED_SUFFIXES: frozenset[str] = frozenset({".pdf", ".docx"})
    SKILLS = _SKILLS
    SECTION_TITLES = _SECTION_TITLES

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract_text(self, filename: str, content: bytes) -> str:
        """Validate the file and return extracted plain text.

        Raises
        ------
        ValueError
            If the extension is not ``.pdf`` or ``.docx``.
        ValueError
            If the file content is empty or zero-byte.
        """
        if not content:
            raise ValueError("The uploaded file is empty.")

        suffix = filename.lower().rsplit(".", maxsplit=1)
        suffix = f".{suffix[-1]}" if len(suffix) == 2 else ""
        if suffix not in self.ALLOWED_SUFFIXES:
            raise ValueError(
                f"Unsupported file type '{suffix or '(none)'}'. "
                "Only PDF and DOCX resume files are accepted."
            )

        if suffix == ".pdf":
            return self._extract_pdf(content)
        return self._extract_docx(content)

    def validate_resume_structure(self, text: str) -> bool:
        """Return ``True`` if *text* looks like a real resume.

        A valid resume must have at minimum:
        * Non-trivial length (≥ 80 characters after stripping)
        * Two or more recognised section headings, **or**
          contact information plus at least one section/skill hit.
        """
        if not text or len(text.strip()) < 80:
            return False

        section_hits = sum(
            1
            for pattern in _RESUME_SECTION_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)
        )
        has_contact = bool(self._email(text) or self._phone(text))
        has_skills = bool(self._skills(text))

        return (section_hits >= 2) or (has_contact and (section_hits >= 1 or has_skills))

    def parse_text(self, text: str) -> CandidateProfile:
        """Build a ``CandidateProfile`` from plain resume text.

        Raises
        ------
        ValueError
            If *text* does not pass ``validate_resume_structure``.
        """
        if not self.validate_resume_structure(text):
            raise ValueError(
                "The uploaded document does not appear to be a valid resume. "
                "Please ensure your file contains standard resume sections "
                "such as Skills, Experience, Education, or Projects."
            )

        lines = self._clean_lines(text)
        baseline = CandidateProfile(
            name=self._name(lines),
            email=self._email(text),
            phone=self._phone(text),
            linkedin=self._linkedin(text),
            github=self._github(text),
            summary=self._summary(lines),
            skills=self._skills(text),
            experience=self._experience_entries(text, lines),
            education=self._education(lines),
            projects=(
                self._first_section(lines, "projects")
                or self._first_section(lines, "project experience")
                or self._first_section(lines, "key projects")
            ),
            certifications=(
                self._first_section(lines, "certifications")
                or self._first_section(lines, "certificates")
            ),
        )

        if not self.llm_provider.available:
            return baseline

        extracted = self.llm_provider.extract_candidate_profile(text)
        if not extracted:
            return baseline

        return self._merge_with_llm(baseline, extracted)

    def parse(self, filename: str, content: bytes) -> CandidateProfile:
        """End-to-end convenience: bytes → ``CandidateProfile``."""
        return self.parse_text(self.extract_text(filename, content))

    # ------------------------------------------------------------------
    # File extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        try:
            document = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise ValueError(
                "The PDF file appears to be corrupted or unreadable."
            ) from exc
        try:
            pages = [page.get_text() for page in document]
        finally:
            document.close()
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                "No text could be extracted from the PDF. "
                "It may be a scanned image without OCR text."
            )
        return text

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        try:
            document = Document(io.BytesIO(content))
        except Exception as exc:
            raise ValueError(
                "The DOCX file appears to be corrupted or unreadable."
            ) from exc
        text = "\n".join(p.text for p in document.paragraphs).strip()
        if not text:
            raise ValueError("No text could be extracted from the DOCX file.")
        return text

    # ------------------------------------------------------------------
    # Text-cleaning utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_lines(text: str) -> list[str]:
        """Return non-empty, whitespace-normalised lines."""
        return [
            re.sub(r"\s+", " ", line).strip()
            for line in text.splitlines()
            if line.strip()
        ]

    # ------------------------------------------------------------------
    # Section extractor
    # ------------------------------------------------------------------

    @staticmethod
    def _first_section(
        lines: list[str], heading: str, max_items: int = 8
    ) -> list[str]:
        """Return up to *max_items* lines after the first occurrence of *heading*.

        Stops early when another known section title is encountered.
        """
        heading_norm = heading.lower()
        for index, line in enumerate(lines):
            if line.lower().strip(":") == heading_norm:
                section: list[str] = []
                for candidate in lines[index + 1 :]:
                    if candidate.lower().strip(":") in _SECTION_TITLES:
                        break
                    section.append(candidate)
                    if len(section) >= max_items:
                        break
                return section
        return []

    # ------------------------------------------------------------------
    # Field extractors
    # ------------------------------------------------------------------

    @staticmethod
    def _name(lines: list[str]) -> str | None:
        """Heuristic: first line that looks like a person's name."""
        for line in lines[:3]:
            if re.fullmatch(r"[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024F .'\-]{1,80}", line):
                return line
        return None

    @staticmethod
    def _email(text: str) -> str | None:
        match = re.search(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", text)
        return match.group(0) if match else None

    @staticmethod
    def _phone(text: str) -> str | None:
        """Captures common international and Indian mobile formats."""
        match = re.search(
            r"(?<!\d)"
            r"(?:\+?(\d{1,3})[\s\-.]?)?"          # country code
            r"(?:\(?\d{2,4}\)?[\s\-.]?)?"          # area code
            r"\d{3,5}[\s\-.]?\d{4,6}"              # local number
            r"(?!\d)",
            text,
        )
        return match.group(0).strip() if match else None

    @staticmethod
    def _linkedin(text: str) -> str | None:
        match = re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9\-_%]+)",
            text,
            re.IGNORECASE,
        )
        return f"https://linkedin.com/in/{match.group(1)}" if match else None

    @staticmethod
    def _github(text: str) -> str | None:
        match = re.search(
            r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9\-_.]+)",
            text,
            re.IGNORECASE,
        )
        return f"https://github.com/{match.group(1)}" if match else None

    @staticmethod
    def _summary(lines: list[str]) -> str | None:
        """Extract the candidate's own summary / objective paragraph."""
        for heading in ("summary", "professional summary", "objective", "profile", "about me", "about"):
            section = ResumeParser._first_section(lines, heading, max_items=4)
            if section:
                return " ".join(section).strip() or None
        return None

    def _skills(self, text: str) -> list[str]:
        """Return a de-duplicated list of recognised skills found in *text*."""
        found = [
            skill
            for skill in self.SKILLS
            if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text, re.IGNORECASE)
        ]
        # Preserve order, de-duplicate (case-insensitive)
        seen: set[str] = set()
        result: list[str] = []
        for skill in found:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                result.append(skill)
        return result

    @staticmethod
    def _education(lines: list[str]) -> list[str]:
        """Extract education lines from the education section and keyword scan."""
        # Try the dedicated section first
        section = (
            ResumeParser._first_section(lines, "education")
            or ResumeParser._first_section(lines, "academic background")
            or ResumeParser._first_section(lines, "qualifications")
        )
        if section:
            return section[:6]
        # Fall back to scanning all lines for degree keywords
        edu_terms = (
            "b.e", "b.tech", "b.sc", "b.s", "b.a", "m.sc", "m.e",
            "m.tech", "m.s", "m.a", "mba", "ph.d", "phd", "bachelor",
            "master", "associate", "diploma", "computer science",
            "information technology", "software engineering",
            "electronics", "electrical", "mechanical",
        )
        return [
            line
            for line in lines
            if any(term in line.lower() for term in edu_terms)
        ][:6]

    @staticmethod
    def _experience_entries(text: str, lines: list[str]) -> list[ExperienceEntry]:
        """Extract structured work-experience entries.

        Strategy
        --------
        1. Locate the experience section.
        2. Try to parse ``"Title at Company | date range"`` inline patterns.
        3. Try to parse ``"Company\\nDate range"`` two-line patterns.
        4. Fall back to a single entry with the years-of-experience figure.
        """
        section_lines = (
            ResumeParser._first_section(lines, "experience", max_items=30)
            or ResumeParser._first_section(lines, "work experience", max_items=30)
            or ResumeParser._first_section(lines, "professional experience", max_items=30)
            or ResumeParser._first_section(lines, "employment history", max_items=30)
            or ResumeParser._first_section(lines, "career history", max_items=30)
        )

        entries: list[ExperienceEntry] = []

        # Pattern A: "Job Title at Company | Jan 2020 – Dec 2022"
        inline_re = re.compile(
            r"^(.+?)\s+(?:at|@|,)\s+(.+?)\s*[|–\-]\s*(.+)$", re.IGNORECASE
        )
        # Pattern B: date range standalone (next / same line is the company / title)
        date_re = re.compile(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}"
            r"\s*[-–]\s*"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*"
            r"(?:\d{4}|Present|Current|Now)",
            re.IGNORECASE,
        )
        # Pattern C: "YYYY – YYYY" or "YYYY – Present"
        year_range_re = re.compile(
            r"\b\d{4}\s*[-–]\s*(?:\d{4}|Present|Current|Now)\b",
            re.IGNORECASE,
        )

        if section_lines:
            i = 0
            while i < len(section_lines):
                line = section_lines[i]

                # Pattern A
                m = inline_re.match(line)
                if m:
                    entries.append(
                        ExperienceEntry(
                            title=m.group(1).strip(),
                            company=m.group(2).strip(),
                            duration=m.group(3).strip(),
                        )
                    )
                    i += 1
                    continue

                # Pattern B / C: current line is entity, next line has date
                if i + 1 < len(section_lines):
                    next_line = section_lines[i + 1]
                    if date_re.search(next_line) or year_range_re.search(next_line):
                        entries.append(
                            ExperienceEntry(
                                company=line,
                                duration=next_line,
                            )
                        )
                        i += 2
                        continue

                # Standalone date on this line → treat as duration-only entry
                if date_re.search(line) or year_range_re.search(line):
                    if entries:
                        # Annotate the most recent entry if it lacks a duration
                        if entries[-1].duration is None:
                            entries[-1] = entries[-1].model_copy(
                                update={"duration": line}
                            )
                    i += 1
                    continue

                i += 1

        # Fallback: extract total years figure
        if not entries:
            years_m = re.search(
                r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
                text,
                re.IGNORECASE,
            )
            if years_m:
                entries.append(ExperienceEntry(duration=f"{years_m.group(1)} years"))

        return entries

    # ------------------------------------------------------------------
    # LLM merge
    # ------------------------------------------------------------------

    @staticmethod
    def _is_list_of_str(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    @staticmethod
    def _parse_llm_experience(raw: object) -> list[ExperienceEntry]:
        """Convert the LLM's experience payload into ``ExperienceEntry`` objects."""
        if not isinstance(raw, list) or not raw:
            return []
        entries: list[ExperienceEntry] = []
        for item in raw:
            if isinstance(item, dict):
                entries.append(
                    ExperienceEntry(
                        company=item.get("company") if isinstance(item.get("company"), str) else None,
                        title=item.get("title") if isinstance(item.get("title"), str) else None,
                        duration=item.get("duration") if isinstance(item.get("duration"), str) else None,
                        description=item.get("description") if isinstance(item.get("description"), str) else None,
                    )
                )
        return entries

    def _merge_with_llm(
        self, baseline: CandidateProfile, extracted: dict
    ) -> CandidateProfile:
        """Merge LLM-extracted fields with the regex baseline.

        The LLM result is preferred when it is non-empty and well-typed;
        otherwise the baseline value is kept.
        """

        def _str(key: str) -> str | None:
            val = extracted.get(key)
            return val if isinstance(val, str) and val.strip() else None

        # Skills: union of LLM + baseline, de-duplicated
        llm_skills = extracted.get("skills")
        if self._is_list_of_str(llm_skills) and llm_skills:
            combined = list(dict.fromkeys(llm_skills + baseline.skills))
        else:
            combined = baseline.skills

        # Experience: prefer LLM if it produced structured entries
        llm_experience = self._parse_llm_experience(extracted.get("experience"))
        merged_experience = llm_experience if llm_experience else baseline.experience

        llm_education = extracted.get("education")
        merged_education = (
            llm_education
            if self._is_list_of_str(llm_education) and llm_education
            else baseline.education
        )

        llm_projects = extracted.get("projects")
        merged_projects = (
            llm_projects
            if self._is_list_of_str(llm_projects) and llm_projects
            else baseline.projects
        )

        llm_certs = extracted.get("certifications")
        merged_certs = (
            llm_certs
            if self._is_list_of_str(llm_certs) and llm_certs
            else baseline.certifications
        )

        return CandidateProfile(
            candidate_id=baseline.candidate_id,
            name=_str("name") or baseline.name,
            email=_str("email") or baseline.email,
            phone=_str("phone") or baseline.phone,
            linkedin=_str("linkedin") or baseline.linkedin,
            github=_str("github") or baseline.github,
            summary=_str("summary") or baseline.summary,
            skills=combined,
            experience=merged_experience,
            education=merged_education,
            projects=merged_projects,
            certifications=merged_certs,
        )
