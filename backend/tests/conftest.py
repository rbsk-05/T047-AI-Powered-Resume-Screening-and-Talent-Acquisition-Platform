import os

# Default to a local sqlite file for tests when no DATABASE_URL is set, so
# `pytest` works standalone without requiring PostgreSQL. If DATABASE_URL is
# already set (e.g. CI pointing at a real Postgres instance), that's
# respected instead.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest

import app.models  # noqa: F401 - registers model metadata
from app.db.base import Base
from app.db.session import engine


@pytest.fixture(autouse=True, scope="session")
def _create_tables():
    Base.metadata.create_all(bind=engine)
    yield
