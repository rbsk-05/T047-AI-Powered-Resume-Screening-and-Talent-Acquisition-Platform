from enum import Enum
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    EXPLICIT = "EXPLICIT"
    INFERRED = "INFERRED"
    UNSPECIFIED = "UNSPECIFIED"


class RequirementImportance(str, Enum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequirementStatus(str, Enum):
    KNOWN = "KNOWN"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class JobRequirement(BaseModel):
    name: str
    normalized_name: str
    category: str = "Technology"
    importance: RequirementImportance = RequirementImportance.REQUIRED
    evidence_type: EvidenceType = EvidenceType.EXPLICIT
    evidence_text: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    status: RequirementStatus = RequirementStatus.KNOWN


class JobCreateRequest(BaseModel):
    """Full job creation form — submitted by the recruiter."""
    job_title: str = Field(min_length=2, max_length=160)
    job_description: str = Field(min_length=30, max_length=20_000)
    company_name: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=120)
    employment_type: str = Field(default="", max_length=60)
    experience_required: str = Field(default="", max_length=60)
    job_family: str = Field(default="")
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)


# Keep backward-compat alias used by /jobs/analyze
JobDescriptionAnalysisRequest = JobCreateRequest


class JobProfile(BaseModel):
    """AI-extracted structured profile from a job description with context awareness and ontology."""
    job_title: str
    job_family: str = "General Engineering"
    technology_specified: bool = True
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    education: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    domain_knowledge: list[str] = Field(default_factory=list)



