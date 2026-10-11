from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import Organization, Repository, Sprint, Policy
from app.services.policy_engine import evaluate_policy_gatekeeper


def setup_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    org = Organization(name="Test Org", monthly_budget_usd=Decimal("500.00"), carbon_budget_kg=Decimal("100.00"))
    db.add(org)
    db.commit()

    repo = Repository(
        organization_id=org.id,
        github_repo_id=999,
        owner="test-org",
        name="test-repo",
        full_name="test-org/test-repo",
    )
    db.add(repo)
    db.commit()

    policy = Policy(
        organization_id=org.id,
        repository_id=repo.id,
        max_cost_per_run_usd=Decimal("1.0000"),
        max_carbon_per_run_g=Decimal("200.00"),
        high_grid_intensity_threshold=Decimal("350.00"),
        allow_deferred_execution=True,
    )
    db.add(policy)
    db.commit()

    return db, org, repo, policy


def test_policy_hotfix_bypass():
    db, org, repo, policy = setup_test_db()
    # High grid intensity (450 gCO2e) during a hotfix should still be APPROVED
    res = evaluate_policy_gatekeeper(
        db=db,
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=None,
        estimated_cost_usd=Decimal("0.5000"),
        estimated_carbon_g=Decimal("150.00"),
        grid_intensity_gco2_kwh=Decimal("450.00"),
        urgency="HOTFIX",
    )
    assert res.decision == "APPROVED"
    assert "Hotfix priority override" in res.reason


def test_policy_routine_high_grid_deferred():
    db, org, repo, policy = setup_test_db()
    # High grid intensity (400 > threshold 350) on routine PR should be DEFERRED
    res = evaluate_policy_gatekeeper(
        db=db,
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=None,
        estimated_cost_usd=Decimal("0.1000"),
        estimated_carbon_g=Decimal("50.00"),
        grid_intensity_gco2_kwh=Decimal("400.00"),
        urgency="ROUTINE",
    )
    assert res.decision == "DEFERRED"
    assert res.can_defer is True
    assert "exceeds green threshold" in res.reason


def test_policy_single_run_carbon_limit_flagged():
    db, org, repo, policy = setup_test_db()
    # Carbon footprint 250g > max 200g should be FLAGGED
    res = evaluate_policy_gatekeeper(
        db=db,
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=None,
        estimated_cost_usd=Decimal("0.2000"),
        estimated_carbon_g=Decimal("250.00"),
        grid_intensity_gco2_kwh=Decimal("200.00"),
        urgency="ROUTINE",
    )
    assert res.decision == "FLAGGED"
    assert res.rule_violated == "MAX_SINGLE_RUN_CARBON_EXCEEDED"
