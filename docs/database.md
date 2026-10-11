# Database Schema & Entity Relationships

The GreenOps data tier is built on PostgreSQL (managed via SQLAlchemy 2.0 and Alembic migrations).

## ER Model Diagram
```
ORGANIZATIONS (id, name, monthly_budget_usd, carbon_budget_kg)
  │
  ├── 1:N ── REPOSITORIES (id, github_repo_id, full_name, runner_type, runner_region, cost_per_minute, power_idle_watts, power_max_watts, pue)
  │            │
  │            └── 1:N ── PIPELINE_RUNS (id, pr_number, commit_sha, estimated_*, actual_*, urgency, policy_decision, policy_reason)
  │                         │
  │                         └── 1:1 ── DEFERRED_JOBS (id, scheduled_for, priority, status, attempts)
  │
  └── 1:N ── SPRINTS (id, name, start_date, end_date, budget_usd, carbon_budget_kg, status)
               │
               └── 1:N ── SPRINT_BUDGET_LEDGER (id, pipeline_run_id, amount_usd, carbon_g, entry_type)

WEBHOOK_EVENTS (id, github_delivery_id, event_type, payload_hash, payload, processed)
CARBON_READINGS (id, region, carbon_intensity_gco2_kwh, timestamp, source, forecast)
POLICIES (id, organization_id, repository_id, max_cost_per_run_usd, max_carbon_per_run_g, high_grid_intensity_threshold)
```

## Migration Commands
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Upgrade to latest schema
alembic upgrade head
```
