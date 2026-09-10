from app.db.base import Base
import app.models  # noqa: F401


def test_database_schema_contains_core_entities() -> None:
    assert set(Base.metadata.tables) == {"jobs", "candidates", "applications", "users", "companies"}
