"""Candidate profile schema — the public contract produced by the resume pipeline.

Person 1 (AI matching) consumes ``CandidateProfile`` directly.  All fields are
optional so a partial extraction never causes a hard failure; downstream modules
must handle ``None`` and empty lists gracefully.
"""

from uuid import UUID

from pydantic import BaseModel, Field


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

    Produced exclusively by the resume pipeline
    (``ResumeParser`` / ``app.services.resume_parser``).

    Fields
    ------
    candidate_id
        UUID of the persisted ``Candidate`` row; ``None`` for ephemeral
        parse-only requests (``POST /api/v1/resumes/parse``).
    name, email, phone
        Basic contact information.
    linkedin, github
        Social / professional profile URLs when present in the resume.
    summary
        Candidate's own summary / objective paragraph, if any.
    skills
        Flat list of recognised technical skills (de-duplicated).
    experience
        Ordered list of work-experience entries, newest first where detectable.
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
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
