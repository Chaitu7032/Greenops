# GreenOps REST API Specification

Base URI: `/api/v1`

## Endpoints

### Health & Readiness
- `GET /healthz` -> Returns `{"status": "ok"}`
- `GET /ready` -> Returns database & Redis connection health

### Webhooks
- `POST /api/v1/webhooks/github` -> Accepts GitHub `pull_request` & `workflow_run` events

### Organizations & Sprints
- `GET /api/v1/organizations` -> List organizations
- `GET /api/v1/sprints` -> List all sprints
- `GET /api/v1/sprints/{id}/budget` -> Sprint financial & carbon budget summary
- `GET /api/v1/sprints/{id}/burn-down` -> Sprint burn-down data points

### Dashboard Analytics
- `GET /api/v1/dashboard/overview` -> Real-time summary gauges, run counts, savings
- `GET /api/v1/dashboard/cost` -> Daily cumulative compute spending
- `GET /api/v1/dashboard/carbon` -> Scope-2 emissions timeline
- `GET /api/v1/dashboard/repositories` -> Repository consumption rankings
- `GET /api/v1/dashboard/savings` -> Avoided cost and carbon savings analytics

### Pipelines & Deferred Jobs
- `GET /api/v1/pipelines` -> Paginated pipeline runs & telemetry variance
- `GET /api/v1/deferred-jobs` -> List scheduled low-carbon deferred jobs
- `POST /api/v1/deferred-jobs/{id}/dispatch` -> Trigger manual workflow dispatch

### Demo & Testing
- `POST /api/v1/demo/seed` -> Seed deterministic SPM capstone dataset
