from app.schemas.match import MatchRequest, MatchResult
from app.matching.embeddings import EmbeddingProvider, get_embedding_provider
from app.matching.scorer import ComponentScorer


class CandidateMatcher:
    """Explainable scoring for one candidate profile against one job profile."""

    WEIGHTS = ComponentScorer.WEIGHTS

    def __init__(self, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.embeddings = embedding_provider or get_embedding_provider()
        self.scorer = ComponentScorer(embedding_provider=self.embeddings)

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

    def score(self, request: MatchRequest) -> MatchResult:
        job = request.job_profile
        candidate = request.candidate_profile
        candidate_skills = self.scorer.normalise(candidate.skills)
        required = self.scorer.normalise(job.required_skills)
        
        raw_matched = [skill for skill in job.required_skills + job.preferred_skills if skill.strip().lower() in candidate_skills]
        matched = self._deduplicate_preserve_casing(raw_matched)
        
        missing_required = self._deduplicate_preserve_casing(
            [skill for skill in job.required_skills if skill.strip().lower() not in candidate_skills]
        )
        missing_preferred = self._deduplicate_preserve_casing(
            [skill for skill in job.preferred_skills if skill.strip().lower() not in candidate_skills]
        )

        breakdown = self.scorer.compute_breakdown(
            candidate_skills=candidate_skills,
            required_skills=required,
            candidate_experience=candidate.experience,
            job_experience=job.experience,
            candidate_education=candidate.education,
            job_education=job.education,
            candidate_projects=candidate.projects,
            job_responsibilities=job.responsibilities,
            candidate_certifications=candidate.certifications,
            job_all_skills=job.required_skills + job.preferred_skills,
            candidate_all_skills=candidate.skills,
        )

        overall = self.scorer.calculate_overall_score(breakdown)

        return MatchResult(
            overall_match_score=overall,
            score_breakdown=breakdown,
            matched_skills=matched,
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
        )
