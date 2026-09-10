from app.schemas.gap import SkillGap, SkillGapRequest, SkillGapResult
from app.services.matching import CandidateMatcher


class SkillGapAnalyzer:
    """Identify and prioritize skills not evidenced in a candidate profile."""

    def __init__(self) -> None:
        self.matcher = CandidateMatcher()

    def analyze(self, request: SkillGapRequest) -> SkillGapResult:
        candidate_skills = {skill.lower().strip() for skill in request.candidate_profile.skills if skill.strip()}
        required = request.job_profile.required_skills
        preferred = request.job_profile.preferred_skills

        matched = [skill for skill in required + preferred if self.matcher._skill_matches(skill, candidate_skills)]
        gaps = [
            SkillGap(skill=skill, priority="critical", reason="This is a required skill for the target role and is not demonstrated in the candidate profile.")
            for skill in required if not self.matcher._skill_matches(skill, candidate_skills)
        ]
        gaps.extend(
            SkillGap(skill=skill, priority="important", reason="This is a preferred skill for the target role and is not demonstrated in the candidate profile.")
            for skill in preferred if not self.matcher._skill_matches(skill, candidate_skills)
        )
        return SkillGapResult(matched_skills=matched, gaps=gaps)

