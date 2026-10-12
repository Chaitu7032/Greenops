import json
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db
from app.models import Organization, Repository, Sprint, PipelineRun, SprintBudgetLedger
from app.core.config import settings
from app.core.security import verify_github_signature

from app.main import app
from app.models import Organization, Repository, Sprint, PipelineRun, SprintBudgetLedger
from app.core.config import settings
from app.core.security import verify_github_signature


def test_full_pipeline_end_to_end_flow(client):
    # 1. Trigger Seed Endpoint
    seed_res = client.post("/api/v1/demo/seed")
    assert seed_res.status_code == 201
    assert seed_res.json()["status"] == "seeded"

    # 2. Query Dashboard Overview
    dash_res = client.get("/api/v1/dashboard/overview")
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert dash["total_runs_count"] > 0
    assert float(dash["financial_budget_usd"]) > 0

    # 3. Simulate Incoming Pull Request Webhook
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "number": 99,
            "title": "[HOTFIX] Critical patch for auth token expiry",
            "head": {"sha": "99feedbeef0011", "ref": "hotfix/auth-patch"},
            "user": {"login": "devops-lead"},
            "labels": [{"name": "hotfix"}],
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }

    import hmac, hashlib
    body_bytes = json.dumps(pr_payload).encode("utf-8")
    mac = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"), msg=body_bytes, digestmod=hashlib.sha256)
    sig = f"sha256={mac.hexdigest()}"

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": "delivery-e2e-001",
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json",
    }
    pr_res = client.post("/api/v1/webhooks/github", content=body_bytes, headers=headers)
    assert pr_res.status_code == 200
    pr_data = pr_res.json()
    assert pr_data["policy_decision"] == "APPROVED"
    assert "Hotfix" in pr_data["reason"]

    # 4. Simulate workflow_run completed webhook
    wf_payload = {
        "action": "completed",
        "workflow_run": {
            "id": 88776655,
            "name": "CI",
            "head_sha": "99feedbeef0011",
            "conclusion": "success",
            "created_at": "2026-09-08T10:00:00Z",
            "run_started_at": "2026-09-08T10:00:00Z",
            "updated_at": "2026-09-08T10:03:30Z",  # 210 seconds duration
            "actor": {"login": "devops-lead"},
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }

    wf_bytes = json.dumps(wf_payload).encode("utf-8")
    wf_sig = f"sha256={hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'), msg=wf_bytes, digestmod=hashlib.sha256).hexdigest()}"
    wf_headers = {
        "X-GitHub-Event": "workflow_run",
        "X-GitHub-Delivery": "delivery-e2e-002",
        "X-Hub-Signature-256": wf_sig,
        "Content-Type": "application/json",
    }
    wf_res = client.post("/api/v1/webhooks/github", content=wf_bytes, headers=wf_headers)
    assert wf_res.status_code == 200

    # 5. Verify Pipeline list endpoint returns variance metrics
    pipes_res = client.get("/api/v1/pipelines")
    assert pipes_res.status_code == 200
    pipelines_list = pipes_res.json()
    matched = next((p for p in pipelines_list if p["commit_sha"] == "99feedbeef0011"), None)
    assert matched is not None
    assert float(matched["actual_duration_seconds"]) == 210.0
    assert matched["duration_variance_seconds"] is not None
    assert matched["execution_status"] == "COMPLETED"

    # 6. Verify Sprint Burn-Down chart is generated
    sprints_res = client.get("/api/v1/sprints")
    assert sprints_res.status_code == 200
    active_sprint = next(s for s in sprints_res.json() if s["status"] == "ACTIVE")
    burn_res = client.get(f"/api/v1/sprints/{active_sprint['id']}/burn-down")
    assert burn_res.status_code == 200
    assert len(burn_res.json()) > 0
