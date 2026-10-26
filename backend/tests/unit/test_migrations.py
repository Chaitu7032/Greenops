import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect
from alembic.config import Config
from alembic import command
from app.db.base import Base
import app.models  # load all models


def test_alembic_fresh_database_upgrade_head():
    """
    Test Scenario A: Starting from a completely empty database,
    running `alembic upgrade head` creates all expected tables,
    indexes, foreign keys, and records the current Alembic revision.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name

    try:
        temp_db_url = f"sqlite:///{temp_db_path}"

        # Initialize Alembic config targeting temp database
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", temp_db_url)

        # 1. Run migrations to head on empty database
        command.upgrade(alembic_cfg, "head")

        # 2. Inspect resulting schema
        test_engine = create_engine(temp_db_url)
        inspector = inspect(test_engine)
        table_names = set(inspector.get_table_names())

        # Expected domain tables
        expected_tables = {
            "alembic_version",
            "organizations",
            "repositories",
            "sprints",
            "pipeline_runs",
            "sprint_budget_ledger",
            "policies",
            "deferred_jobs",
            "webhook_events",
            "carbon_readings",
        }
        assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"

        # 3. Verify Alembic recorded the current head revision
        with test_engine.connect() as conn:
            from sqlalchemy import text
            rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            assert rev == "c341c4aec7e3"

        # 4. Verify model columns match in one representative core table
        pipeline_cols = {col["name"] for col in inspector.get_columns("pipeline_runs")}
        assert "run_id" in pipeline_cols
        assert "actual_duration_seconds" in pipeline_cols
        assert "actual_cost_usd" in pipeline_cols
        assert "actual_carbon_g" in pipeline_cols
        assert "execution_status" in pipeline_cols

        # 5. Verify re-running upgrade head is idempotent and safe
        command.upgrade(alembic_cfg, "head")

    finally:
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass


def test_alembic_existing_database_baseline_safety():
    """
    Test Scenario B: For an existing database with tables,
    stamping with alembic stamp head records the baseline without
    dropping tables or erasing application data.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name

    try:
        temp_db_url = f"sqlite:///{temp_db_path}"
        test_engine = create_engine(temp_db_url)

        # Create tables directly (simulating pre-existing database initialized with create_all)
        Base.metadata.create_all(bind=test_engine)

        # Insert a sample organization record to prove data safety
        with test_engine.begin() as conn:
            from sqlalchemy import text
            conn.execute(
                text(
                    "INSERT INTO organizations (id, name, monthly_budget_usd, carbon_budget_kg, created_at, updated_at) "
                    "VALUES ('test-org-123', 'Pre-existing Corp', 500.0, 50.0, '2026-01-01 00:00:00', '2026-01-01 00:00:00')"
                )
            )

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", temp_db_url)

        # Baseline: stamp head
        command.stamp(alembic_cfg, "head")

        # Verify alembic_version was created and stamped
        with test_engine.connect() as conn:
            from sqlalchemy import text
            rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            assert rev == "c341c4aec7e3"

            # Verify existing data was untouched
            org_name = conn.execute(
                text("SELECT name FROM organizations WHERE id = 'test-org-123'")
            ).scalar()
            assert org_name == "Pre-existing Corp"

    finally:
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass
