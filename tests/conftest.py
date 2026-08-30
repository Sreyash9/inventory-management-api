"""
Shared pytest fixtures.

Tests run against an in-memory SQLite database instead of PostgreSQL.
This is a deliberate design decision (documented in the README): it
keeps the test suite fast and dependency-free (no running Postgres
service required in CI or on a fresh machine), while the application
itself still targets PostgreSQL for real usage. SQLAlchemy's ORM layer
abstracts the dialect differences for the simple schema used here.

Each test function gets a fresh database (tables created, then dropped)
so tests are fully isolated from one another.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from main import app

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def category(client):
    """Creates a category and returns its JSON body."""
    response = client.post("/categories", json={"name": "Electronics"})
    assert response.status_code == 201
    return response.json()
