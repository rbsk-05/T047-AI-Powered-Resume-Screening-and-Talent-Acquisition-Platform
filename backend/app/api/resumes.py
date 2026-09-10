from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.resume_agent import ResumeAgent
from app.api.deps import get_current_user, require_candidate
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.candidate import CandidateProfile
from app.schemas.records import StoredCandidate

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_agent = ResumeAgent()


@router.post("/parse", response_model=CandidateProfile)
async def parse_resume(file: UploadFile = File(...)) -> CandidateProfile:
    """Extract a structured candidate profile from a PDF or DOCX resume."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="A resume file is required.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume files must be 10 MB or smaller.")
    try:
        return resume_agent.process(file.filename, content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("", response_model=StoredCandidate, status_code=201)
async def create_candidate(file: UploadFile = File(...), db: Session = Depends(get_db), candidate_user: User = Depends(require_candidate)) -> StoredCandidate:
    """Parse and persist a resume, retaining its extracted text and profile.

    Restricted to candidate accounts and tied to the uploading user, so a
    candidate's own resumes stay theirs.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="A resume file is required.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume files must be 10 MB or smaller.")
    try:
        text = resume_agent.parser.extract_text(file.filename, content)
        profile = resume_agent.process_text(text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    candidate = Candidate(
        name=profile.name,
        email=profile.email,
        resume_filename=file.filename,
        resume_text=text,
        structured_profile=profile.model_dump(),
        candidate_user_id=candidate_user.id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return StoredCandidate(id=candidate.id, profile=profile, resume_filename=candidate.resume_filename, created_at=candidate.created_at)


@router.get("", response_model=list[StoredCandidate])
def list_candidates(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[StoredCandidate]:
    """List stored candidate profiles, newest first.

    Candidates see only their own resumes; recruiters see all candidates,
    since they need to evaluate applicants.
    """
    query = select(Candidate).order_by(Candidate.created_at.desc())
    if user.role == "candidate":
        query = query.where(Candidate.candidate_user_id == user.id)
    candidates = db.scalars(query).all()
    return [StoredCandidate(id=candidate.id, profile=CandidateProfile.model_validate(candidate.structured_profile), resume_filename=candidate.resume_filename, created_at=candidate.created_at) for candidate in candidates]
