from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    company_name: str
    description: str | None = None
    location: str | None = None
    website: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    description: str | None = None
    location: str | None = None
    website: str | None = None


class CompanyOut(CompanyBase):
    id: UUID
    recruiter_id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
