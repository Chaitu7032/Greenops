from datetime import datetime, timedelta, timezone
from decimal import Decimal
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.organization import Organization
from app.models.repository import Repository
from app.models.sprint import Sprint
from app.models.pipeline_run import PipelineRun
from app.models.policy import Policy
from app.models.deferred_job import DeferredJob
from app.models.budget_ledger import SprintBudgetLedger

router = APIRouter(prefix="/api/v1/demo", tags=["Demo Seed"])


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_demo_data(db: Session = Depends(get_db)):
    """Seed comprehensive, deterministic SPM demo dataset for capstone evaluation."""
    now = datetime.now(timezone.utc)

    # 1. Organization
    org = db.query(Organization).filter(Organization.name == "GreenOps Demo Organization").first()
    if not org:
        org = Organization(
            name="GreenOps Demo Organization",
            monthly_budget_usd=Decimal("500.0000"),
            carbon_budget_kg=Decimal("100.0000"),
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # 2. Sprints
    sprint1 = db.query(Sprint).filter(Sprint.name == "Sprint 1 - Inception & Core Gateway").first()
    if not sprint1:
        sprint1 = Sprint(
            organization_id=org.id,
            name="Sprint 1 - Inception & Core Gateway",
            external_sprint_id="SPM-SPRINT-01",
            start_date=now - timedelta(days=14),
            end_date=now - timedelta(days=1),
            budget_usd=Decimal("200.0000"),
            carbon_budget_kg=Decimal("40.0000"),
            status="COMPLETED",
        )
        db.add(sprint1)

    sprint2 = db.query(Sprint).filter(Sprint.name == "Sprint 2 - Analytical & Policy Engine").first()
    if not sprint2:
        sprint2 = Sprint(
            organization_id=org.id,
            name="Sprint 2 - Analytical & Policy Engine",
            external_sprint_id="SPM-SPRINT-02",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=13),
            budget_usd=Decimal("300.0000"),
            carbon_budget_kg=Decimal("60.0000"),
            status="ACTIVE",
        )
        db.add(sprint2)
        db.commit()
        db.refresh(sprint2)
        org.active_sprint_id = sprint2.id
        db.commit()

    # 3. Repositories
    repos_data = [
        {
            "github_repo_id": 90101,
            "owner": "greenops-org",
            "name": "backend-api",
            "full_name": "greenops-org/backend-api",
            "runner_type": "ubuntu-latest",
            "runner_region": "US-EAST",
            "cpu_cores": 4,
            "memory_gb": Decimal("16.00"),
            "cost_per_minute": Decimal("0.016000"),
            "power_idle_watts": Decimal("15.00"),
            "power_max_watts": Decimal("75.00"),
            "pue": Decimal("1.150"),
        },
        {
            "github_repo_id": 90102,
            "owner": "greenops-org",
            "name": "frontend-web",
            "full_name": "greenops-org/frontend-web",
            "runner_type": "ubuntu-latest",
            "runner_region": "EU-WEST",
            "cpu_cores": 2,
            "memory_gb": Decimal("7.00"),
            "cost_per_minute": Decimal("0.008000"),
            "power_idle_watts": Decimal("10.00"),
            "power_max_watts": Decimal("45.00"),
            "pue": Decimal("1.120"),
        },
        {
            "github_repo_id": 90103,
            "owner": "greenops-org",
            "name": "ml-service",
            "full_name": "greenops-org/ml-service",
            "runner_type": "ubuntu-latest",
            "runner_region": "AP-SOUTH",
            "cpu_cores": 8,
            "memory_gb": Decimal("32.00"),
            "cost_per_minute": Decimal("0.032000"),
            "power_idle_watts": Decimal("25.00"),
            "power_max_watts": Decimal("140.00"),
            "pue": Decimal("1.250"),
        },
    ]

    saved_repos = {}
    for r_data in repos_data:
        r = db.query(Repository).filter(Repository.full_name == r_data["full_name"]).first()
        if not r:
            r = Repository(organization_id=org.id, **r_data)
            db.add(r)
            db.commit()
            db.refresh(r)
        saved_repos[r.name] = r

    # 4. Standard Policy
    pol = db.query(Policy).filter(Policy.organization_id == org.id).first()
    if not pol:
        pol = Policy(
            organization_id=org.id,
            name="GreenOps Standard Sprint Gate",
            max_cost_per_run_usd=Decimal("1.2000"),
            max_carbon_per_run_g=Decimal("280.00"),
            budget_warning_percent=Decimal("80.00"),
            budget_block_percent=Decimal("100.00"),
            high_grid_intensity_threshold=Decimal("380.00"),
            allow_deferred_execution=True,
        )
        db.add(pol)
        db.commit()

    # 5. Seed Pipeline Runs across scenarios
    runs_seed = [
        # Scenario 1: Routine PR Approved in Sprint 1
        {
            "repo": "backend-api",
            "sprint": sprint1,
            "pr": 101,
            "sha": "a1b2c3d4e5f601",
            "author": "sarah-dev",
            "urgency": "ROUTINE",
            "decision": "APPROVED",
            "reason": "Within sprint financial budget and green grid thresholds.",
            "status": "COMPLETED",
            "est_dur": 420.0,
            "act_dur": 435.0,
            "est_cost": Decimal("0.1120"),
            "act_cost": Decimal("0.1160"),
            "est_energy": Decimal("0.0065"),
            "act_energy": Decimal("0.0067"),
            "grid_region": "US-EAST",
            "grid_intensity": Decimal("240.00"),
            "est_carbon": Decimal("1.5600"),
            "act_carbon": Decimal("1.6080"),
            "days_ago": 10,
        },
        # Scenario 2: Documentation PR Fast path
        {
            "repo": "frontend-web",
            "sprint": sprint1,
            "pr": 45,
            "sha": "b2c3d4e5f6a102",
            "author": "alex-tech",
            "urgency": "ROUTINE",
            "decision": "APPROVED",
            "reason": "Documentation changes only; minimal compute footprint.",
            "status": "COMPLETED",
            "est_dur": 30.0,
            "act_dur": 28.0,
            "est_cost": Decimal("0.0040"),
            "act_cost": Decimal("0.0037"),
            "est_energy": Decimal("0.0003"),
            "act_energy": Decimal("0.0002"),
            "grid_region": "EU-WEST",
            "grid_intensity": Decimal("180.00"),
            "est_carbon": Decimal("0.0540"),
            "act_carbon": Decimal("0.0360"),
            "days_ago": 8,
        },
        # Scenario 3: High Grid Intensity -> DEFERRED
        {
            "repo": "backend-api",
            "sprint": sprint2,
            "pr": 112,
            "sha": "c3d4e5f6a1b203",
            "author": "dev-vikram",
            "urgency": "ROUTINE",
            "decision": "DEFERRED",
            "reason": "Current regional grid carbon intensity (440.0 gCO2e/kWh) exceeds green threshold (380.0 gCO2e/kWh). Queued for lower-carbon window.",
            "status": "DEFERRED",
            "est_dur": 900.0,
            "act_dur": None,
            "est_cost": Decimal("0.2400"),
            "act_cost": None,
            "est_energy": Decimal("0.0142"),
            "act_energy": None,
            "grid_region": "US-EAST",
            "grid_intensity": Decimal("440.00"),
            "est_carbon": Decimal("6.2480"),
            "act_carbon": None,
            "days_ago": 1,
        },
        # Scenario 4: Hotfix PR during High Carbon Window -> APPROVED
        {
            "repo": "frontend-web",
            "sprint": sprint2,
            "pr": 52,
            "sha": "d4e5f6a1b2c304",
            "author": "lead-rachel",
            "urgency": "HOTFIX",
            "decision": "APPROVED",
            "reason": "Hotfix priority override: Bypassed carbon/budget optimization gates for urgent production remediation.",
            "status": "COMPLETED",
            "est_dur": 180.0,
            "act_dur": 195.0,
            "est_cost": Decimal("0.0240"),
            "act_cost": Decimal("0.0260"),
            "est_energy": Decimal("0.0017"),
            "act_energy": Decimal("0.0018"),
            "grid_region": "EU-WEST",
            "grid_intensity": Decimal("410.00"),
            "est_carbon": Decimal("0.6970"),
            "act_carbon": Decimal("0.7380"),
            "days_ago": 0,
        },
        # Scenario 5: Large ML Pipeline PR -> FLAGGED
        {
            "repo": "ml-service",
            "sprint": sprint2,
            "pr": 19,
            "sha": "e5f6a1b2c3d405",
            "author": "data-chen",
            "urgency": "ROUTINE",
            "decision": "FLAGGED",
            "reason": "Estimated carbon footprint (312.5 gCO2e) exceeds single-run limit of 280.0 gCO2e.",
            "status": "PENDING",
            "est_dur": 2400.0,
            "act_dur": None,
            "est_cost": Decimal("1.2800"),
            "act_cost": None,
            "est_energy": Decimal("0.0712"),
            "act_energy": None,
            "grid_region": "AP-SOUTH",
            "grid_intensity": Decimal("650.00"),
            "est_carbon": Decimal("46.2800"),
            "act_carbon": None,
            "days_ago": 0,
        },
    ]

    for item in runs_seed:
        r_obj = saved_repos[item["repo"]]
        existing_run = db.query(PipelineRun).filter(PipelineRun.commit_sha == item["sha"]).first()
        if not existing_run:
            created_time = now - timedelta(days=item["days_ago"])
            p_run = PipelineRun(
                repository_id=r_obj.id,
                organization_id=org.id,
                sprint_id=item["sprint"].id if item.get("sprint") else None,
                pr_number=item["pr"],
                commit_sha=item["sha"],
                author=item["author"],
                workflow_name="CI",
                trigger_type="pull_request",
                changed_files_count=8,
                lines_added=150,
                lines_deleted=40,
                source_files_count=5,
                test_files_count=2,
                documentation_files_count=1,
                configuration_files_count=0,
                integration_files_count=0,
                estimated_duration_seconds=Decimal(str(item["est_dur"])),
                actual_duration_seconds=Decimal(str(item["act_dur"])) if item["act_dur"] else None,
                estimated_cost_usd=item["est_cost"],
                actual_cost_usd=item["act_cost"],
                estimated_energy_kwh=item["est_energy"],
                actual_energy_kwh=item["act_energy"],
                grid_region=item["grid_region"],
                grid_intensity_gco2_kwh=item["grid_intensity"],
                estimated_carbon_g=item["est_carbon"],
                actual_carbon_g=item["act_carbon"],
                urgency=item["urgency"],
                policy_decision=item["decision"],
                policy_reason=item["reason"],
                execution_status=item["status"],
                created_at=created_time,
                updated_at=created_time,
            )
            db.add(p_run)
            db.commit()
            db.refresh(p_run)

            # Add ledger debit if actual cost exists
            if item["act_cost"] and item.get("sprint"):
                ledger = SprintBudgetLedger(
                    sprint_id=item["sprint"].id,
                    pipeline_run_id=p_run.id,
                    amount_usd=item["act_cost"],
                    carbon_g=item["act_carbon"] or Decimal("0"),
                    entry_type="ACTUAL_DEBIT",
                    created_at=created_time,
                )
                db.add(ledger)
                db.commit()

            # If DEFERRED, create deferred job
            if item["decision"] == "DEFERRED":
                d_job = DeferredJob(
                    pipeline_run_id=p_run.id,
                    repository_id=r_obj.id,
                    pr_number=item["pr"],
                    workflow_name="CI",
                    target_ref="main",
                    scheduled_for=now + timedelta(hours=2),
                    reason=item["reason"],
                    priority=item["urgency"],
                    status="PENDING",
                    created_at=created_time,
                )
                db.add(d_job)
                db.commit()

    return {
        "status": "seeded",
        "message": "GreenOps SPM demo data seeded successfully",
        "organization": org.name,
        "active_sprint": sprint2.name,
        "repositories_count": len(saved_repos),
        "pipeline_runs_seeded": len(runs_seed),
    }
