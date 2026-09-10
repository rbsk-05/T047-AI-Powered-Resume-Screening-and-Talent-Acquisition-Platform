from app.schemas.job import JobDescriptionAnalysisRequest, JobProfile
from app.services.job_analyzer import JobDescriptionAnalyzer
from app.services.llm_provider import LLMProvider, get_llm_provider


class JDAgent:
    """Agent 2: Specialized Job Description Agent.
    
    Responsibilities:
    - Analyzes unstructured job description text.
    - Strictly distinguishes between Required Skills vs. Preferred Skills.
    - Extracts experience, education, and key responsibilities.
    - Does not invent requirements not present in the text.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()
        self.analyzer = JobDescriptionAnalyzer(llm_provider=self.llm_provider)

    def process(self, job_title: str, job_description: str) -> JobProfile:
        """Analyze job description into a structured JobProfile."""
        request = JobDescriptionAnalysisRequest(job_title=job_title, job_description=job_description)
        return self.analyzer.analyze(request)


