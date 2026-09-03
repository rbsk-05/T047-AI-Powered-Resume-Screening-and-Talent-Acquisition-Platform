from pydantic import BaseModel


class CandidateProfile(BaseModel):
    name: str | None
    email: str | None
    phone: str | None
    skills: list[str]
    experience: str | None
    education: list[str]
    projects: list[str]
    certifications: list[str]
