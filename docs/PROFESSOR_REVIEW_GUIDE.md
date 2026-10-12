# 🎓 GreenOps: SPM Capstone Project Review & Viva Defense Guide
## High-Scoring Defense & Demonstration Guide for Evaluators & Professors

---

## ⚡ 1. Quick Commands to Run the Complete System

### Terminal 1: Start Backend Server (FastAPI)
```powershell
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```
- **Live API Endpoint**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health / Readiness Checks**: `http://127.0.0.1:8000/healthz` | `http://127.0.0.1:8000/ready`

### Terminal 2: Start Frontend Dashboard (Next.js 14)
```powershell
cd frontend
npm run dev
```
- **Live Dashboard**: `http://localhost:3000/dashboard`
- **Sprint Governance & Burn-Down**: `http://localhost:3000/sprints`
- **CI Pipeline Telemetry Audit**: `http://localhost:3000/pipelines`
- **Repository Rankings**: `http://localhost:3000/repositories`
- **Policy Gatekeeper**: `http://localhost:3000/policies`

### Terminal 3: Trigger Live Simulation Script (During Presentation)
```powershell
cd backend
python -u scripts/demo_runner.py
```

---

## 🎯 2. The 30-Second Elevator Pitch (Opening Hook)

> *"Professor, conventional CI/CD pipelines trigger automated cloud runners indiscriminately upon every commit without knowing whether the sprint cloud budget is exhausted or whether the regional electricity grid is running on high-carbon fossil fuels.*
>
> *Most FinOps tools are reactive—they show waste weeks later when the cloud bill arrives.*
>
> ***GreenOps is an intelligent, event-driven middleware gatekeeper.*** *It intercepts GitHub Pull Requests in real-time, models runtime, compute cost, server power (PUE), and Scope-2 carbon emissions, and enforces SPM sprint budget policies—producing **APPROVED**, **DEFERRED**, or **FLAGGED** decisions before cloud money and carbon are spent."*

---

## 🏛️ 3. Why This is an SPM (Software Project Management) Platform, Not Just a DevOps Tool

Make sure to emphasize the **SPM elements** to score high:

1. **Automated Sprint Mapping**: Every pull request, commit, and workflow run is automatically linked to the active **SPM Sprint ID** in PostgreSQL.
2. **Sprint Budget Governance**: Tracks financial budget ($) and Scope-2 carbon budget (kg) per sprint, preventing budget overrun during release crunches.
3. **Linear Ideal vs. Actual Burn-Down**: Provides real-time burn-down charts of remaining cloud budget vs. ideal burn trajectory across the sprint timeline.
4. **Authoritative Microservice Accountability**: Ranks repositories by total spend, emissions, and deferred runs so project managers can identify resource-heavy components.
5. **Estimator Accuracy & Variance Telemetry**: Compares pre-run estimates with post-run actuals (`variance = actual - estimated`) to continuously evaluate estimation accuracy without relying on unexplainable black-box ML.

---

## 🔬 4. The Engineering & Mathematical Models (Show These Formulas!)

### A. FinOps Compute Cost Engine
$$\text{Cost (\$) } = \left(\frac{\text{Duration (seconds)}}{60}\right) \times \text{CostPerMinute} + \text{DataTransferCost}$$
- **Key point for examiner**: Evaluated using high-precision **Python `Decimal` arithmetic** to eliminate binary floating-point round-off errors.

### B. Cloud Server Energy Engine
$$\text{Power (Watts)} = P_{\text{idle}} + (P_{\text{max}} - P_{\text{idle}}) \times \text{CPU\_Utilization}$$
$$E (\text{kWh}) = \frac{\text{Power (Watts)} \times \left(\frac{\text{Duration (seconds)}}{3600}\right) \times \text{PUE}}{1000}$$
- **Key point for examiner**: Accounts for Power Usage Effectiveness ($PUE = 1.15$) and baseline idle draw ($10\text{W}$) vs max draw ($50\text{W}$).

### C. Scope-2 Carbon Footprint Model
$$\text{CO}_2\text{e (grams)} = E (\text{kWh}) \times \text{Grid\_Carbon\_Intensity} (\text{gCO}_2\text{e/kWh})$$
- **Key point for examiner**: Regional intensity retrieved dynamically via **Electricity Maps API** and cached in Redis with a 60-minute TTL.

---

## 🎬 5. The 5 Live Presentation Scenarios (Demo Walkthrough)

| Scenario | PR Condition | Decision | Explanation for Professor |
|---|---|---|---|
| **Scenario 1** | Routine PR with normal diff under budget during clean grid hours | **`APPROVED` 🟢** | Telemetry estimated ($0.025, 0.67g), within sprint limits. Scorecard posted to PR comment. |
| **Scenario 2** | Routine non-urgent PR during peak grid carbon intensity ($>380\text{ gCO}_2\text{e/kWh}$) | **`DEFERRED` 🟡** | Policy Engine defers non-critical run to a scheduled lower-carbon window via Redis/Celery queue. |
| **Scenario 3** | Production Hotfix (`[HOTFIX]` tag) during peak carbon grid window | **`APPROVED` 🟢** | **Urgency Priority Override**: Hotfixes bypass optimization gates to guarantee system uptime. |
| **Scenario 4** | Sprint budget exhausted or large run exceeding single-run limit | **`FLAGGED` 🔴** | Policy blocks unapproved expenditure, requiring Engineering Lead sign-off. |
| **Scenario 5** | GitHub Actions execution completes (`workflow_run`) | **Telemetry Actuals** | PostgreSQL captures actual duration, cost, and Scope-2 emissions, calculating variance against estimates. |

---

## ❓ 6. Expected Professor / Examiner Questions & Model Answers

### Q1: "How do you estimate CI duration without using Machine Learning?"
> **Answer**: *"We deliberately used a deterministic, explainable two-tier model: **Historical Median** of previous completed runs for the same repository and workflow, with a conservative **Deterministic Heuristic Fallback** based on file classification (source, unit tests, integration tests, CI configuration, and line changes). This avoids ML 'hallucinations' or cold-start bias, and provides auditable confidence metrics."*

### Q2: "How do you handle GitHub webhook security and duplicate deliveries?"
> **Answer**: *"We implement constant-time HMAC-SHA256 signature verification (`X-Hub-Signature-256`) using our server-side webhook secret to reject unauthenticated requests. Additionally, every GitHub delivery ID (`X-GitHub-Delivery`) is checked against our `webhook_events` table for **strict idempotency**, preventing duplicate processing if GitHub retries a webhook."*

### Q3: "What happens if Electricity Maps API is down or rate-limited?"
> **Answer**: *"We implement a 3-tier fallback in our `grid_service.py`: First, it queries fresh Redis cache (60m TTL). Second, if the API fails, it uses stale Redis cache with a `stale=True` flag displayed on the UI. Third, it falls back to documented regional baseline averages. We never crash or fabricate ungrounded live data."*

### Q4: "How does deferred execution actually run on GitHub Actions?"
> **Answer**: *"When a job is deferred, GreenOps creates a `DeferredJob` record. Our Celery worker polls for scheduled green windows. When the window opens, GreenOps dispatches the workflow via GitHub REST API (`POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`), which triggers the target workflow on GitHub."*

### Q5: "How does the PR comment not spam developer pull requests?"
> **Answer**: *"We embed a hidden HTML marker `<!-- greenops-scorecard -->` inside our scorecard markdown. When a new commit or actual run finishes, our service queries existing issue comments, finds the comment with this anchor, and updates it in-place using a GitHub API `PATCH` request."*

### Q6: "How do you prevent two background workers from claiming and dispatching the same deferred job simultaneously?"
> **Answer**: *"We use an atomic compare-and-swap (CAS) conditional SQL update in `claim_deferred_job()`. A worker updates the job status to `SCHEDULED` only if its status is currently `PENDING` or stuck in `SCHEDULED` beyond a 5-minute timeout. Only the worker that gets `rows_updated == 1` proceeds with the GitHub dispatch. Stale claims are automatically recovered if a worker crashes midway."*

### Q7: "How do you ensure financial budgets aren't debited twice if a webhook is redelivered?"
> **Answer**: *"Beyond the webhook delivery ID check, we enforce ledger-level idempotency in `record_pipeline_ledger_entry()`. We check for existing entries matching `(sprint_id, pipeline_run_id, entry_type)`. If one exists, we update the recorded amounts rather than appending a duplicate debit row, guaranteeing financial integrity."*

### Q8: "How is database schema evolution managed across local development and production?"
> **Answer**: *"We use version-controlled Alembic migrations (`head: c341c4aec7e3`). In production, application startup strictly bypasses `Base.metadata.create_all()` and relies entirely on `alembic upgrade head`. Furthermore, our CI pipeline runs `alembic check` to automatically fail builds if developers modify SQLAlchemy models without generating a migration."*

### Q9: "What testing and automated quality gates exist in the project?"
> **Answer**: *"We have 37 backend tests in Pytest covering all engines, diff analyzers, scheduler concurrency, and end-to-end integration flows. On the frontend, we have 14 Jest/React Testing Library unit tests verifying component states and budget gauge thresholds, alongside strict TypeScript validation and production builds. Both run automatically in parallel on GitHub Actions via `.github/workflows/ci.yml`."*

---

## 📊 7. Step-by-Step Presentation Checklist

1. [ ] Start Backend (`python -m alembic upgrade head && python -m uvicorn app.main:app --port 8000`).
2. [ ] Open Dashboard at `http://localhost:3000/dashboard`.
3. [ ] Explain the **Problem Statement** & **Elevator Pitch**.
4. [ ] Point out the **Sprint Financial & Carbon Budget Gauges**.
5. [ ] Navigate to `/sprints` and explain the **Linear Burn-Down Chart**.
6. [ ] Navigate to `/repositories` and explain **Power Usage Profiles & Rankings**.
7. [ ] Run `python -u scripts/demo_runner.py` in terminal to simulate live PR events and watch the UI update in real time.
8. [ ] Navigate to `/policies` to showcase the **Deferred Execution Queue** and manual dispatch override.
