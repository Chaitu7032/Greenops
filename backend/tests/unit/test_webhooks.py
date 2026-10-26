import hmac
import hashlib
import json
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db
from app.core.config import settings

from app.main import app
from app.core.config import settings


def compute_signature(payload_bytes: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def test_webhook_hmac_verification_and_pr_ingestion(client):
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 12,
            "title": "feat: add user authentication",
            "head": {"sha": "c0ffee12345678", "ref": "feature/auth"},
            "user": {"login": "octocat"},
            "labels": [],
        },
        "repository": {
            "id": 100200,
            "name": "sample-repo",
            "full_name": "octo-org/sample-repo",
            "owner": {"login": "octo-org"},
        },
    }

    body = json.dumps(payload).encode("utf-8")
    sig = compute_signature(body, settings.GITHUB_WEBHOOK_SECRET)

    # 1. Send valid webhook
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": "delivery-uuid-001",
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json",
    }
    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "processed"
    assert res_data["policy_decision"] in ["APPROVED", "DEFERRED", "FLAGGED"]

    # 2. Replay the exact same delivery ID to verify idempotency
    response_replay = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response_replay.status_code == 200
    replay_data = response_replay.json()
    assert replay_data["status"] == "idempotent_skip"


def test_webhook_invalid_signature_rejected(client):
    body = b'{"action": "ping"}'
    headers = {
        "X-GitHub-Event": "ping",
        "X-GitHub-Delivery": "delivery-uuid-bad",
        "X-Hub-Signature-256": "sha256=invalidhexsignature000000000000000000",
    }
    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 401
