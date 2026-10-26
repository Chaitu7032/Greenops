# 🌱 GreenOps: FinOps & Cloud Carbon Budget Gatekeeper for CI/CD Pipelines

> **Software Project Management (SPM) Academic Capstone Platform**  
> An event-driven middleware bridging GitHub Pull Requests, cloud infrastructure cost modeling, regional grid carbon intensity tracking, and SPM sprint budgeting.

---

## 📌 Executive Summary

Traditional CI/CD pipelines trigger automated compute jobs indiscriminately upon every commit or pull request. **GreenOps** sits as an intelligent governance gatekeeper between GitHub Pull Requests and CI execution to:
1. **Enforce FinOps Sprint Budgets**: Prevent runaway cloud infrastructure costs by tracking CI spend against active sprint allocations in real-time.
2. **Reduce Scope-2 Carbon Footprints**: Evaluate regional electricity-grid carbon intensity (via Electricity Maps) and shift non-critical PR runs to off-peak, green energy windows.
3. **Actionable Developer Feedback**: Deliver immediate CI cost, duration, energy, and carbon scorecards directly inside GitHub PR comments.
4. **SPM Burn-Down Analytics**: Provide engineering managers with live budget vs. actuals, variance analysis, and repository rankings in a Next.js 14 command center.

---

## 🏛️ System Architecture

```
Developer
   ↓
GitHub Pull Request
   ↓
GitHub Webhook (HMAC-SHA256 Auth + Delivery Idempotency)
   ↓
FastAPI Ingestion Gateway
   ↓
PR Diff & File Classifier
   ↓
CI Duration Estimator (Historical Median + Deterministic Fallback)
   ↓
FinOps Cost Engine (Decimal Precision)
   ↓
Energy Engine (PUE + CPU Power Model)
   ↓
Grid Carbon Service (Electricity Maps API + Redis Cache 60m TTL)
   ↓
Scope-2 Carbon Engine (gCO₂e)
   ↓
SPM Sprint Budget Ledger
   ↓
Policy Gatekeeper
   ↓
┌──────────────┬──────────────┬──────────────┐
│   APPROVED   │   DEFERRED   │   FLAGGED    │
└──────────────┴──────────────┴──────────────┘
       ↓               ↓               ↓
  GitHub Actions  Redis/Celery    Lead Sign-off
    Execution      Delay Queue       Required
       ↓               ↓
GitHub Scorecard (In-Place Comment Update via <!-- greenops-scorecard -->)
       ↓
PostgreSQL Storage
       ↓
Next.js 14 SPM Command Center
```

---

## 🎯 Target Metrics vs Measured Telemetry

| Target Metric | Specification Objective | GreenOps Implementation Mechanism |
|---|---|---|
| **CI Spend Reduction** | 15–25% reduction | Single-run cost caps, sprint budget ceilings, and unnecessary run elimination |
| **Scope-2 Emissions** | 30% reduction per run | Regional grid intensity gating, deferred low-carbon execution windows |
| **Ingestion Latency** | Sub-3-second webhook processing | Constant-time HMAC validation, sub-500ms immediate ack, async processing |
| **Sprint Mapping** | 100% automated mapping | Git/commit telemetry mapped to active Sprint ledger in PostgreSQL |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Structlog
- **Database**: PostgreSQL (Supabase / local PostgreSQL / SQLite dev mode)
- **Caching & Async Queues**: Redis, Celery (Periodic low-carbon window polling & dispatch)
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Recharts, Lucide Icons
- **External Integrations**: GitHub REST API (Webhooks, Comments, Checks, Workflow Dispatch), Electricity Maps API
- **Testing**: Pytest, Pytest-Mock, Pytest-Cov (>80% engine coverage)
- **Deployment Targets**: Render/Railway (Backend), Vercel (Frontend), Supabase (PostgreSQL), Upstash (Redis)

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python >= 3.11
- Node.js >= 18
- Docker & Docker Compose (optional for full containerized stack)

### 2. Clone and Configure Environment
```bash
git clone https://github.com/your-org/greenops.git
cd greenops

# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration
cp frontend/.env.example frontend/.env.local
```

### 3. Start Backend & Run Migrations
```bash
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://127.0.0.1:8000` (Docs: `http://127.0.0.1:8000/docs`).

### 4. Start Celery Worker (Optional for Deferred Jobs)
```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info --beat
```

### 5. Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be available at `http://localhost:3000`.

### 6. One-Click Demo Seed
Visit `http://localhost:3000/dashboard` and click **"Seed SPM Demo Data"**, or run:
```bash
curl -X POST http://localhost:8000/api/v1/demo/seed
```

---

## 🧪 Testing & Verification Suite

GreenOps enforces rigorous quality gates across backend services, database migrations, and frontend components:

### Backend Tests (Pytest)
Run the full 37-test suite covering cost/carbon engines, diff classifiers, scheduler concurrency, webhook HMAC validation, and end-to-end integration:
```bash
cd backend
python -m pytest -v
```

### Database Migration Verification (Alembic)
Verify schema synchronization and detect any model/database drift:
```bash
cd backend
python -m alembic heads
python -m alembic check
```

### Frontend Tests & Type Checking (Jest & TypeScript)
Execute component unit tests, strict TypeScript validation, and production build checks:
```bash
cd frontend
npm test               # Run Jest unit test suites
npx tsc --noEmit       # Strict TypeScript type checking
npm run build          # Production Next.js bundle compilation
```

### Automated CI Quality Gates (GitHub Actions)
All pull requests and main branch commits are evaluated by `.github/workflows/ci.yml`:
- Parallel execution of **Backend CI** (PostgreSQL 16 container, `alembic upgrade head`, `alembic check`, `pytest`) and **Frontend CI** (`npm ci`, `jest`, `tsc`, `next build`).
- Consolidated branch protection gatekeeper job (`ci-gatekeeper`).

---

## 📚 Technical Documentation Directory

- [Architecture Specification](docs/architecture.md)
- [Database Schema & ER Model](docs/database.md)
- [REST API Reference](docs/api.md)
- [GitHub Webhooks & Actions Integration](docs/github-integration.md)
- [Cloud Energy & Carbon Mathematical Model](docs/carbon-model.md)
- [FinOps Cost Calculation Model](docs/cost-model.md)
- [Policy Gatekeeper Rules](docs/policy-engine.md)
- [Production Deployment Guide](docs/deployment.md)
- [Testing & Quality Assurance](docs/testing.md)
- [Capstone Demo & Presentation Script](docs/demo.md)
