import re

from app.schemas.match import MatchRequest, MatchResult, ScoreBreakdown
from app.services.embedding_provider import EmbeddingProvider, get_embedding_provider


class CandidateMatcher:
    """Explainable scoring for one candidate against one job profile.

    Semantic similarity prefers Sentence Transformers embeddings when
    available, and falls back to lexical (Jaccard) token overlap otherwise.
    Either way the six weighted component scores and their weights stay
    fixed and auditable -- only how `semantic_similarity` is computed
    changes, never what it means or how much it counts.
    """

    def __init__(self, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.embeddings = embedding_provider or get_embedding_provider()

    WEIGHTS = {
        "required_skills": 0.35,
        "experience": 0.20,
        "education": 0.10,
        "projects": 0.15,
        "semantic_similarity": 0.15,
        "certifications": 0.05,
    }

    @staticmethod
    def _normalise(values: list[str]) -> set[str]:
        return {value.strip().lower() for value in values if value.strip()}

    @staticmethod
    def _years(value: str | None) -> float | None:
        if not value:
            return None
        match = re.search(r"\d+(?:\.\d+)?", value)
        return float(match.group()) if match else None

    @staticmethod
    def _tokens(values: list[str]) -> set[str]:
        return set(re.findall(r"[a-z]{3,}", " ".join(values).lower()))

    def score(self, request: MatchRequest) -> MatchResult:
        job = request.job_profile
        candidate = request.candidate_profile
        candidate_skills = self._normalise(candidate.skills)
        required = self._normalise(job.required_skills)
        preferred = self._normalise(job.preferred_skills)
        matched = [skill for skill in job.required_skills + job.preferred_skills if skill.lower() in candidate_skills]
        missing_required = [skill for skill in job.required_skills if skill.lower() not in candidate_skills]
        missing_preferred = [skill for skill in job.preferred_skills if skill.lower() not in candidate_skills]

        # Required skills match
        if required:
            required_score = 100.0 * len(required & candidate_skills) / len(required)
        else:
            required_score = 100.0 if candidate_skills else 0.0

        # Experience match
        required_years, candidate_years = self._years(job.experience), self._years(candidate.experience)
        if required_years is not None and required_years > 0:
            experience_score = min(100.0, 100.0 * (candidate_years or 0) / required_years)
        else:
            experience_score = 100.0 if candidate_years and candidate_years > 0 else 0.0

        # Education match
        required_education = self._normalise(job.education)
        candidate_education = self._normalise(candidate.education)
        if required_education:
            education_score = 100.0 if any(req in degree for req in required_education for degree in candidate_education) else 0.0
        else:
            education_score = 100.0 if candidate_education else 0.0

        # Semantic & Project similarity
        if not candidate_skills and not candidate.projects:
            semantic_score = 0.0
            project_score = 0.0
        else:
            job_text = " ".join(job.required_skills + job.preferred_skills + job.responsibilities)
            candidate_text = " ".join(candidate.skills + candidate.projects)
            raw_embedding_score = self.embeddings.similarity(job_text, candidate_text)
            if raw_embedding_score is not None:
                # Cosine similarity noise floor calibration:
                # Unrelated English text usually scores 0.25 - 0.35 (25 - 35).
                # Subtract the baseline floor and scale 0-100.
                if raw_embedding_score <= 30.0:
                    semantic_score = 0.0
                else:
                    semantic_score = min(100.0, (raw_embedding_score - 30.0) / (100.0 - 30.0) * 100.0)
            else:
                job_tokens = self._tokens(job.required_skills + job.preferred_skills + job.responsibilities)
                candidate_tokens = self._tokens(candidate.skills + candidate.projects)
                semantic_score = 100.0 * len(job_tokens & candidate_tokens) / len(job_tokens | candidate_tokens) if job_tokens | candidate_tokens else 0.0
            
            project_score = semantic_score if candidate.projects else 0.0

        certification_score = 100.0 if candidate.certifications else 0.0
        breakdown = ScoreBreakdown(
            required_skills=round(required_score, 1),
            experience=round(experience_score, 1),
            education=round(education_score, 1),
            projects=round(project_score, 1),
            semantic_similarity=round(semantic_score, 1),
            certifications=round(certification_score, 1),
        )
        overall = sum(getattr(breakdown, key) * weight for key, weight in self.WEIGHTS.items())
        return MatchResult(
            overall_match_score=round(overall, 1),
            score_breakdown=breakdown,
            matched_skills=matched,
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
        )
