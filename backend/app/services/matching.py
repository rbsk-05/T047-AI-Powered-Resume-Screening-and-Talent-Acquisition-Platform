from app.schemas.match import MatchLevel, MatchRequest, MatchResult, ScoreBreakdown, SkillMatchDetail
from app.services.embedding_provider import EmbeddingProvider, get_embedding_provider
from app.services.skill_ontology import RelationshipType, SkillOntology, get_skill_ontology


class CandidateMatcher:
    """Intelligent, explainable, 3-level candidate matching engine.

    Evaluates candidates against job profiles across:
    1. Level 1 — Exact Match (1.0): Direct technology or canonical alias match.
    2. Level 2 — Related Match (0.4-0.6): Ontology ecosystem, parent, or related technology match.
    3. Level 3 — Missing / No Evidence (0.0): No exact or related skill found.

    Fairness Guarantee:
    If a technology is NOT explicitly specified in the JD (e.g. generic web development),
    candidates are NOT penalized for specific unrequested technologies.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        ontology: SkillOntology | None = None,
    ) -> None:
        self.embeddings = embedding_provider or get_embedding_provider()
        self.ontology = ontology or get_skill_ontology()

    WEIGHTS = {
        "required_skills": 0.35,
        "experience": 0.20,
        "education": 0.10,
        "projects": 0.15,
        "semantic_similarity": 0.15,
        "certifications": 0.05,
    }

    def _skill_matches(self, skill: str, candidate_skills: set[str]) -> bool:
        """Helper to check if a skill matches (exact or related/substring)."""
        s_norm, _ = self.ontology.normalize_skill(skill)
        s_low = (s_norm or skill).lower().strip()
        if not s_low:
            return False

        for cand in candidate_skills:
            c_norm, _ = self.ontology.normalize_skill(cand)
            c_low = (c_norm or cand).lower().strip()

            rel = self.ontology.find_relationship(s_low, c_low)
            if rel.relation_type in (RelationshipType.EXACT, RelationshipType.ALIAS, RelationshipType.ECOSYSTEM, RelationshipType.PARENT):
                return True
            if s_low in c_low or c_low in s_low:
                return True

        return False

    @staticmethod
    def _normalise(values: list[str]) -> set[str]:
        return {value.strip().lower() for value in values if value.strip()}

    @staticmethod
    def _years(value: str | None) -> float | None:
        if not value:
            return None
        num_str = "".join(c for c in value if c.isdigit() or c == ".").strip(".")
        try:
            return float(num_str) if num_str else None
        except ValueError:
            return None

    @staticmethod
    def _tokens(values: list[str]) -> set[str]:
        words = " ".join(values).lower().replace(",", " ").replace(".", " ").replace(";", " ").split()
        return {w for w in words if len(w) >= 3 and w.isalpha()}

    def evaluate_skill_requirement(self, req_skill: str, candidate_skills: list[str]) -> SkillMatchDetail:
        """Evaluates a single skill requirement against candidate skills using 3-level ontology matching."""
        req_norm, _ = self.ontology.normalize_skill(req_skill)
        canonical_req = req_norm if req_norm else req_skill

        best_detail = SkillMatchDetail(
            skill_name=req_skill,
            match_level=MatchLevel.MISSING,
            matched_candidate_skill=None,
            relationship_type=RelationshipType.NONE.value,
            score_weight=0.0,
            explanation=f"No supporting evidence found in candidate profile for {req_skill}.",
        )

        for cand_s in candidate_skills:
            cand_norm, _ = self.ontology.normalize_skill(cand_s)
            canonical_cand = cand_norm if cand_norm else cand_s

            rel = self.ontology.find_relationship(canonical_req, canonical_cand)

            if rel.relation_type in (RelationshipType.EXACT, RelationshipType.ALIAS):
                return SkillMatchDetail(
                    skill_name=req_skill,
                    match_level=MatchLevel.EXACT,
                    matched_candidate_skill=cand_s,
                    relationship_type=rel.relation_type.value,
                    score_weight=1.0,
                    explanation=f"Exact match with {cand_s}.",
                )
            elif rel.relation_type == RelationshipType.ECOSYSTEM and best_detail.score_weight < 0.6:
                best_detail = SkillMatchDetail(
                    skill_name=req_skill,
                    match_level=MatchLevel.RELATED,
                    matched_candidate_skill=cand_s,
                    relationship_type=rel.relation_type.value,
                    score_weight=0.6,
                    explanation=f"Candidate has {cand_s} ({rel.description}).",
                )
            elif rel.relation_type == RelationshipType.PARENT and best_detail.score_weight < 0.6:
                best_detail = SkillMatchDetail(
                    skill_name=req_skill,
                    match_level=MatchLevel.RELATED,
                    matched_candidate_skill=cand_s,
                    relationship_type=rel.relation_type.value,
                    score_weight=0.6,
                    explanation=rel.description,
                )
            elif rel.relation_type == RelationshipType.CHILD and best_detail.score_weight < 0.6:
                best_detail = SkillMatchDetail(
                    skill_name=req_skill,
                    match_level=MatchLevel.RELATED,
                    matched_candidate_skill=cand_s,
                    relationship_type=rel.relation_type.value,
                    score_weight=0.6,
                    explanation=rel.description,
                )
            elif rel.relation_type == RelationshipType.RELATED and best_detail.score_weight < 0.4:
                best_detail = SkillMatchDetail(
                    skill_name=req_skill,
                    match_level=MatchLevel.RELATED,
                    matched_candidate_skill=cand_s,
                    relationship_type=rel.relation_type.value,
                    score_weight=0.4,
                    explanation=rel.description,
                )

        return best_detail

    def score(self, request: MatchRequest) -> MatchResult:
        job = request.job_profile
        candidate = request.candidate_profile
        candidate_skills = candidate.skills

        exact_matches: list[str] = []
        related_matches: list[str] = []
        missing_required: list[str] = []
        missing_preferred: list[str] = []
        match_details: list[SkillMatchDetail] = []

        total_req_points = 0.0
        max_req_points = float(len(job.required_skills)) if job.required_skills else 1.0

        # Evaluate Required Skills
        for req in job.required_skills:
            detail = self.evaluate_skill_requirement(req, candidate_skills)
            match_details.append(detail)

            if detail.match_level == MatchLevel.EXACT:
                exact_matches.append(detail.skill_name)
                total_req_points += 1.0
            elif detail.match_level == MatchLevel.RELATED:
                related_matches.append(f"{detail.skill_name} ({detail.matched_candidate_skill})")
                total_req_points += detail.score_weight
            else:
                missing_required.append(detail.skill_name)

        # Evaluate Preferred Skills
        for pref in job.preferred_skills:
            detail = self.evaluate_skill_requirement(pref, candidate_skills)
            match_details.append(detail)

            if detail.match_level == MatchLevel.EXACT:
                exact_matches.append(detail.skill_name)
            elif detail.match_level == MatchLevel.RELATED:
                related_matches.append(f"{detail.skill_name} ({detail.matched_candidate_skill})")
            else:
                missing_preferred.append(detail.skill_name)

        # 1. Required Skills Score
        if job.required_skills:
            required_score = min(100.0, 100.0 * total_req_points / max_req_points)
        else:
            # Fairness rule for generic JDs: if candidate has domain skills, score favorably
            required_score = 100.0 if candidate_skills else 0.0

        # 2. Experience match
        required_years, candidate_years = self._years(job.experience), self._years(candidate.experience)
        if required_years is not None and required_years > 0:
            experience_score = min(100.0, 100.0 * (candidate_years or 0) / required_years)
        else:
            experience_score = 100.0 if candidate_years and candidate_years > 0 else 0.0

        # 3. Education match
        required_education = self._normalise(job.education)
        candidate_education = self._normalise(candidate.education)
        if required_education:
            education_score = 100.0 if any(req in degree for req in required_education for degree in candidate_education) else 0.0
        else:
            education_score = 100.0 if candidate_education else 0.0

        # 4. Semantic & Project similarity
        if not candidate_skills and not candidate.projects:
            semantic_score = 0.0
            project_score = 0.0
        else:
            job_text = " ".join(job.required_skills + job.preferred_skills + job.responsibilities + [job.job_family])
            candidate_text = " ".join(candidate.skills + candidate.projects + candidate.domain_knowledge)
            raw_embedding_score = self.embeddings.similarity(job_text, candidate_text)
            if raw_embedding_score is not None:
                if raw_embedding_score <= 30.0:
                    semantic_score = 0.0
                else:
                    semantic_score = min(100.0, (raw_embedding_score - 30.0) / (100.0 - 30.0) * 100.0)
            else:
                job_tokens = self._tokens(job.required_skills + job.preferred_skills + job.responsibilities + [job.job_family])
                candidate_tokens = self._tokens(candidate.skills + candidate.projects)
                semantic_score = 100.0 * len(job_tokens & candidate_tokens) / len(job_tokens | candidate_tokens) if job_tokens | candidate_tokens else 0.0

            project_score = semantic_score if candidate.projects else 0.0

        # 5. Certification match
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

        # Preferred skills bonus/penalty adjustment (lighter weight: up to +/- 5 points)
        if job.preferred_skills:
            pref_matched = len(job.preferred_skills) - len(missing_preferred)
            pref_bonus = 5.0 * (pref_matched / len(job.preferred_skills))
            overall = min(100.0, overall + pref_bonus)

        # Confidence calculation
        total_eval_reqs = len(job.required_skills) + len(job.preferred_skills)
        matched_eval_reqs = len(exact_matches) + len(related_matches)
        coverage_pct = round(100.0 * matched_eval_reqs / total_eval_reqs, 1) if total_eval_reqs > 0 else 100.0

        if coverage_pct >= 75 and bool(candidate.skills) and bool(candidate.experience):
            confidence_level = "HIGH"
        elif coverage_pct >= 40 or bool(candidate.skills):
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        matched_all = list(dict.fromkeys(exact_matches + related_matches))

        return MatchResult(
            overall_match_score=round(overall, 1),
            score_breakdown=breakdown,
            matched_skills=matched_all,
            exact_matched_skills=exact_matches,
            related_matched_skills=related_matches,
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
            match_details=match_details,
            confidence_level=confidence_level,
            evidence_coverage_pct=coverage_pct,
        )

