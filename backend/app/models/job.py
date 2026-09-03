import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# JSONB on PostgreSQL for efficient querying/indexing; plain JSON everywhere
# else (e.g. SQLite in tests), so the same model works in both.
JSONVariant = JSON().with_variant(JSONB(), "postgresql")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # Basic info
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str] = mapped_column(Text)
    # Recruiter / company context
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Job card fields
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    experience_required: Mapped[str | None] = mapped_column(String(60), nullable=True)
    required_skills: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)
    preferred_skills: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)
    education: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)
    # AI-structured full profile
    structured_profile: Mapped[dict] = mapped_column(JSONVariant)
    # Publication status: draft | published
    status: Mapped[str] = mapped_column(String(20), default="published")
    # Nullable so existing rows created before auth was added stay valid;
    # new jobs are always created by an authenticated recruiter.
    recruiter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

