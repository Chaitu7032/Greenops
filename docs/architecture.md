# GreenOps System Architecture

## Overview
GreenOps operates as an asynchronous, event-driven middleware connecting GitHub pull requests, cloud compute infrastructure, regional power grid carbon intensity datasets, and Software Project Management (SPM) sprint ledgers.

## High-Level Pipeline Flow
```
Developer Pull Request
  │ (Webhook Event: pull_request)
  ▼
GitHub Webhook Gateway (FastAPI)
  ├── HMAC-SHA256 Signature Verification
  └── Idempotency Guard (X-GitHub-Delivery)
  ▼
PR Diff Analyzer & File Classifier
  ▼
CI Duration Estimator (Historical Median or Deterministic Heuristic)
  ▼
FinOps Cost Engine (Decimal precision)
  ▼
Energy Engine (PUE, Server Idle/Max Watts, CPU Utilization)
  ▼
Grid Carbon Service (Electricity Maps API / Redis 60m TTL Cache)
  ▼
Scope-2 Carbon Engine (gCO2e)
  ▼
SPM Sprint Budget Ledger
  ▼
Policy Gatekeeper
  ├── APPROVED  -> GitHub Workflow Execution + Scorecard Comment
  ├── DEFERRED  -> Redis/Celery Queue -> Lower Carbon Window Dispatch
  └── FLAGGED   -> PR Warning + Lead Approval Required
  ▼
Telemetry Capture & Variance (workflow_run completion)
  ▼
PostgreSQL / Next.js 14 SPM Dashboard
```

## Architectural Invariants
1. **Authoritative Backend**: All mathematical modeling, FinOps calculations, and gatekeeper decisions occur server-side in Python.
2. **Idempotent Ingestion**: Every GitHub delivery ID is tracked in `webhook_events` to prevent duplicated executions.
3. **No Machine Learning in MVP**: Deterministic heuristics and historical medians are used for clear explainability.
4. **Distinction of Estimated vs Actual**: Telemetry cleanly differentiates estimated pre-run predictions from post-run actuals to calculate estimator variance.
