# GreenOps Quality Assurance & Testing Strategy

GreenOps enforces comprehensive testing across all calculation engines, webhook security, and database lifecycle flows.

## Test Matrix

| Layer | Target / Path | Coverage Scope |
|---|---|---|
| **Unit Tests: Mathematical Modeling** | `backend/tests/unit/test_engines.py` | Compute cost formula (Decimal), Power energy model (PUE, Watts, Utilization), Scope-2 Carbon gCO2e math, zero/negative inputs, CPU utilization bounds |
| **Unit Tests: PR Diff Analysis** | `backend/tests/unit/test_diff_analyzer.py` | Multi-language classification (source, test, integration, CI, infra, docs) |
| **Unit Tests: Policy Gatekeeper** | `backend/tests/unit/test_policy.py` | Hotfix urgency bypass, routine deferral on high carbon grid intensity, sprint budget exhaustion, single-run limits |
| **Unit Tests: Webhook Security** | `backend/tests/unit/test_webhooks.py` | HMAC-SHA256 signature validation, invalid signature 401 rejection, delivery ID idempotency |
| **Integration: End-to-End Lifecycle** | `backend/tests/integration/test_pipeline_flow.py` | Seed demo dataset -> PR webhook ingestion -> Policy decision -> Scorecard generation -> Workflow run completion -> Actual telemetry vs Estimate variance |

## Running the Automated Test Suite
```bash
cd backend
python -m pytest --cov=app tests/ -v
```
Current backend engine coverage: **>80%**.
