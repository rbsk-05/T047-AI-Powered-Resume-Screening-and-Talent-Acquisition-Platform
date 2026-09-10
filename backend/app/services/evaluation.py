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
        strengths = [f"Demonstrates required skill: {skill}" for skill in match.exact_matched_skills]
        strengths.extend([f"Demonstrates related skill: {skill}" for skill in match.related_matched_skills])
        if match.score_breakdown.experience == 100 and job.experience:
            strengths.append(f"Meets the {job.experience} experience requirement")
        if match.score_breakdown.education == 100 and job.education:
            strengths.append("Meets the requested education requirement")

        gaps = [f"Required skill not demonstrated: {skill}" for skill in match.missing_required_skills]
        gaps.extend(f"Preferred skill not demonstrated: {skill}" for skill in match.missing_preferred_skills)

        # Build evidence items from match_details
        evidence_by_req = {d.skill_name: d for d in match.match_details}
        evidence = []
        for req_skill in job.required_skills + job.preferred_skills:
            if req_skill in evidence_by_req:
                detail = evidence_by_req[req_skill]
                status_str = detail.match_level.value.lower() if hasattr(detail.match_level, "value") else str(detail.match_level).lower()
                evidence.append(
                    EvidenceItem(
                        requirement=req_skill,
                        status=status_str,
                        evidence=detail.explanation or (f"Found in candidate skills: {detail.matched_candidate_skill}" if detail.matched_candidate_skill else "No supporting evidence found in candidate profile."),
                    )
                )
            else:
                is_matched = req_skill in match.matched_skills
                evidence.append(
                    EvidenceItem(
                        requirement=req_skill,
                        status="exact" if is_matched else "missing",
                        evidence=f"Found in candidate skills: {req_skill}" if is_matched else "No supporting evidence found in the candidate profile.",
                    )
                )

        candidate_name = candidate.name or "The candidate"
        recommendation = self._recommendation(match.overall_match_score, match.missing_required_skills)
        job_role = getattr(job, "job_title", getattr(job, "title", "target"))
        summary = None
        if self.llm_provider.available:
            summary = self.llm_provider.generate_summary(
                candidate_name=candidate_name,
                overall_score=match.overall_match_score,
                matched_skills=match.matched_skills,
                missing_required_skills=match.missing_required_skills,
                missing_preferred_skills=match.missing_preferred_skills,
                job_title=job_role,
                experience=candidate.experience,
                recommendation=recommendation,
            )
        if not summary or len(summary.strip()) < 30 or summary.strip().endswith((" an", " a", " the", " with", " and", " for")):
            parts = []
            if match.exact_matched_skills:
                parts.append(f"demonstrates verified core competencies in {', '.join(match.exact_matched_skills)}")
            if match.related_matched_skills:
                parts.append(f"possesses transferable foundations in {', '.join(match.related_matched_skills)}")
            if match.missing_required_skills:
                parts.append(f"has critical skill gaps in {', '.join(match.missing_required_skills[:5])}")
            elif not match.exact_matched_skills and not match.related_matched_skills:
                parts.append("does not currently list direct technical keywords for the required core stack")

            summary_detail = "; ".join(parts) if parts else "profile evaluated against job criteria"
            exp_detail = f" Demonstrates strong background alignment with {candidate.experience or 'required experience'}." if match.score_breakdown.experience >= 80 else ""
            summary = (
                f"{candidate_name} holds an overall ATS match score of {match.overall_match_score}% for the {job_role or 'target'} role. "
                f"The candidate {summary_detail}.{exp_detail} "
                f"Recommendation: {recommendation}."
            )

        return CandidateEvaluation(
            match=match,
            recommendation=recommendation,
            summary=summary,
            strengths=strengths,
            gaps=gaps,
            evidence=evidence,
        )
