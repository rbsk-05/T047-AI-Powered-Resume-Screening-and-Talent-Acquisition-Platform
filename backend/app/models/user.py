import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """A recruiter or candidate account.

    Role is a plain string with a database-level check constraint rather
    than a Python enum -- this keeps the migration path simple (no enum
    type to alter later) while still rejecting bad values at the database
    layer, not just in application code.
    """

    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('recruiter', 'candidate')", name="users_role_check"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(20))
    # Recruiter-only fields (null for candidates)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    company_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
