from app.schemas.candidate import CandidateProfile
from app.schemas.gap import SkillGap, SkillGapRequest, SkillGapResult
from app.schemas.job import JobProfile
from app.services.skill_gap import SkillGapAnalyzer


class SkillAgent:
    """Agent 3: Specialized Skill & Semantic Gap Agent.
    
    Responsibilities:
    - Compares candidate skills against job requirements.
    - Determines matched skills, missing required skills (Critical), and missing preferred skills (Important).
    - Uses deterministic set operations and semantic interpretation.
    """

    def __init__(self) -> None:
        self.analyzer = SkillGapAnalyzer()

    def process(self, job_profile: JobProfile, candidate_profile: CandidateProfile) -> SkillGapResult:
        """Analyze and prioritize the candidate's skill gaps against the job profile."""
        request = SkillGapRequest(job_profile=job_profile, candidate_profile=candidate_profile)
        return self.analyzer.analyze(request)
