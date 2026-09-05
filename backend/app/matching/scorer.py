import re

from app.schemas.match import ScoreBreakdown
from app.matching.embeddings import EmbeddingProvider, get_embedding_provider


class ComponentScorer:
    """Calculates weighted individual component scores for candidate matching."""

    WEIGHTS = {
        "required_skills": 0.35,
        "experience": 0.20,
        "education": 0.10,
        "projects": 0.15,
        "semantic_similarity": 0.15,
        "certifications": 0.05,
    }

    def __init__(self, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.embeddings = embedding_provider or get_embedding_provider()

    @staticmethod
    def normalise(values: list[str]) -> set[str]:
        return {value.strip().lower() for value in values if value.strip()}

    @staticmethod
    def extract_years(value: str | None) -> float | None:
        if not value:
            return None
        match = re.search(r"\d+(?:\.\d+)?", value)
        return float(match.group()) if match else None

    @staticmethod
    def extract_tokens(values: list[str]) -> set[str]:
        return set(re.findall(r"[a-z]{3,}", " ".join(values).lower()))

    def compute_breakdown(
        self,
        candidate_skills: set[str],
        required_skills: set[str],
        candidate_experience: str | None,
        job_experience: str | None,
        candidate_education: list[str],
        job_education: list[str],
        candidate_projects: list[str],
        job_responsibilities: list[str],
        candidate_certifications: list[str],
        job_all_skills: list[str],
        candidate_all_skills: list[str],
    ) -> ScoreBreakdown:
        # 1. Required skills match
        if required_skills:
            required_score = 100.0 * len(required_skills & candidate_skills) / len(required_skills)
        else:
            required_score = 100.0 if candidate_skills else 0.0

        # 2. Experience match
        required_years = self.extract_years(job_experience)
        candidate_years = self.extract_years(candidate_experience)
        if required_years is not None and required_years > 0:
            experience_score = min(100.0, 100.0 * (candidate_years or 0) / required_years)
        else:
            experience_score = 100.0 if candidate_years and candidate_years > 0 else 0.0

        # 3. Education match
        norm_req_edu = self.normalise(job_education)
        norm_cand_edu = self.normalise(candidate_education)
        if norm_req_edu:
            education_score = 100.0 if any(req in degree for req in norm_req_edu for degree in norm_cand_edu) else 0.0
        else:
            education_score = 100.0 if norm_cand_edu else 0.0

        # 4. Semantic & Project similarity
        if not candidate_skills and not candidate_projects:
            semantic_score = 0.0
            project_score = 0.0
        else:
            job_text = " ".join(job_all_skills + job_responsibilities)
            candidate_text = " ".join(candidate_all_skills + candidate_projects)
            raw_embedding_score = self.embeddings.similarity(job_text, candidate_text)
            if raw_embedding_score is not None:
                if raw_embedding_score <= 30.0:
                    semantic_score = 0.0
                else:
                    semantic_score = min(100.0, (raw_embedding_score - 30.0) / (100.0 - 30.0) * 100.0)
            else:
                job_tokens = self.extract_tokens(job_all_skills + job_responsibilities)
                candidate_tokens = self.extract_tokens(candidate_all_skills + candidate_projects)
                semantic_score = 100.0 * len(job_tokens & candidate_tokens) / len(job_tokens | candidate_tokens) if job_tokens | candidate_tokens else 0.0

            project_score = semantic_score if candidate_projects else 0.0

        # 5. Certifications match
        certification_score = 100.0 if candidate_certifications else 0.0

        return ScoreBreakdown(
            required_skills=round(required_score, 1),
            experience=round(experience_score, 1),
            education=round(education_score, 1),
            projects=round(project_score, 1),
            semantic_similarity=round(semantic_score, 1),
            certifications=round(certification_score, 1),
        )

    def calculate_overall_score(self, breakdown: ScoreBreakdown) -> float:
        overall = sum(getattr(breakdown, key) * weight for key, weight in self.WEIGHTS.items())
        return round(overall, 1)
