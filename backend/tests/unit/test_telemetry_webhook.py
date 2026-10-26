import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.repository import Repository
from app.models.sprint import Sprint
from app.models.pipeline_run import PipelineRun
from app.models.deferred_job import DeferredJob
from app.models.budget_ledger import SprintBudgetLedger
from app.models.webhook_event import WebhookEvent
from app.core.config import settings


def compute_sig(payload_bytes: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


@pytest.fixture
def telemetry_setup(db_session: Session):
    now = datetime.now(timezone.utc)
    org = Organization(name="Telemetry Org", monthly_budget_usd=Decimal("1000.00"))
    db_session.add(org)
    db_session.commit()

    sprint = Sprint(
        organization_id=org.id,
        name="Sprint 42",
        start_date=now - timedelta(days=2),
        end_date=now + timedelta(days=12),
        budget_usd=Decimal("200.00"),
        carbon_budget_kg=Decimal("10.00"),
        status="ACTIVE",
    )
    db_session.add(sprint)
    db_session.commit()

    repo = Repository(
        organization_id=org.id,
        github_repo_id=778899,
        owner="telemetry-owner",
        name="ci-repo",
        full_name="telemetry-owner/ci-repo",
        cost_per_minute=Decimal("0.008000"),
        runner_region="US-EAST",
    )
    db_session.add(repo)
    db_session.commit()

    return org, sprint, repo


def test_workflow_run_completion_telemetry_accepted_and_reconciled(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    # 1. Simulate prior PR estimate
    pipeline_run = PipelineRun(
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=sprint.id,
        pr_number=99,
        commit_sha="fedcba9876",
        workflow_name="CI",
        trigger_type="pull_request",
        estimated_duration_seconds=Decimal("150.00"),
        estimated_cost_usd=Decimal("0.0200"),
        estimated_energy_kwh=Decimal("0.0018"),
        estimated_carbon_g=Decimal("0.5400"),
        execution_status="PENDING",
    )
    db_session.add(pipeline_run)
    db_session.commit()

    # 2. Dispatch workflow_run.completed payload
    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 123456789,
            "name": "CI",
            "head_sha": "fedcba9876",
            "conclusion": "success",
            "run_started_at": "2026-10-12T10:00:00Z",
            "updated_at": "2026-10-12T10:03:00Z",  # 180 seconds elapsed
            "actor": {"login": "ci-bot"},
            "pull_requests": [{"number": 99}],
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)

    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-wf-001",
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json",
    }

    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "processed"
    assert res_data["pipeline_run_id"] == pipeline_run.id

    # 3. Verify Database Persistence & Actual Calculations
    db_session.refresh(pipeline_run)
    assert pipeline_run.execution_status == "COMPLETED"
    assert pipeline_run.run_id == 123456789
    assert pipeline_run.actual_duration_seconds == Decimal("180.00")
    # 180s = 3 minutes * $0.008 = $0.024
    assert pipeline_run.actual_cost_usd == Decimal("0.024000")
    assert pipeline_run.actual_carbon_g is not None


def test_workflow_run_failure_conclusion_persisted(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 999888777,
            "name": "CI",
            "head_sha": "failsha1234",
            "conclusion": "failure",
            "run_started_at": "2026-10-12T12:00:00Z",
            "updated_at": "2026-10-12T12:01:30Z",  # 90 seconds
            "actor": {"login": "developer"},
            "pull_requests": [],
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-wf-fail",
        "X-Hub-Signature-256": sig,
    }

    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200

    # Auto-created pipeline run has FAILED status
    run = db_session.query(PipelineRun).filter(PipelineRun.run_id == 999888777).first()
    assert run is not None
    assert run.execution_status == "FAILED"
    assert run.actual_duration_seconds == Decimal("90.00")


def test_deferred_job_marked_completed_when_workflow_run_completes(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    pipeline_run = PipelineRun(
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=sprint.id,
        pr_number=55,
        commit_sha="deferredsha99",
        workflow_name="CI",
        execution_status="DEFERRED",
    )
    db_session.add(pipeline_run)
    db_session.commit()

    deferred_job = DeferredJob(
        pipeline_run_id=pipeline_run.id,
        repository_id=repo.id,
        pr_number=55,
        workflow_name="CI",
        target_ref="main",
        scheduled_for=pipeline_run.created_at,
        reason="Carbon optimization",
        status="DISPATCHED",
    )
    db_session.add(deferred_job)
    db_session.commit()

    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 444333222,
            "name": "CI",
            "head_sha": "deferredsha99",
            "conclusion": "success",
            "run_started_at": "2026-10-12T14:00:00Z",
            "updated_at": "2026-10-12T14:02:00Z",
            "actor": {"login": "greenops-worker"},
            "pull_requests": [{"number": 55}],
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-wf-deferred",
        "X-Hub-Signature-256": sig,
    }

    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200

    db_session.refresh(deferred_job)
    assert deferred_job.status == "COMPLETED"


def test_duplicate_telemetry_webhook_is_idempotent(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 111222333,
            "name": "CI",
            "head_sha": "idempotentsha",
            "conclusion": "success",
            "run_started_at": "2026-10-12T15:00:00Z",
            "updated_at": "2026-10-12T15:01:00Z",
            "actor": {"login": "user"},
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-repeat-123",
        "X-Hub-Signature-256": sig,
    }

    # First delivery
    res1 = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"

    # Second delivery with exact same X-GitHub-Delivery
    res2 = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "idempotent_skip"


def test_unregistered_repository_telemetry_handled_safely(client, db_session: Session):
    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 7777777,
            "name": "CI",
            "head_sha": "unknownrepo",
            "conclusion": "success",
        },
        "repository": {
            "id": 9999999,
            "name": "unregistered",
            "full_name": "unknown-org/unregistered",
            "owner": {"login": "unknown-org"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-unknown-repo",
        "X-Hub-Signature-256": sig,
    }

    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    # Skipped gracefully without crashing or database foreign key errors
    assert data["pipeline_run_id"] is None


def test_cancelled_workflow_run_telemetry_persisted(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    pipeline_run = PipelineRun(
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=sprint.id,
        pr_number=77,
        commit_sha="cancelledsha",
        workflow_name="CI",
        execution_status="PENDING",
    )
    db_session.add(pipeline_run)
    db_session.commit()

    deferred_job = DeferredJob(
        pipeline_run_id=pipeline_run.id,
        repository_id=repo.id,
        pr_number=77,
        workflow_name="CI",
        target_ref="main",
        scheduled_for=pipeline_run.created_at,
        reason="Carbon delay",
        status="DISPATCHED",
    )
    db_session.add(deferred_job)
    db_session.commit()

    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 555666777,
            "name": "CI",
            "head_sha": "cancelledsha",
            "conclusion": "cancelled",
            "run_started_at": "2026-10-12T16:00:00Z",
            "updated_at": "2026-10-12T16:01:00Z",
            "actor": {"login": "ci-user"},
            "pull_requests": [{"number": 77}],
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-wf-cancelled",
        "X-Hub-Signature-256": sig,
    }

    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200

    db_session.refresh(pipeline_run)
    db_session.refresh(deferred_job)
    assert pipeline_run.execution_status == "CANCELLED"
    assert deferred_job.status == "CANCELLED"
    assert deferred_job.last_error == "Workflow run was cancelled on GitHub"


def test_duplicate_telemetry_different_delivery_ids_prevents_double_billing(client, db_session: Session, telemetry_setup):
    org, sprint, repo = telemetry_setup

    pipeline_run = PipelineRun(
        repository_id=repo.id,
        organization_id=org.id,
        sprint_id=sprint.id,
        pr_number=88,
        commit_sha="idempotent-sha88",
        workflow_name="CI",
        execution_status="PENDING",
    )
    db_session.add(pipeline_run)
    db_session.commit()

    payload = {
        "action": "completed",
        "workflow_run": {
            "id": 999111222,
            "name": "CI",
            "head_sha": "idempotent-sha88",
            "conclusion": "success",
            "run_started_at": "2026-10-12T17:00:00Z",
            "updated_at": "2026-10-12T17:02:00Z",  # 120 seconds
            "actor": {"login": "ci-bot"},
            "pull_requests": [{"number": 88}],
        },
        "repository": {
            "id": 778899,
            "name": "ci-repo",
            "full_name": "telemetry-owner/ci-repo",
            "owner": {"login": "telemetry-owner"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_sig(body, settings.GITHUB_WEBHOOK_SECRET)

    # First delivery via Action delivery ID
    headers1 = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-from-action-01",
        "X-Hub-Signature-256": sig,
    }
    res1 = client.post("/api/v1/webhooks/github", content=body, headers=headers1)
    assert res1.status_code == 200

    # Second delivery via Native GitHub webhook delivery ID
    headers2 = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-from-native-webhook-02",
        "X-Hub-Signature-256": sig,
    }
    res2 = client.post("/api/v1/webhooks/github", content=body, headers=headers2)
    assert res2.status_code == 200

    # Verify SprintBudgetLedger contains exactly ONE debit entry for this pipeline run
    entries = (
        db_session.query(SprintBudgetLedger)
        .filter(
            SprintBudgetLedger.sprint_id == sprint.id,
            SprintBudgetLedger.pipeline_run_id == pipeline_run.id,
            SprintBudgetLedger.entry_type == "ACTUAL_DEBIT",
        )
        .all()
    )
    assert len(entries) == 1
    # Cost for 120 seconds (2 minutes * $0.008000) = $0.016000
    assert entries[0].amount_usd == Decimal("0.016000")
