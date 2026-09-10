from app.schemas.candidate import CandidateProfile
from app.services.llm_provider import LLMProvider, get_llm_provider
from app.services.resume_parser import ResumeParser


class ResumeAgent:
    """Agent 1: Specialized Resume Agent.
    
    Responsibilities:
    - Analyzes raw extracted resume text (PDF/DOCX).
    - Extracts candidate profile (skills, education, experience, projects, certifications).
    - Normalizes information without inventing unstated facts.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()
        self.parser = ResumeParser(llm_provider=self.llm_provider)

    def process(self, filename: str, content: bytes) -> CandidateProfile:
        """Parse uploaded resume binary content into a structured candidate profile."""
        return self.parser.parse(filename, content)

    def process_text(self, text: str) -> CandidateProfile:
        """Parse clean text into a structured candidate profile."""
        return self.parser.parse_text(text)
