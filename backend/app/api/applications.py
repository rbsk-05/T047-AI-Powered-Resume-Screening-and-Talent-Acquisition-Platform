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
from app.services.evaluation import EvaluationService
from app.services.matching import CandidateMatcher

router = APIRouter(prefix="/applications", tags=["applications"])
matcher = CandidateMatcher()
evaluator = EvaluationService()


@router.post("", response_model=StoredApplication, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> StoredApplication:
    """Associate a stored candidate with a job and save the current evaluation."""
    job = db.get(Job, payload.job_id)
    candidate = db.get(Candidate, payload.candidate_id)
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Job or candidate was not found.")
    match_request = MatchRequest(job_profile=JobProfile.model_validate(job.structured_profile), candidate_profile=CandidateProfile.model_validate(candidate.structured_profile))
    match = matcher.score(match_request)
    evaluation = evaluator.evaluate(EvaluationRequest(match_request=match_request))
    application = Application(job_id=job.id, candidate_id=candidate.id, overall_match_score=match.overall_match_score, evaluation=evaluation.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return StoredApplication(id=application.id, job_id=application.job_id, candidate_id=application.candidate_id, status=application.status, match=match, evaluation=evaluation, created_at=application.created_at)


@router.get("", response_model=list[StoredApplication])
def list_my_applications(db: Session = Depends(get_db), user: User = Depends(require_candidate)) -> list[StoredApplication]:
    """List applications submitted by the current candidate."""
    from sqlalchemy import select
    query = (
        select(Application, Job.title, Job.company_name)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Candidate.candidate_user_id == user.id)
        .order_by(Application.created_at.desc())
    )
    results = db.execute(query).all()
    
    apps = []
    for app_obj, job_title, company_name in results:
        apps.append(
            StoredApplication(
                id=app_obj.id,
                job_id=app_obj.job_id,
                candidate_id=app_obj.candidate_id,
                status=app_obj.status,
                match=MatchResult.model_validate(app_obj.evaluation["match"]),
                evaluation=CandidateEvaluation.model_validate(app_obj.evaluation),
                created_at=app_obj.created_at,
                job_title=job_title,
                company_name=company_name
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
        select(Application, Job.title, Job.company_name, Candidate.name)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job.id)
        .order_by(Application.overall_match_score.desc())
    )
    results = db.execute(query).all()
    
    apps = []
    for app_obj, job_title, company_name, candidate_name in results:
        # We'll abuse company_name to pass back candidate_name for the recruiter UI
        apps.append(
            StoredApplication(
                id=app_obj.id,
                job_id=app_obj.job_id,
                candidate_id=app_obj.candidate_id,
                status=app_obj.status,
                match=MatchResult.model_validate(app_obj.evaluation["match"]),
                evaluation=CandidateEvaluation.model_validate(app_obj.evaluation),
                created_at=app_obj.created_at,
                job_title=job_title,
                company_name=candidate_name # Hack: passing candidate name instead
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
    
    # We won't bother injecting titles here since this is just a quick update return
    return StoredApplication(
        id=app_obj.id,
        job_id=app_obj.job_id,
        candidate_id=app_obj.candidate_id,
        status=app_obj.status,
        match=MatchResult.model_validate(app_obj.evaluation["match"]),
        evaluation=CandidateEvaluation.model_validate(app_obj.evaluation),
        created_at=app_obj.created_at
    )

