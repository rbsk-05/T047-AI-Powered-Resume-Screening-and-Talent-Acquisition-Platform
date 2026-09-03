from typing import Literal

from pydantic import BaseModel

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile


class SkillGapRequest(BaseModel):
    job_profile: JobProfile
    candidate_profile: CandidateProfile


class SkillGap(BaseModel):
    skill: str
    priority: Literal["critical", "important"]
    reason: str


class SkillGapResult(BaseModel):
    matched_skills: list[str]
    gaps: list[SkillGap]
