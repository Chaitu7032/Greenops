# GreenOps System Architecture & Design Specification

GreenOps is an asynchronous, event-driven middleware connecting GitHub pull requests, cloud compute runners, regional power grid carbon intensity datasets, and Software Project Management (SPM) sprint accounting ledgers.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph GitHub[GitHub Ecosystem]
        PR[Developer Pull Request]
        Action[GreenOps Composite Action]
        Runner[GitHub Actions Runner]
    end

    subgraph Gateway[Ingestion & Security Tier]
        WH[FastAPI Webhook Gateway /webhooks/github]
        Auth[HMAC-SHA256 Auth & Idempotency Guard]
    end

    subgraph Engines[Analytical Modeling Tier]
        Diff[PR Diff & File Classifier]
        Dur[CI Duration Estimator - Historical & Heuristic]
        Cost[FinOps Cost Engine - Decimal Precision]
        Energy[Server Power Engine - PUE & TDP Model]
        Grid[Grid Carbon Service - Electricity Maps & Redis]
        Carbon[Scope-2 Carbon Engine - gCO2e]
    end

    subgraph Governance[Policy & Accounting Tier]
        Policy[Deterministic Policy Gatekeeper]
        Ledger[SPM Sprint Budget Ledger]
    end

    subgraph Execution[Background Dispatch Tier]
        Redis[(Redis Queue)]
        Celery[Celery Beat & Worker]
        Dispatch[Atomic CAS Job Claim & REST Dispatcher]
    end

    subgraph Storage[Data & Persistence Tier]
        DB[(PostgreSQL - Alembic Migrations c341c4aec7e3)]
    end

    subgraph UI[Presentation & Analytics Tier]
        Next[Next.js 14 SPM Command Center]
        PR_Comment[In-Place PR Scorecard Comment]
    end

    %% Flow connections
    PR -->|pull_request event| WH
    WH --> Auth
    Auth --> Diff
    Diff --> Dur --> Cost --> Energy --> Grid --> Carbon
    Carbon --> Policy
    Policy --> Ledger

    Policy -->|APPROVED| Runner
    Policy -->|DEFERRED| DB
    Policy -->|FLAGGED| PR_Comment

    DB --> Celery
    Celery --> Redis
    Redis --> Dispatch
    Dispatch -->|workflow_dispatch| Runner

    Runner --> Action
    Action -->|workflow_run.completed telemetry| WH
    WH -->|Reconcile actuals & debit ledger| DB
    DB --> PR_Comment
    DB --> Next
```

---

## 2. Core Architectural Pillars & Invariants

### 1. Shift-Left FinOps & Carbon Governance
Traditional FinOps is retrospective—organizations discover cloud waste weeks after billing cycles close. GreenOps moves governance left into the pre-merge pull-request lifecycle. By evaluating resource consumption against active sprint budgets before code merges, runaway pipeline expenditure is prevented.

### 2. Explainable Deterministic Modeling
GreenOps intentionally avoids black-box machine learning for baseline estimations:
- **Duration**: Combines historical median durations for identical repository workflows with deterministic heuristic multipliers based on file categorization (source, unit tests, integration tests, CI configuration).
- **Compute Cost**: High-precision Python `Decimal` arithmetic using exact runner pricing per minute.
- **Server Power**: Cloud server TDP modeling with baseline idle wattage ($10\text{W}$), peak wattage ($50\text{W}$), estimated CPU utilization ($70\%$), and data center PUE ($1.15$).
- **Carbon Emissions**: Scope-2 emissions calculated using live or cached regional grid carbon intensity ($\text{gCO}_2\text{e}/\text{kWh}$).

### 3. Dual-Tier Idempotency Architecture
Network failures and webhook retries are standard in distributed CI/CD environments. GreenOps enforces two layers of defense against duplicate side effects:
1. **Webhook Ingestion Layer**: Every inbound delivery ID (`X-GitHub-Delivery`) is stored in `webhook_events`. Repeated delivery IDs immediately return `idempotent_skip`.
2. **Financial Ledger Layer**: In `record_pipeline_ledger_entry()`, debits are keyed by `(sprint_id, pipeline_run_id, entry_type)`. If alternate delivery IDs or concurrent telemetry events arrive for the same execution, GreenOps updates the existing ledger record instead of double-billing the sprint budget.

### 4. Distributed Concurrency & At-Least-Once Dispatch
When deferred jobs are queued for lower-carbon execution windows:
- **Atomic Compare-and-Swap (CAS)**: Workers execute a single SQL conditional update (`status = "SCHEDULED"` where status is `PENDING` or stale `SCHEDULED`). Only the winning worker proceeds.
- **Stale Claim Recovery**: If a worker crashes before completing dispatch, the claim expires after 5 minutes (`CLAIM_TIMEOUT_MINUTES`), allowing subsequent scheduler ticks to safely reclaim the job.
- **At-Least-Once Semantics**: Because GitHub's `workflow_dispatch` endpoint does not support client idempotency tokens, GreenOps guarantees at-least-once external triggering, while protecting downstream accounting via the webhook idempotency layer.

### 5. Migration-Governed Database Evolution
Database tables are strictly version-controlled with Alembic (`head: c341c4aec7e3`). The backend lifespan configuration strictly bypasses `Base.metadata.create_all()` in production environments, ensuring that schema modifications are always executed through deterministic, reversible migrations.
