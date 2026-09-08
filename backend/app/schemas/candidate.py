"""Candidate profile schema — the public contract produced by the resume pipeline.

The AI Candidate Analysis Layer consumes ``CandidateProfile`` directly. All fields are
optional so a partial extraction never causes a hard failure; downstream modules
must handle ``None`` and empty lists gracefully.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ExperienceEntry(BaseModel):
    """A single work-experience entry extracted from a resume.

    All sub-fields are optional because resume formatting varies widely; the
    extractor fills what it can, the LLM layer enriches when available.
    """

    company: str | None = None
    title: str | None = None
    duration: str | None = None
    description: str | None = None


class CandidateProfile(BaseModel):
    """Structured, schema-validated representation of a candidate's resume.

    Produced exclusively by the resume pipeline (``app.resume``).

    Fields
    ------
    candidate_id
        UUID of the persisted ``Candidate`` row; ``None`` for ephemeral parse-only requests.
    name, email, phone
        Basic contact information.
    linkedin, github
        Social / professional profile URLs when present in the resume.
    summary
        Candidate's own summary / objective paragraph, if any.
    skills
        Flat list of recognised technical skills (de-duplicated).
    experience
        Total experience summary string (e.g., "1.8 years", "3 years", "0 years")
        consumed directly by the AI Candidate Analysis Layer (ComponentScorer).
    experience_entries
        Detailed work-experience entries (company, title, duration, description)
        for rich UI presentation and metadata storage.
    education
        Degree / institution strings.
    projects
        Project descriptions (one string per project).
    certifications
        Certification / award strings.
    """

    candidate_id: UUID | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    experience_entries: list[ExperienceEntry] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    @field_validator("experience", mode="before")
    @classmethod
    def _coerce_experience_input(cls, v: Any) -> str | None:
        """Provide minimal backward-compatibility if legacy code passes a list to experience."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            # If a list of ExperienceEntry/dicts was passed to `experience`,
            # extract the first duration string if available, or return None.
            for item in v:
                duration = None
                if isinstance(item, dict):
                    duration = item.get("duration")
                elif hasattr(item, "duration"):
                    duration = getattr(item, "duration")
                if duration and isinstance(duration, str):
                    return duration
            return None
        return str(v)
