"""Internal schemas for the Resume Analysis module.

Defines the rich ``ResumeData`` model used internally by the Resume pipeline.
This model contains richer detailed information than the public ``CandidateProfile``.
"""

from typing import Literal
from pydantic import BaseModel, Field

from app.schemas.candidate import ExperienceEntry


class WorkExperience(BaseModel):
    """Detailed internal work-experience entry."""

    company: str | None = None
    role: str | None = None
    start_date: str | None = None  # e.g., "2024-08", "2024"
    end_date: str | None = None    # e.g., "2025-09", "present"
    duration_text: str | None = None
    description: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    """Detailed internal education entry."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_year: str | None = None
    cgpa_or_grade: str | None = None


class ProjectEntry(BaseModel):
    """Detailed internal project entry."""

    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    """Rich, detailed internal representation of parsed resume data.

    Produced by the hybrid Resume Analysis pipeline (deterministic + AI agent).
    Converted to the shared ``CandidateProfile`` via ``CandidateProfileAdapter``.
    """

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None

    skills: list[str] = Field(default_factory=list)

    work_experience: list[WorkExperience] = Field(default_factory=list)
    total_experience_years: float = 0.0

    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    analysis_method: Literal["hybrid", "deterministic_fallback"] = "deterministic_fallback"
