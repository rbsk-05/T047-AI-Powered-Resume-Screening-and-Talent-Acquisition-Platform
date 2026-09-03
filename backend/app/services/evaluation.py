from app.schemas.evaluation import CandidateEvaluation, EvaluationRequest, EvidenceItem
from app.services.llm_provider import LLMProvider, get_llm_provider
from app.services.matching import CandidateMatcher


class EvaluationService:
    """Create recruiter-friendly explanations for a match result.

    The recommendation, strengths, gaps, and evidence are always computed
    deterministically from the match result -- these drive decisions, so
    they stay fully auditable. Only the free-text `summary` is optionally
    handed to an LLM to phrase more naturally; the LLM is given the already-
    computed facts as ground truth and told not to add anything, and any
    failure falls back to the existing template.
    """

    def __init__(self, matcher: CandidateMatcher | None = None, llm_provider: LLMProvider | None = None) -> None:
        self.matcher = matcher or CandidateMatcher()
        self.llm_provider = llm_provider or get_llm_provider()

    @staticmethod
    def _recommendation(score: float, missing_required: list[str]) -> str:
        if missing_required:
            return "Review required skill gaps before progressing"
        if score >= 80:
            return "Recommended for technical interview"
        if score >= 60:
            return "Consider for recruiter review"
        return "Not recommended at this stage"

    def evaluate(self, request: EvaluationRequest) -> CandidateEvaluation:
        match = self.matcher.score(request.match_request)
        job = request.match_request.job_profile
        candidate = request.match_request.candidate_profile
        strengths = [f"Demonstrates {skill}" for skill in match.matched_skills]
        if match.score_breakdown.experience == 100 and job.experience:
            strengths.append(f"Meets the {job.experience} experience requirement")
        if match.score_breakdown.education == 100 and job.education:
            strengths.append("Meets the requested education requirement")

        gaps = [f"Required skill not demonstrated: {skill}" for skill in match.missing_required_skills]
        gaps.extend(f"Preferred skill not demonstrated: {skill}" for skill in match.missing_preferred_skills)
        evidence = [
            EvidenceItem(
                requirement=skill,
                status="matched" if skill in match.matched_skills else "missing",
                evidence=(f"Found in candidate skills: {skill}" if skill in match.matched_skills else "No supporting evidence found in the candidate profile."),
            )
            for skill in job.required_skills + job.preferred_skills
        ]
        candidate_name = candidate.name or "The candidate"
        summary = None
        if self.llm_provider.available:
            summary = self.llm_provider.generate_summary(
                candidate_name=candidate_name,
                overall_score=match.overall_match_score,
                matched_skills=match.matched_skills,
                missing_required_skills=match.missing_required_skills,
                missing_preferred_skills=match.missing_preferred_skills,
            )
        if summary is None:
            if match.missing_required_skills:
                summary = f"{candidate_name} has a {match.overall_match_score}% match, but lacks evidence for {', '.join(match.missing_required_skills)}."
            else:
                summary = f"{candidate_name} meets all required skills and has a {match.overall_match_score}% overall match."
        return CandidateEvaluation(
            match=match,
            recommendation=self._recommendation(match.overall_match_score, match.missing_required_skills),
            summary=summary,
            strengths=strengths,
            gaps=gaps,
            evidence=evidence,
        )
