import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app import models  # noqa: F401 - registers models on Base.metadata


@pytest.fixture
def db_session():
    """Fresh in-memory SQLite DB per test, fully isolated, no LLM calls."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user(db_session):
    from app.memory_service import get_or_create_user
    return get_or_create_user(db_session, "Test User")