import re

from app.schemas.job import JobDescriptionAnalysisRequest, JobProfile
from app.services.llm_provider import LLMProvider, get_llm_provider


class JobDescriptionAnalyzer:
    """Extracts a structured job profile from a job description.

    Always computes the deterministic regex-based baseline first -- this
    keeps behaviour predictable, keeps tests fast and offline, and gives us
    something to fall back to. If an LLM provider is available and enabled,
    its extraction is used instead *only* where it returns a validly-typed
    value; any missing or malformed field quietly keeps the baseline value
    for that field. The response contract (JobProfile) never changes shape.
    """

    SKILLS = (
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "SQL",
        "React", "Angular", "Vue", "Node.js", "FastAPI", "Django", "Flask",
        "Spring Boot", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Git", "REST API",
        "GraphQL", "CI/CD", "Linux", "TensorFlow", "PyTorch", "spaCy",
    )
    EDUCATION = (
        "Computer Science", "Information Technology", "Software Engineering",
        "Computer Engineering", "Data Science",
    )
    PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "plus", "desirable")

    @staticmethod
    def _normalise(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _find_skills(self, text: str) -> list[str]:
        return [
            skill for skill in self.SKILLS
            if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text, re.IGNORECASE)
        ]

    def _split_skills_by_priority(self, text: str) -> tuple[list[str], list[str]]:
        preferred_sections: list[str] = []
        for sentence in re.split(r"(?<=[.!?;])", text):
            if any(marker in sentence.lower() for marker in self.PREFERRED_MARKERS):
                preferred_sections.append(sentence)

        preferred = self._find_skills(" ".join(preferred_sections))
        all_skills = self._find_skills(text)
        required = [skill for skill in all_skills if skill not in preferred]
        return required, preferred

    def _experience(self, text: str) -> str | None:
        match = re.search(
            r"\b(\d+(?:\s*[-+]\s*\d+)?\+?)\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
            text,
            re.IGNORECASE,
        )
        return f"{match.group(1)} years" if match else None

    def _education(self, text: str) -> list[str]:
        return [subject for subject in self.EDUCATION if subject.lower() in text.lower()]

    def _responsibilities(self, text: str) -> list[str]:
        sentences = [self._normalise(item) for item in re.split(r"(?<=[.!?])", text)]
        verbs = ("develop", "design", "build", "maintain", "lead", "collaborate", "implement", "manage")
        return [sentence for sentence in sentences if sentence and sentence.lower().startswith(verbs)][:6]

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()

    @staticmethod
    def _is_list_of_str(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    def analyze(self, request: JobDescriptionAnalysisRequest) -> JobProfile:
        text = self._normalise(request.job_description)
        required_skills, preferred_skills = self._split_skills_by_priority(text)
        baseline = JobProfile(
            job_title=request.job_title.strip(),
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            experience=self._experience(text),
            education=self._education(text),
            responsibilities=self._responsibilities(text),
        )
        if not self.llm_provider.available:
            return baseline

        extracted = self.llm_provider.extract_job_requirements(request.job_title, request.job_description)
        if not extracted:
            return baseline

        # Field-by-field validation: only trust LLM output where it's the
        # expected type, otherwise keep the deterministic baseline value.
        return JobProfile(
            job_title=baseline.job_title,
            required_skills=extracted["required_skills"] if self._is_list_of_str(extracted.get("required_skills")) else baseline.required_skills,
            preferred_skills=extracted["preferred_skills"] if self._is_list_of_str(extracted.get("preferred_skills")) else baseline.preferred_skills,
            experience=extracted["experience"] if isinstance(extracted.get("experience"), (str, type(None))) else baseline.experience,
            education=extracted["education"] if self._is_list_of_str(extracted.get("education")) else baseline.education,
            responsibilities=extracted["responsibilities"] if self._is_list_of_str(extracted.get("responsibilities")) else baseline.responsibilities,
        )
