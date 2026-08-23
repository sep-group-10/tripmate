import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.base import Base
from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_db",
)


@pytest.fixture(scope="session")
def engine():
    """SQLAlchemy engine for the test database, created once per test
    session with all tables in place."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine):
    """Isolate each test in an outer transaction/savepoint that is always
    rolled back, even though route code calls session.commit() internally.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_local()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client wired to use the isolated db_session instead
    of a real database connection."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def existing_user(db_session):
    """A single pre-created user for tests that need a real account
    to log in as."""
    user = User(
        full_name="Existing User",
        email="existing@example.com",
        password_hash=hash_password("existingpassword123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    """A second user, distinct from existing_user, for tests that check
    one user's actions don't affect another user's account."""
    user = User(
        full_name="Other User",
        email="otheruser@example.com",
        password_hash=hash_password("otheruserpassword123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
