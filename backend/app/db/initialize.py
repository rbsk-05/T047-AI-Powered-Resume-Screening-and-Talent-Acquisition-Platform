"""Run with: python -m app.db.initialize after PostgreSQL is configured."""

from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401 - imports model metadata


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("TalentLens AI database tables created.")


if __name__ == "__main__":
    main()
