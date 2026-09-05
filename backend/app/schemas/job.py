from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    """Full job creation form — submitted by the recruiter."""
    job_title: str = Field(min_length=2, max_length=160)
    job_description: str = Field(min_length=30, max_length=20_000)
    company_name: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=120)
    employment_type: str = Field(default="", max_length=60)
    experience_required: str = Field(default="", max_length=60)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)


# Keep backward-compat alias used by /jobs/analyze
JobDescriptionAnalysisRequest = JobCreateRequest


class JobProfile(BaseModel):
    """AI-extracted structured profile from a job description."""
    job_title: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    education: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
