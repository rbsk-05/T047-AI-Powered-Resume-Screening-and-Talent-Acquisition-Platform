from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_candidate, require_recruiter
from app.db.session import get_db
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.user import User
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateEvaluation, EvaluationRequest
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest, MatchResult
from app.schemas.records import ApplicationCreate, StoredApplication
from app.schemas.gap import SkillGapResult
from app.schemas.recommendation import RecommendationResult
from app.schemas.workflow import CandidateWorkflowRequest
from app.agents.orchestrator import MultiAgentOrchestrator

router = APIRouter(prefix="/applications", tags=["applications"])
orchestrator = MultiAgentOrchestrator()


@router.post("", response_model=StoredApplication, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> StoredApplication:
    """Associate a stored candidate with a job, run complete analysis workflow, and save the result."""
    job = db.get(Job, payload.job_id)
    candidate = db.get(Candidate, payload.candidate_id)
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Job or candidate was not found.")

    job_profile = JobProfile.model_validate(job.structured_profile)
    candidate_profile = CandidateProfile.model_validate(candidate.structured_profile)
    
    # Run multi-agent orchestrator: Match -> Evaluate -> Skill Gap -> Recommendations
    result = orchestrator.run_candidate_pipeline(CandidateWorkflowRequest(job_profile=job_profile, candidate_profile=candidate_profile))

    application = Application(
        job_id=job.id,
        candidate_id=candidate.id,
        status="APPLIED",
        overall_match_score=result.match.overall_match_score,
        evaluation=result.model_dump(),
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return StoredApplication(
        id=application.id,
        job_id=application.job_id,
        candidate_id=application.candidate_id,
        status=application.status,
        match=result.match,
        evaluation=result.evaluation,
        skill_gap=result.skill_gap,
        recommendations=result.recommendations,
        created_at=application.created_at,
    )


def _enrich_evaluation_data(eval_data: dict, job_title: str | None = None, candidate_name: str | None = None) -> dict:
    if not isinstance(eval_data, dict):
        eval_data = {}
    evaluation_dict = dict(eval_data.get("evaluation", eval_data))
    match_dict = eval_data.get("match", {}) or evaluation_dict.get("match", {})
    summary = evaluation_dict.get("summary")

    if not summary or len(str(summary).strip()) < 30 or str(summary).strip().endswith((" an", " a", " the", " with", " and", " for", " has an")):
        cand_n = candidate_name or "The candidate"
        score = float(match_dict.get("overall_match_score", 0.0))
        exact = match_dict.get("exact_matched_skills", []) or match_dict.get("matched_skills", [])
        related = match_dict.get("related_matched_skills", [])
        missing_req = match_dict.get("missing_required_skills", [])

        parts = []
        if exact:
            parts.append(f"demonstrates verified core competencies in {', '.join(exact)}")
        if related:
            parts.append(f"possesses transferable foundations in {', '.join(related)}")
        if missing_req:
            parts.append(f"has critical skill gaps in {', '.join(missing_req[:5])}")
        elif not exact and not related:
            parts.append("does not currently list direct technical keywords for the required core stack")

        summary_detail = "; ".join(parts) if parts else "profile evaluated against job criteria"
        rec = evaluation_dict.get("recommendation") or (
            "Review required skill gaps before progressing" if missing_req
            else ("Recommended for technical interview" if score >= 80 else "Consider for recruiter review")
        )
        evaluation_dict["summary"] = (
            f"{cand_n} holds an overall ATS match score of {score}% for the {job_title or 'target'} role. "
            f"The candidate {summary_detail}. "
            f"Recommendation: {rec}."
        )
        if not evaluation_dict.get("recommendation"):
            evaluation_dict["recommendation"] = rec
    return evaluation_dict


@router.get("", response_model=list[StoredApplication])
def list_my_applications(db: Session = Depends(get_db), user: User = Depends(require_candidate)) -> list[StoredApplication]:
    """List applications submitted by the current candidate."""
    from sqlalchemy import select
    query = (
        select(Application, Job.title, Job.company_name, Candidate.name)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Candidate.candidate_user_id == user.id)
        .order_by(Application.created_at.desc())
    )
    results = db.execute(query).all()
    
    apps = []
    for app_obj, job_title, company_name, candidate_name in results:
        eval_data = app_obj.evaluation or {}
        match_data = eval_data.get("match", {})
        evaluation_data = _enrich_evaluation_data(eval_data, job_title=job_title, candidate_name=candidate_name)
        skill_gap_data = eval_data.get("skill_gap")
        recommendations_data = eval_data.get("recommendations")

        apps.append(
            StoredApplication(
                id=app_obj.id,
                job_id=app_obj.job_id,
                candidate_id=app_obj.candidate_id,
                status=app_obj.status,
                match=MatchResult.model_validate(match_data) if match_data else MatchResult.model_validate(evaluation_data.get("match")),
                evaluation=CandidateEvaluation.model_validate(evaluation_data),
                skill_gap=SkillGapResult.model_validate(skill_gap_data) if skill_gap_data else None,
                recommendations=RecommendationResult.model_validate(recommendations_data) if recommendations_data else None,
                created_at=app_obj.created_at,
                job_title=job_title,
                company_name=company_name,
            )
        )
        
    return apps



@router.get("/job/{job_id}", response_model=list[StoredApplication])
def list_job_applications(job_id: str, db: Session = Depends(get_db), user: User = Depends(require_recruiter)) -> list[StoredApplication]:
    """List applications for a specific job, ranked by score (descending). Restricted to recruiters."""
    import uuid
    from sqlalchemy import select
    
    # Verify the recruiter owns the job
    job = db.get(Job, uuid.UUID(job_id))
    if not job or job.recruiter_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found.")

    query = (
        select(Application, Job.title, Job.company_name, Candidate)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job.id)
        .order_by(Application.overall_match_score.desc())
    )
    results = db.execute(query).all()
    
    apps = []
    for app_obj, job_title, company_name, candidate_obj in results:
        eval_data = app_obj.evaluation or {}
        match_data = eval_data.get("match", {})
        evaluation_data = _enrich_evaluation_data(eval_data, job_title=job_title, candidate_name=candidate_obj.name)
        
        apps.append(
            StoredApplication(
                id=app_obj.id,
                job_id=app_obj.job_id,
                candidate_id=app_obj.candidate_id,
                status=app_obj.status,
                match=MatchResult.model_validate(match_data) if match_data else MatchResult.model_validate(evaluation_data.get("match")),
                evaluation=CandidateEvaluation.model_validate(evaluation_data),
                created_at=app_obj.created_at,
                job_title=job_title,
                company_name=company_name,
                candidate_name=candidate_obj.name,
                candidate_profile=CandidateProfile.model_validate(candidate_obj.structured_profile) if candidate_obj.structured_profile else None,
            )
        )
        
    return apps


from pydantic import BaseModel
class StatusUpdate(BaseModel):
    status: str


@router.patch("/{app_id}/status", response_model=StoredApplication)
def update_application_status(app_id: str, payload: StatusUpdate, db: Session = Depends(get_db), user: User = Depends(require_recruiter)) -> StoredApplication:
    """Update the status of an application (e.g. 'shortlisted', 'rejected')."""
    import uuid
    
    app_obj = db.get(Application, uuid.UUID(app_id))
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found.")
        
    # Verify recruiter owns the job
    job = db.get(Job, app_obj.job_id)
    if not job or job.recruiter_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized.")
        
    app_obj.status = payload.status
    db.commit()
    db.refresh(app_obj)
    
    return StoredApplication(
        id=app_obj.id,
        job_id=app_obj.job_id,
        candidate_id=app_obj.candidate_id,
        status=app_obj.status,
        match=MatchResult.model_validate(app_obj.evaluation["match"]),
        evaluation=CandidateEvaluation.model_validate(app_obj.evaluation),
        created_at=app_obj.created_at
    )


class CompareRequest(BaseModel):
    application_ids: list[str]


class SkillCoverageItem(BaseModel):
    skill: str
    is_required: bool
    coverage: dict[str, bool]


class CompareCandidateItem(BaseModel):
    id: str
    name: str
    overall_match_score: float
    experience: str | None
    education: list[str]
    status: str
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str


class CompareResponse(BaseModel):
    job_title: str
    skills_matrix: list[SkillCoverageItem]
    candidates: list[CompareCandidateItem]
    comparison_summary: str


@router.post("/compare", response_model=CompareResponse)
def compare_applications(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_recruiter),
) -> CompareResponse:
    """Compare 2 or more candidate applications side-by-side for a job."""
    import uuid
    from app.services.llm_provider import get_llm_provider

    if len(payload.application_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 candidates to compare.")

    app_uuids = [uuid.UUID(app_id) for app_id in payload.application_ids]
    
    # Query applications joined with Job and Candidate
    from sqlalchemy import select
    query = (
        select(Application, Job, Candidate)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.id.in_(app_uuids))
    )
    rows = db.execute(query).all()

    if not rows:
        raise HTTPException(status_code=404, detail="No matching applications found.")

    # Verify authorization
    for app_obj, job, _ in rows:
        if job.recruiter_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view these applications.")

    job_title = rows[0][1].title
    required_skills = rows[0][1].required_skills or []
    preferred_skills = rows[0][1].preferred_skills or []
    all_job_skills = list(dict.fromkeys(required_skills + preferred_skills))

    candidates_out: list[CompareCandidateItem] = []
    candidates_for_llm: list[dict] = []

    for app_obj, _, cand in rows:
        eval_data = app_obj.evaluation or {}
        match_data = eval_data.get("match", {})
        cand_name = cand.name or "Anonymous Candidate"
        matched = match_data.get("matched_skills", [])
        missing = match_data.get("missing_required_skills", []) + match_data.get("missing_preferred_skills", [])
        score = float(app_obj.overall_match_score or match_data.get("overall_match_score", 0.0))

        candidates_out.append(
            CompareCandidateItem(
                id=str(app_obj.id),
                name=cand_name,
                overall_match_score=score,
                experience=cand.structured_profile.get("experience"),
                education=cand.structured_profile.get("education", []),
                status=app_obj.status,
                matched_skills=matched,
                missing_skills=missing,
                summary=eval_data.get("summary", ""),
            )
        )
        candidates_for_llm.append({
            "name": cand_name,
            "score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "experience": cand.structured_profile.get("experience", "N/A"),
        })

    # Build skills coverage matrix
    skills_matrix: list[SkillCoverageItem] = []
    for skill in all_job_skills:
        is_req = skill in required_skills
        coverage = {}
        for app_obj, _, cand in rows:
            cand_name = cand.name or "Anonymous Candidate"
            cand_skills = {s.lower().strip() for s in cand.structured_profile.get("skills", []) if s}
            coverage[cand_name] = orchestrator.matcher._skill_matches(skill, cand_skills)
        skills_matrix.append(
            SkillCoverageItem(skill=skill, is_required=is_req, coverage=coverage)
        )

    # Generate AI comparison summary via Agent 4 (ExplanationAgent)
    summary = orchestrator.explanation_agent.explain_comparison(job_title, candidates_for_llm)

    if not summary:
        # Fallback comparison summary
        top_cand = max(candidates_out, key=lambda c: c.overall_match_score)
        summary = f"{top_cand.name} leads with the highest match score of {top_cand.overall_match_score}%, matching {len(top_cand.matched_skills)} skills. Review the matrix above for side-by-side skill coverage."

    return CompareResponse(
        job_title=job_title,
        skills_matrix=skills_matrix,
        candidates=candidates_out,
        comparison_summary=summary,
    )


