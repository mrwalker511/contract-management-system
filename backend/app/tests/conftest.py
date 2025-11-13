"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..main import app
from ..core.database import Base, get_db
from ..core.security import get_password_hash
from ..models.user import User, UserRole

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with overridden database"""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Disable startup events for testing
    app.router.on_startup = []

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        role=UserRole.PROCUREMENT,
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_legal_user(db_session):
    """Create a test legal user"""
    user = User(
        email="legal@example.com",
        full_name="Legal User",
        role=UserRole.LEGAL,
        hashed_password=get_password_hash("legalpass123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user"""
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        hashed_password=get_password_hash("adminpass123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def legal_auth_headers(client, test_legal_user):
    """Get authentication headers for legal user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "legal@example.com", "password": "legalpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, test_admin_user):
    """Get authentication headers for admin user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
