"""Resume ingestion API routes.

All routes live under ``/api/v1/resumes`` (prefix applied in ``main.py``).

Route summary
-------------
POST  /parse              – ephemeral parse, no DB write, no auth required
POST  /                   – parse + persist (candidate accounts only)
GET   /                   – list stored candidates (own records for candidates,
                            all records for recruiters)
GET   /{candidate_id}     – fetch a single stored candidate profile by ID
DELETE /{candidate_id}    – remove a candidate's own stored resume
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_candidate
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.candidate import CandidateProfile
from app.schemas.records import StoredCandidate
from app.services.resume_parser import ResumeParser

router = APIRouter(prefix="/resumes", tags=["resumes"])
parser = ResumeParser()

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _read_upload(file: UploadFile, content: bytes) -> None:
    """Shared guard: reject missing filename and oversized payloads."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A resume file is required.",
        )
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume files must be 10 MB or smaller.",
        )


# ---------------------------------------------------------------------------
# POST /parse  — ephemeral, no authentication required
# ---------------------------------------------------------------------------

@router.post("/parse", response_model=CandidateProfile)
async def parse_resume(file: UploadFile = File(...)) -> CandidateProfile:
    """Extract a structured candidate profile from a PDF or DOCX resume.

    No authentication is required and nothing is persisted.  The ``candidate_id``
    field in the response will always be ``null`` for this endpoint.
    """
    content = await file.read()
    _read_upload(file, content)
    try:
        return parser.parse(file.filename, content)  # type: ignore[arg-type]
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


# ---------------------------------------------------------------------------
# POST /  — parse + persist (candidate accounts only)
# ---------------------------------------------------------------------------

@router.post("", response_model=StoredCandidate, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate_user: User = Depends(require_candidate),
) -> StoredCandidate:
    """Parse and persist a resume, returning a ``StoredCandidate``.

    Restricted to candidate accounts.  The uploaded resume is linked to the
    authenticated user so each candidate owns only their own records.
    The ``candidate_id`` field in the returned ``CandidateProfile`` is populated
    with the newly created database row ID.
    """
    content = await file.read()
    _read_upload(file, content)
    try:
        text = parser.extract_text(file.filename, content)  # type: ignore[arg-type]
        profile = parser.parse_text(text)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    candidate = Candidate(
        name=profile.name,
        email=profile.email,
        resume_filename=file.filename,
        resume_text=text,
        structured_profile=profile.model_dump(mode="json"),
        candidate_user_id=candidate_user.id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Populate candidate_id now that the DB row exists
    profile_with_id = profile.model_copy(update={"candidate_id": candidate.id})
    # Persist the updated profile (with candidate_id) back to the DB
    candidate.structured_profile = profile_with_id.model_dump(mode="json")
    db.commit()

    return StoredCandidate(
        id=candidate.id,
        profile=profile_with_id,
        resume_filename=candidate.resume_filename,
        created_at=candidate.created_at,
    )


# ---------------------------------------------------------------------------
# GET /  — list (role-aware)
# ---------------------------------------------------------------------------

@router.get("", response_model=list[StoredCandidate])
def list_candidates(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[StoredCandidate]:
    """List stored candidate profiles, newest first.

    * **Candidates** see only their own resumes.
    * **Recruiters** see all candidates (needed for evaluation / matching).
    """
    query = select(Candidate).order_by(Candidate.created_at.desc())
    if user.role == "candidate":
        query = query.where(Candidate.candidate_user_id == user.id)
    candidates = db.scalars(query).all()
    return [
        StoredCandidate(
            id=candidate.id,
            profile=CandidateProfile.model_validate(candidate.structured_profile),
            resume_filename=candidate.resume_filename,
            created_at=candidate.created_at,
        )
        for candidate in candidates
    ]


# ---------------------------------------------------------------------------
# GET /{candidate_id}  — fetch single
# ---------------------------------------------------------------------------

@router.get("/{candidate_id}", response_model=StoredCandidate)
def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StoredCandidate:
    """Fetch a single stored candidate profile by its UUID.

    * **Candidates** may only access their own records.
    * **Recruiters** may access any candidate's profile.

    Returns ``404`` if the candidate does not exist, ``403`` if the requesting
    candidate tries to access someone else's record.
    """
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )
    if user.role == "candidate" and candidate.candidate_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this candidate's profile.",
        )
    return StoredCandidate(
        id=candidate.id,
        profile=CandidateProfile.model_validate(candidate.structured_profile),
        resume_filename=candidate.resume_filename,
        created_at=candidate.created_at,
    )


# ---------------------------------------------------------------------------
# DELETE /{candidate_id}  — remove own record
# ---------------------------------------------------------------------------

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    candidate_user: User = Depends(require_candidate),
) -> None:
    """Delete a candidate's stored resume and profile.

    Restricted to candidate accounts.  Candidates may only delete their own
    records; attempting to delete another user's record returns ``403``.
    """
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )
    if candidate.candidate_user_id != candidate_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only delete your own resume.",
        )
    db.delete(candidate)
    db.commit()
