# Database Schema, ER Model & Alembic Migrations

GreenOps uses PostgreSQL for production environments and SQLite for local rapid-testing, managed declaratively via SQLAlchemy 2.0 and version-controlled via Alembic migrations.

---

## 1. Entity Relationship (ER) Model

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ REPOSITORIES : owns
    ORGANIZATIONS ||--o{ SPRINTS : plans
    ORGANIZATIONS ||--o{ POLICIES : defines
    
    REPOSITORIES ||--o{ PIPELINE_RUNS : executes
    REPOSITORIES ||--o{ POLICIES : configures
    REPOSITORIES ||--o{ WEBHOOK_EVENTS : receives
    
    SPRINTS ||--o{ PIPELINE_RUNS : tracks
    SPRINTS ||--o{ SPRINT_BUDGET_LEDGER : records
    
    PIPELINE_RUNS ||--o| DEFERRED_JOBS : defers
    PIPELINE_RUNS ||--o{ SPRINT_BUDGET_LEDGER : debits
    
    ORGANIZATIONS {
        uuid id PK
        string name
        numeric monthly_budget_usd
        numeric carbon_budget_kg
        datetime created_at
    }
    
    REPOSITORIES {
        uuid id PK
        uuid organization_id FK
        bigint github_repo_id UK
        string full_name UK
        string runner_region
        numeric cost_per_minute
        numeric power_idle_watts
        numeric power_max_watts
        numeric pue
    }
    
    SPRINTS {
        uuid id PK
        uuid organization_id FK
        string name
        datetime start_date
        datetime end_date
        numeric budget_usd
        numeric carbon_budget_kg
        string status
    }
    
    PIPELINE_RUNS {
        uuid id PK
        uuid repository_id FK
        uuid organization_id FK
        uuid sprint_id FK
        int pr_number
        string commit_sha
        bigint run_id
        numeric estimated_duration_seconds
        numeric actual_duration_seconds
        numeric estimated_cost_usd
        numeric actual_cost_usd
        numeric estimated_carbon_g
        numeric actual_carbon_g
        string urgency
        string policy_decision
        string execution_status
    }
    
    DEFERRED_JOBS {
        uuid id PK
        uuid pipeline_run_id FK, UK
        uuid repository_id FK
        int pr_number
        datetime scheduled_for
        string priority
        string status
        int attempts
        string last_error
    }
    
    SPRINT_BUDGET_LEDGER {
        uuid id PK
        uuid sprint_id FK
        uuid pipeline_run_id FK
        numeric amount_usd
        numeric carbon_g
        string entry_type
        datetime created_at
    }
    
    WEBHOOK_EVENTS {
        uuid id PK
        string github_delivery_id UK
        string event_type
        string payload_hash
        json payload
        boolean processed
        datetime received_at
    }
    
    CARBON_READINGS {
        uuid id PK
        string region
        numeric carbon_intensity_gco2_kwh
        datetime timestamp
        string source
        boolean forecast
    }
    
    POLICIES {
        uuid id PK
        uuid organization_id FK
        uuid repository_id FK
        numeric max_cost_per_run_usd
        numeric max_carbon_per_run_g
        numeric high_grid_intensity_threshold
        boolean allow_deferred_execution
    }
```

---

## 2. Table Specifications & Constraints

### `repositories`
- **Primary Key**: `id` (`GUID`)
- **Indexes & Unique Constraints**:
  - `ix_repositories_github_repo_id`: Unique on `github_repo_id`
  - `ix_repositories_full_name`: Unique on `full_name` (`owner/name`)
  - `ix_repositories_organization_id`: Index on `organization_id`
- **Foreign Keys**: `organization_id` $\to$ `organizations.id` (ON DELETE CASCADE)

### `pipeline_runs`
- **Primary Key**: `id` (`GUID`)
- **Indexes**: `commit_sha`, `pr_number`, `repository_id`, `sprint_id`, `organization_id`, `created_at`
- **Foreign Keys**:
  - `repository_id` $\to$ `repositories.id` (ON DELETE CASCADE)
  - `organization_id` $\to$ `organizations.id` (ON DELETE CASCADE)
  - `sprint_id` $\to$ `sprints.id` (ON DELETE SET NULL)

### `deferred_jobs`
- **Primary Key**: `id` (`GUID`)
- **Constraints**:
  - `uq_deferred_jobs_pipeline_run_id`: Unique on `pipeline_run_id` (ensures strict 1-to-1 relationship with pipeline run)
- **Foreign Keys**:
  - `pipeline_run_id` $\to$ `pipeline_runs.id` (ON DELETE CASCADE)
  - `repository_id` $\to$ `repositories.id` (ON DELETE CASCADE)

### `sprint_budget_ledger`
- **Primary Key**: `id` (`GUID`)
- **Indexes**: `sprint_id`, `pipeline_run_id`
- **Foreign Keys**:
  - `sprint_id` $\to$ `sprints.id` (ON DELETE CASCADE)
  - `pipeline_run_id` $\to$ `pipeline_runs.id` (ON DELETE SET NULL)
- **Application Idempotency**:
  - GreenOps enforces idempotency at the service layer in `record_pipeline_ledger_entry()`, querying `(sprint_id, pipeline_run_id, entry_type)` to prevent duplicate debits.

### `webhook_events`
- **Primary Key**: `id` (`GUID`)
- **Constraints**:
  - `ix_webhook_events_github_delivery_id`: Unique on `github_delivery_id` (prevents processing identical webhook deliveries)

---

## 3. Platform-Independent GUID Type

To allow smooth local development with SQLite without breaking PostgreSQL production UUID columns, GreenOps uses a custom SQLAlchemy `TypeDecorator`:

```python
class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            return str(uuid.UUID(str(value)))
```

---

## 4. Alembic Migration Architecture

Migrations are versioned in `backend/app/db/migrations/versions/`.

### Migration History
| Revision ID | Description | Down Revision |
|---|---|---|
| `c341c4aec7e3` | Initial comprehensive schema creation with all 8 core entities, indexes, and foreign keys | `None` (Head) |

### Migration Commands
```bash
cd backend

# View current migration head
python -m alembic heads

# View database current revision
python -m alembic current

# Upgrade database to latest revision
python -m alembic upgrade head

# Detect schema/model drift (used in CI)
python -m alembic check
```

---

## 5. Startup Policy: Production vs. Development

In `backend/app/main.py`:
- **Development Mode (`ENVIRONMENT == "development"` and SQLite)**: Automatically calls `Base.metadata.create_all(bind=engine)` if tables do not exist for instant local onboarding.
- **Production Mode (`ENVIRONMENT == "production"` or PostgreSQL)**: `create_all()` is **strictly bypassed**. All schema evolution is governed solely by `alembic upgrade head`.
