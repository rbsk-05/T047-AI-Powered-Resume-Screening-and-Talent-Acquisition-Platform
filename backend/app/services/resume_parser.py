import io
import re

import fitz
from docx import Document

from app.schemas.candidate import CandidateProfile


from app.services.llm_provider import LLMProvider, get_llm_provider


class ResumeParser:
    """Extract text and structured candidate profile from a resume using AI + regex fallback."""

    ALLOWED_SUFFIXES = {".pdf", ".docx"}
    SKILLS = (
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "SQL",
        "React", "Angular", "Vue", "Node.js", "FastAPI", "Django", "Flask",
        "Spring Boot", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Git", "REST API",
        "GraphQL", "CI/CD", "Linux", "TensorFlow", "PyTorch", "spaCy",
    )
    SECTION_TITLES = ("projects", "project experience", "certifications", "education", "experience", "skills")

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()

    @staticmethod
    def _is_list_of_str(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    def extract_text(self, filename: str, content: bytes) -> str:
        suffix = filename.lower().rsplit(".", maxsplit=1)
        suffix = f".{suffix[-1]}" if len(suffix) == 2 else ""
        if suffix not in self.ALLOWED_SUFFIXES:
            raise ValueError("Only PDF and DOCX resume files are supported.")

        if suffix == ".pdf":
            document = fitz.open(stream=content, filetype="pdf")
            try:
                return "\n".join(page.get_text() for page in document)
            finally:
                document.close()

        document = Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    @staticmethod
    def _clean_lines(text: str) -> list[str]:
        return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]

    def _skills(self, text: str) -> list[str]:
        return [skill for skill in self.SKILLS if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text, re.IGNORECASE)]

    @staticmethod
    def _first_section(lines: list[str], heading: str) -> list[str]:
        for index, line in enumerate(lines):
            if line.lower().strip(":") == heading:
                section: list[str] = []
                for candidate in lines[index + 1:]:
                    if candidate.lower().strip(":") in ResumeParser.SECTION_TITLES:
                        break
                    section.append(candidate)
                return section[:6]
        return []

    @staticmethod
    def _name(lines: list[str]) -> str | None:
        if not lines:
            return None
        first_line = lines[0]
        return first_line if re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,80}", first_line) else None

    @staticmethod
    def _email(text: str) -> str | None:
        match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        return match.group(0) if match else None

    @staticmethod
    def _phone(text: str) -> str | None:
        match = re.search(r"(?<!\d)(?:\+?\d{1,3}[ -]?)?(?:\(?\d{2,4}\)?[ -]?)?\d{3,5}[ -]\d{4,6}(?!\d)", text)
        return match.group(0) if match else None

    @staticmethod
    def _experience(text: str) -> str | None:
        match = re.search(r"\b(\d+(?:\.\d+)?\+?)\s*(?:years?|yrs?)\s+(?:of\s+)?experience", text, re.IGNORECASE)
        return f"{match.group(1)} years" if match else None

    RESUME_SECTION_PATTERNS = [
        r"\b(?:skills|technical skills|technologies|core competencies|areas of expertise|tech stack|tools)\b",
        r"\b(?:experience|work experience|employment history|professional experience|career history|work history)\b",
        r"\b(?:education|academic background|qualifications|academic history|degrees|university|college|school)\b",
        r"\b(?:projects|key projects|academic projects|personal projects|technical projects)\b",
        r"\b(?:certifications|certificates|licenses|achievements|awards|summary|professional summary|profile|objective)\b",
    ]

    def validate_resume_structure(self, text: str) -> bool:
        """Verify that the document contains standard resume sections and structure."""
        if not text or len(text.strip()) < 40:
            return False
        
        matches = sum(1 for pattern in self.RESUME_SECTION_PATTERNS if re.search(pattern, text, re.IGNORECASE))
        has_contact = bool(self._email(text) or self._phone(text))
        has_skills = bool(self._skills(text))
        
        # Valid resume requires either multiple recognized sections OR contact info + at least 1 section/skill
        return (matches >= 2) or (has_contact and (matches >= 1 or has_skills))

    def parse_text(self, text: str) -> CandidateProfile:
        if not self.validate_resume_structure(text):
            raise ValueError(
                "The uploaded document does not appear to be a valid resume. "
                "Please make sure your file contains standard resume sections such as Skills, Experience, Education, or Projects."
            )

        lines = self._clean_lines(text)
        education_terms = ("B.E", "B.Tech", "B.Sc", "M.Sc", "M.E", "M.Tech", "Bachelor", "Master", "Computer Science", "Information Technology")
        education = [line for line in lines if any(term.lower() in line.lower() for term in education_terms)][:5]
        
        baseline = CandidateProfile(
            name=self._name(lines),
            email=self._email(text),
            phone=self._phone(text),
            skills=self._skills(text),
            experience=self._experience(text),
            education=education,
            projects=self._first_section(lines, "projects") or self._first_section(lines, "project experience"),
            certifications=self._first_section(lines, "certifications"),
        )

        if not self.llm_provider.available:
            return baseline

        extracted = self.llm_provider.extract_candidate_profile(text)
        if not extracted:
            return baseline

        # Merge extracted AI profile with baseline fallback
        llm_skills = extracted.get("skills") if self._is_list_of_str(extracted.get("skills")) else baseline.skills
        # Deduplicate and combine skills
        combined_skills = list(dict.fromkeys(llm_skills + baseline.skills))

        return CandidateProfile(
            name=extracted.get("name") if isinstance(extracted.get("name"), str) and extracted.get("name") else baseline.name,
            email=extracted.get("email") if isinstance(extracted.get("email"), str) and extracted.get("email") else baseline.email,
            phone=extracted.get("phone") if isinstance(extracted.get("phone"), str) and extracted.get("phone") else baseline.phone,
            skills=combined_skills,
            experience=extracted.get("experience") if isinstance(extracted.get("experience"), str) and extracted.get("experience") else baseline.experience,
            education=extracted.get("education") if self._is_list_of_str(extracted.get("education")) and extracted.get("education") else baseline.education,
            projects=extracted.get("projects") if self._is_list_of_str(extracted.get("projects")) and extracted.get("projects") else baseline.projects,
            certifications=extracted.get("certifications") if self._is_list_of_str(extracted.get("certifications")) and extracted.get("certifications") else baseline.certifications,
        )

    def parse(self, filename: str, content: bytes) -> CandidateProfile:
        return self.parse_text(self.extract_text(filename, content))

