import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db
from app.models import Organization, Repository, Sprint, PipelineRun, Policy, WebhookEvent

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "degraded"]
    assert response.json()["database"] is True


def test_model_instantiation():
    db = TestingSessionLocal()
    org = Organization(name="Acme Corp")
    db.add(org)
    db.commit()
    db.refresh(org)

    assert org.id is not None
    assert org.name == "Acme Corp"
    assert org.monthly_budget_usd == Decimal("500.0000")

    repo = Repository(
        organization_id=org.id,
        github_repo_id=123456,
        owner="acme",
        name="backend",
        full_name="acme/backend",
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    assert repo.id is not None
    assert repo.full_name == "acme/backend"
    assert repo.cost_per_minute == Decimal("0.008000")

    db.close()
