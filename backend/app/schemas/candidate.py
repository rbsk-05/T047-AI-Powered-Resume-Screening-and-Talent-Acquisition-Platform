from enum import Enum
from pydantic import BaseModel, Field


class CandidateSkillEvidence(str, Enum):
    EXPLICIT = "EXPLICIT"
    INFERRED = "INFERRED"


class CandidateSkill(BaseModel):
    skill_name: str
    normalized_name: str
    evidence_text: str = ""
    evidence_type: CandidateSkillEvidence = CandidateSkillEvidence.EXPLICIT
    confidence: str = "HIGH"


class CandidateProfile(BaseModel):
    name: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    structured_skills: list[CandidateSkill] = Field(default_factory=list)
    experience: str | None = None
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    domain_knowledge: list[str] = Field(default_factory=list)


