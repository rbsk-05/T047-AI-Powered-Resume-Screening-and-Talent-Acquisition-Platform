from app.schemas.gap import SkillGap, SkillGapRequest, SkillGapResult


class SkillGapAnalyzer:
    """Identify and prioritize skills not evidenced in a candidate profile."""

    @staticmethod
    def _deduplicate_preserve_casing(skills: list[str]) -> list[str]:
        seen = set()
        result = []
        for skill in skills:
            cleaned = skill.strip()
            lowered = cleaned.lower()
            if lowered and lowered not in seen:
                seen.add(lowered)
                result.append(cleaned)
        return result

    def analyze(self, request: SkillGapRequest) -> SkillGapResult:
        candidate_skills = {skill.strip().lower() for skill in request.candidate_profile.skills if skill.strip()}
        required = request.job_profile.required_skills
        preferred = request.job_profile.preferred_skills
        
        raw_matched = [skill for skill in required + preferred if skill.strip().lower() in candidate_skills]
        matched = self._deduplicate_preserve_casing(raw_matched)

        gaps = []
        seen_gaps = set()
        
        for skill in required:
            lowered = skill.strip().lower()
            if lowered and lowered not in candidate_skills and lowered not in seen_gaps:
                seen_gaps.add(lowered)
                gaps.append(
                    SkillGap(
                        skill=skill.strip(),
                        priority="critical",
                        reason="This is a required skill for the target role and is not demonstrated in the candidate profile."
                    )
                )

        for skill in preferred:
            lowered = skill.strip().lower()
            if lowered and lowered not in candidate_skills and lowered not in seen_gaps:
                seen_gaps.add(lowered)
                gaps.append(
                    SkillGap(
                        skill=skill.strip(),
                        priority="important",
                        reason="This is a preferred skill for the target role and is not demonstrated in the candidate profile."
                    )
                )

        return SkillGapResult(matched_skills=matched, gaps=gaps)
