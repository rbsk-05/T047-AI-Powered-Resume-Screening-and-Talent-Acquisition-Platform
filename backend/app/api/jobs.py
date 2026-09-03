from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_recruiter
from app.db.session import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreateRequest, JobDescriptionAnalysisRequest, JobProfile
from app.schemas.records import StoredJob
from app.services.job_analyzer import JobDescriptionAnalyzer

router = APIRouter(prefix="/jobs", tags=["job descriptions"])
analyzer = JobDescriptionAnalyzer()


def _job_to_stored(job: Job) -> StoredJob:
    """Convert a Job ORM row into a StoredJob response schema."""
    profile = JobProfile.model_validate(job.structured_profile)
    return StoredJob(
        id=job.id,
        title=job.title,
        description=job.description,
        company_name=job.company_name,
        location=job.location,
        employment_type=job.employment_type,
        experience_required=job.experience_required,
        required_skills=job.required_skills or profile.required_skills,
        preferred_skills=job.preferred_skills or profile.preferred_skills,
        education=job.education or profile.education,
        status=job.status,
        profile=profile,
        created_at=job.created_at,
    )


@router.post("/analyze", response_model=JobProfile)
def analyze_job_description(payload: JobDescriptionAnalysisRequest) -> JobProfile:
    """Convert an unstructured job description into a structured job profile."""
    return analyzer.analyze(payload)


@router.post("", response_model=StoredJob, status_code=201)
def create_job(
    payload: JobCreateRequest,
    db: Session = Depends(get_db),
    recruiter: User = Depends(require_recruiter),
) -> StoredJob:
    """Analyze and persist a job description. Restricted to recruiter accounts.

    The AI JD agent runs first to build a structured profile. Manually entered
    skills / education are merged with AI-extracted values so neither is lost.
    """
    profile = analyzer.analyze(payload)

    # Merge manual skills with AI-extracted (manual entries take priority, AI fills gaps)
    merged_required = list(dict.fromkeys(payload.required_skills + profile.required_skills)) if payload.required_skills else profile.required_skills
    merged_preferred = list(dict.fromkeys(payload.preferred_skills + profile.preferred_skills)) if payload.preferred_skills else profile.preferred_skills
    merged_education = list(dict.fromkeys(payload.education + profile.education)) if payload.education else profile.education

    # Use recruiter's registered company_name if form field is blank
    company = payload.company_name.strip() or (recruiter.company_name or "")

    job = Job(
        title=profile.job_title,
        description=payload.job_description,
        company_name=company,
        location=payload.location.strip() or None,
        employment_type=payload.employment_type.strip() or None,
        experience_required=payload.experience_required.strip() or profile.experience or None,
        required_skills=merged_required,
        preferred_skills=merged_preferred,
        education=merged_education,
        structured_profile=profile.model_dump(),
        status="published",
        recruiter_id=recruiter.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_to_stored(job)


@router.get("", response_model=list[StoredJob])
def list_jobs(db: Session = Depends(get_db)) -> list[StoredJob]:
    """List all published jobs, newest first. Open to candidates (no auth needed)."""
    jobs = db.scalars(
        select(Job).where(Job.status == "published").order_by(Job.created_at.desc())
    ).all()
    return [_job_to_stored(j) for j in jobs]


@router.get("/mine", response_model=list[StoredJob])
def list_my_jobs(
    db: Session = Depends(get_db),
    recruiter: User = Depends(require_recruiter),
) -> list[StoredJob]:
    """List jobs created by the currently authenticated recruiter."""
    jobs = db.scalars(
        select(Job).where(Job.recruiter_id == recruiter.id).order_by(Job.created_at.desc())
    ).all()
    return [_job_to_stored(j) for j in jobs]


@router.get("/{job_id}", response_model=StoredJob)
def get_job(job_id: str, db: Session = Depends(get_db)) -> StoredJob:
    """Fetch a single job by ID — used for the candidate job-detail view."""
    import uuid as _uuid
    job = db.scalar(select(Job).where(Job.id == _uuid.UUID(job_id)))
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return _job_to_stored(job)

