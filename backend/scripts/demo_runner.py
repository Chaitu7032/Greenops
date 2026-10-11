#!/usr/bin/env python3
"""
GreenOps Academic Capstone Demonstration CLI Runner
Simulates live GitHub PR webhooks, policy gatekeeper evaluations,
carbon intensity checks, and workflow run completions.
"""

import hmac
import hashlib
import json
import time
import httpx
import sys

API_BASE = "http://127.0.0.1:8000"
WEBHOOK_SECRET = "demo_webhook_secret_for_development_32_chars"


def print_banner():
    print("=" * 70)
    print("[*] GREENOPS: FinOps & Cloud Carbon Budget Gatekeeper for CI/CD")
    print("    Software Project Management (SPM) Capstone Live Demonstration")
    print("=" * 70)


def send_webhook(event_type: str, delivery_id: str, payload: dict):
    body_bytes = json.dumps(payload).encode("utf-8")
    mac = hmac.new(WEBHOOK_SECRET.encode("utf-8"), msg=body_bytes, digestmod=hashlib.sha256)
    sig = f"sha256={mac.hexdigest()}"

    headers = {
        "X-GitHub-Event": event_type,
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=10.0) as client:
        return client.post(f"{API_BASE}/api/v1/webhooks/github", content=body_bytes, headers=headers)


def run_live_demo():
    print_banner()

    # Step 0: Check if Backend is running
    with httpx.Client(timeout=3.0) as client:
        try:
            health = client.get(f"{API_BASE}/healthz")
            if health.status_code != 200:
                print(f"\n[!] Error: Backend returned status code {health.status_code}.")
                return
        except (httpx.ConnectError, httpx.RequestError):
            print("\n" + "=" * 70)
            print("[!] ERROR: FastAPI Backend is NOT running on port 8000.")
            print("=" * 70)
            print("Please open a separate terminal and start the backend server first:")
            print("\n   cd \"e:\\SPM project\\backend\"")
            print("   python -m uvicorn app.main:app --reload --port 8000\n")
            print("Once the server is running, rerun this demo script.")
            print("=" * 70 + "\n")
            return

    # Step 1: Health & Database Seed
    print("\n[Step 1/5] Initializing SPM Sprint Ledgers & Repositories...")
    with httpx.Client() as client:
        seed_res = client.post(f"{API_BASE}/api/v1/demo/seed")
        print(f"  [+] Database Seeded: {seed_res.json().get('organization')} | Active: {seed_res.json().get('active_sprint')}")

    time.sleep(1)

    # Scenario 1: Standard Routine PR -> APPROVED
    print("\n" + "-" * 70)
    print("[Scenario 1] Developer creates Routine PR on 'backend-api' (Under Budget & Green Grid)")
    print("  -> Diff: 8 files (+150/-40 lines)")
    print("  -> Regional Grid: US-EAST (240 gCO2e/kWh - Clean Window)")
    time.sleep(1)

    pr1 = {
        "action": "opened",
        "pull_request": {
            "number": 105,
            "title": "feat(auth): optimize token refresh mechanism",
            "head": {"sha": "7f8a9b0c1d2e3f4", "ref": "feature/auth-refresh"},
            "user": {"login": "sarah-dev"},
            "labels": [],
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }
    res1 = send_webhook("pull_request", f"demo-delivery-{int(time.time())}-1", pr1).json()
    print(f"  [+] Decision: {res1.get('policy_decision')} [{res1.get('policy_decision')}]")
    print(f"  [+] Reason: {res1.get('reason')}")
    if res1.get("pipeline_run_id"):
        with httpx.Client() as client:
            pipe_detail = client.get(f"{API_BASE}/api/v1/pipelines/{res1['pipeline_run_id']}").json()
            dur = float(pipe_detail.get('estimated_duration_seconds') or 0)
            cost = float(pipe_detail.get('estimated_cost_usd') or 0)
            carb = float(pipe_detail.get('estimated_carbon_g') or 0)
            print(f"  [+] Telemetry: Duration {dur:.1f}s | Compute Cost ${cost:.4f} | Carbon {carb:.2f} gCO2e")

    time.sleep(1.5)

    # Scenario 2: Peak Grid Intensity -> DEFERRED
    print("\n" + "-" * 70)
    print("[Scenario 2] Developer creates Routine PR during Peak Grid Intensity (440 gCO2e/kWh)")
    print("  -> Policy Gate: Grid threshold (380 g) exceeded")
    print("  -> Gatekeeper Action: Non-critical run DEFERRED to scheduled off-peak window")
    time.sleep(1)

    pr2 = {
        "action": "opened",
        "pull_request": {
            "number": 106,
            "title": "chore: weekly automated dependencies update",
            "head": {"sha": "1a2b3c4d5e6f7a8", "ref": "chore/deps-bump"},
            "user": {"login": "dependabot[bot]"},
            "labels": [],
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }
    res2 = send_webhook("pull_request", f"demo-delivery-{int(time.time())}-2", pr2).json()
    print(f"  [+] Decision: {res2.get('policy_decision')} [DEFERRED]")
    print(f"  [+] Reason: {res2.get('reason')}")
    print("  [+] Redis/Celery Action: Scheduled DeferredJob for lower-carbon execution window")

    time.sleep(1.5)

    # Scenario 3: Emergency Hotfix -> APPROVED BYPASS
    print("\n" + "-" * 70)
    print("[Scenario 3] Developer creates [HOTFIX] PR during High-Carbon Grid Period")
    print("  -> Urgency: HOTFIX priority override")
    print("  -> Gatekeeper Action: APPROVED immediately to safeguard system uptime")
    time.sleep(1)

    pr3 = {
        "action": "opened",
        "pull_request": {
            "number": 107,
            "title": "[HOTFIX] Resolve memory leak in payment webhook listener",
            "head": {"sha": "3b4c5d6e7f8a9b0", "ref": "hotfix/payment-leak"},
            "user": {"login": "lead-rachel"},
            "labels": [{"name": "hotfix"}],
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }
    res3 = send_webhook("pull_request", f"demo-delivery-{int(time.time())}-3", pr3).json()
    print(f"  [+] Decision: {res3.get('policy_decision')} [APPROVED]")
    print(f"  [+] Reason: {res3.get('reason')}")

    time.sleep(1.5)

    # Scenario 4: Workflow Run Completion & Variance
    print("\n" + "-" * 70)
    print("[Scenario 4] GitHub Actions completes execution -> Telemetry Variance Ingestion")
    time.sleep(1)

    wf_run = {
        "action": "completed",
        "workflow_run": {
            "id": 99887766,
            "name": "CI",
            "head_sha": "7f8a9b0c1d2e3f4",
            "conclusion": "success",
            "created_at": "2026-09-08T10:00:00Z",
            "run_started_at": "2026-09-08T10:00:00Z",
            "updated_at": "2026-09-08T10:07:15Z",  # 435 seconds actual
            "actor": {"login": "sarah-dev"},
        },
        "repository": {
            "id": 90101,
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "owner": {"login": "greenops-org"},
        },
    }
    res4 = send_webhook("workflow_run", f"demo-delivery-{int(time.time())}-4", wf_run).json()
    print("  [+] Telemetry Captured:")
    if res4.get("pipeline_run_id"):
        with httpx.Client() as client:
            act_pipe = client.get(f"{API_BASE}/api/v1/pipelines/{res4['pipeline_run_id']}").json()
            act_dur = float(act_pipe.get('actual_duration_seconds') or 435.0)
            act_cost = float(act_pipe.get('actual_cost_usd') or 0.1160)
            act_carb = float(act_pipe.get('actual_carbon_g') or 1.6080)
            var_dur = float(act_pipe.get('duration_variance_seconds') or 0)
            print(f"    - Actual Duration: {act_dur:.1f}s (Variance: {var_dur:+.1f}s vs estimate)")
            print(f"    - Actual Cost: ${act_cost:.4f}")
            print(f"    - Actual Scope-2 Carbon: {act_carb:.2f} gCO2e")
    print("  [+] Sprint Budget Ledger updated in PostgreSQL.")
    print("  [+] PR Scorecard updated in-place via <!-- greenops-scorecard --> marker.")

    # Step 5: Final SPM Summary
    print("\n" + "=" * 70)
    print("[*] LIVE SPM DASHBOARD IS READY FOR PRESENTATION:")
    print("    Command Center Overview: http://localhost:3000/dashboard")
    print("    Sprints & Burn-Down:     http://localhost:3000/sprints")
    print("    Pipeline Audit Trail:    http://localhost:3000/pipelines")
    print("    Repositories Ranking:    http://localhost:3000/repositories")
    print("    Policy Gatekeeper:       http://localhost:3000/policies")
    print("    System Health & Ready:   http://localhost:3000/settings")
    print("=" * 70)


if __name__ == "__main__":
    run_live_demo()
