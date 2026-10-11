from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
import structlog

from app.models.organization import Organization
from app.models.repository import Repository
from app.models.sprint import Sprint
from app.models.pipeline_run import PipelineRun
from app.services.diff_analyzer import analyze_pr_diff
from app.services.duration_estimator import estimate_duration
from app.services.cost_engine import calculate_compute_cost
from app.services.energy_engine import calculate_energy
from app.services.grid_service import get_grid_intensity
from app.services.carbon_engine import calculate_carbon
from app.services.budget_service import get_sprint_budget_summary, record_pipeline_ledger_entry
from app.services.policy_engine import evaluate_policy_gatekeeper
from app.services.scorecard_service import generate_pr_scorecard_markdown
from app.services.github_service import github_service
from app.services.scheduler_service import schedule_deferred_job

logger = structlog.get_logger()


def detect_pr_urgency(pr_title: str, labels: list) -> str:
    """Detect urgency level from PR title prefix or GitHub labels."""
    title_lower = pr_title.lower()
    label_names = [str(l.get("name", "")).lower() for l in labels]

    if "hotfix" in title_lower or "[hotfix]" in title_lower or "hotfix" in label_names:
        return "HOTFIX"
    if "blocking" in title_lower or "[blocking]" in title_lower or "blocker" in label_names:
        return "BLOCKING"
    return "ROUTINE"


def process_pull_request_event(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle GitHub `pull_request` (opened, synchronize, reopened) event.
    """
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})

    pr_number = pr_data.get("number")
    commit_sha = pr_data.get("head", {}).get("sha", "")
    author = pr_data.get("user", {}).get("login", "unknown")
    pr_title = pr_data.get("title", "PR")
    labels = pr_data.get("labels", [])
    ref = pr_data.get("head", {}).get("ref", "main")

    owner = repo_data.get("owner", {}).get("login", "")
    repo_name = repo_data.get("name", "")
    full_name = repo_data.get("full_name", f"{owner}/{repo_name}")
    github_repo_id = repo_data.get("id", 0)

    # 1. Look up or auto-register Repository and Organization
    repo = db.query(Repository).filter(Repository.full_name == full_name).first()
    if not repo:
        org = db.query(Organization).first()
        if not org:
            org = Organization(name=owner or "Default Organization")
            db.add(org)
            db.commit()
            db.refresh(org)

        repo = Repository(
            organization_id=org.id,
            github_repo_id=github_repo_id or 10001,
            owner=owner,
            name=repo_name,
            full_name=full_name,
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)

    organization_id = repo.organization_id

    # 2. Get active sprint for organization
    active_sprint = (
        db.query(Sprint)
        .filter(
            Sprint.organization_id == organization_id,
            Sprint.status == "ACTIVE"
        )
        .first()
    )
    sprint_id = active_sprint.id if active_sprint else None

    # 3. Detect urgency
    urgency = detect_pr_urgency(pr_title, labels)

    # 4. Fetch PR diff and analyze
    files_list = github_service.get_pr_files(owner, repo_name, pr_number)
    diff_result = analyze_pr_diff(files_list)

    # 5. Estimate Duration
    duration_res = estimate_duration(db, repo.id, diff_result, workflow_name="CI")
    estimated_seconds = duration_res.estimated_seconds

    # 6. Estimate Compute Cost
    estimated_cost = calculate_compute_cost(
        duration_seconds=estimated_seconds,
        cost_per_minute=repo.cost_per_minute,
    )

    # 7. Estimate Energy Consumption
    estimated_energy = calculate_energy(
        duration_seconds=estimated_seconds,
        power_idle_watts=repo.power_idle_watts,
        power_max_watts=repo.power_max_watts,
        pue=repo.pue,
    )

    # 8. Query Regional Grid Carbon Intensity
    grid_res = get_grid_intensity(repo.runner_region)
    grid_intensity = grid_res.intensity_gco2_kwh

    # 9. Calculate Carbon Footprint
    estimated_carbon = calculate_carbon(estimated_energy, grid_intensity)

    # 10. Evaluate Policy Gatekeeper
    policy_res = evaluate_policy_gatekeeper(
        db=db,
        repository_id=repo.id,
        organization_id=organization_id,
        sprint_id=sprint_id,
        estimated_cost_usd=estimated_cost,
        estimated_carbon_g=estimated_carbon,
        grid_intensity_gco2_kwh=grid_intensity,
        urgency=urgency,
    )

    # 11. Upsert PipelineRun record
    pipeline_run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.repository_id == repo.id,
            PipelineRun.pr_number == pr_number,
            PipelineRun.commit_sha == commit_sha
        )
        .first()
    )

    if not pipeline_run:
        pipeline_run = PipelineRun(
            repository_id=repo.id,
            organization_id=organization_id,
            sprint_id=sprint_id,
            pr_number=pr_number,
            commit_sha=commit_sha,
            author=author,
            workflow_name="CI",
            trigger_type="pull_request",
            changed_files_count=diff_result.changed_files_count,
            lines_added=diff_result.lines_added,
            lines_deleted=diff_result.lines_deleted,
            source_files_count=diff_result.source_files_count,
            test_files_count=diff_result.test_files_count,
            documentation_files_count=diff_result.documentation_files_count,
            configuration_files_count=diff_result.configuration_files_count,
            integration_files_count=diff_result.integration_files_count,
            estimated_duration_seconds=estimated_seconds,
            estimated_cost_usd=estimated_cost,
            estimated_energy_kwh=estimated_energy,
            grid_region=repo.runner_region,
            grid_intensity_gco2_kwh=grid_intensity,
            estimated_carbon_g=estimated_carbon,
            urgency=urgency,
            policy_decision=policy_res.decision,
            policy_reason=policy_res.reason,
            execution_status="DEFERRED" if policy_res.decision == "DEFERRED" else "PENDING",
        )
        db.add(pipeline_run)
    else:
        pipeline_run.estimated_duration_seconds = estimated_seconds
        pipeline_run.estimated_cost_usd = estimated_cost
        pipeline_run.estimated_energy_kwh = estimated_energy
        pipeline_run.grid_intensity_gco2_kwh = grid_intensity
        pipeline_run.estimated_carbon_g = estimated_carbon
        pipeline_run.urgency = urgency
        pipeline_run.policy_decision = policy_res.decision
        pipeline_run.policy_reason = policy_res.reason

    db.commit()
    db.refresh(pipeline_run)

    # 12. Handle Deferral if applicable
    if policy_res.decision == "DEFERRED":
        schedule_deferred_job(
            db=db,
            pipeline_run_id=pipeline_run.id,
            repository_id=repo.id,
            pr_number=pr_number,
            workflow_name="CI",
            target_ref=ref,
            reason=policy_res.reason,
            delay_minutes=policy_res.deferral_delay_minutes or 60,
            priority=urgency,
        )

    # 13. Generate and Post GitHub PR Scorecard
    sprint_summary = get_sprint_budget_summary(db, sprint_id) if sprint_id else None
    scorecard_md = generate_pr_scorecard_markdown(
        pipeline_run=pipeline_run,
        sprint_summary=sprint_summary,
        estimation_method=duration_res.method,
        confidence=duration_res.confidence,
        is_actual=False,
    )
    github_service.post_or_update_pr_comment(owner, repo_name, pr_number, scorecard_md)

    return {
        "pipeline_run_id": pipeline_run.id,
        "policy_decision": policy_res.decision,
        "reason": policy_res.reason,
        "estimated_duration_seconds": float(estimated_seconds),
        "estimated_cost_usd": float(estimated_cost),
        "estimated_carbon_g": float(estimated_carbon),
    }


def process_workflow_run_event(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle GitHub `workflow_run` completed event to capture actual execution telemetry.
    """
    wf_run = payload.get("workflow_run", {})
    repo_data = payload.get("repository", {})

    run_id = wf_run.get("id")
    head_sha = wf_run.get("head_sha", "")
    conclusion = wf_run.get("conclusion", "success")
    created_at_str = wf_run.get("run_started_at") or wf_run.get("created_at")
    updated_at_str = wf_run.get("updated_at")

    # Calculate actual duration
    actual_seconds = Decimal("120.00")
    if created_at_str and updated_at_str:
        try:
            start_t = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            end_t = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
            diff_s = (end_t - start_t).total_seconds()
            if diff_s > 0:
                actual_seconds = Decimal(str(round(diff_s, 2)))
        except Exception:
            pass

    full_name = repo_data.get("full_name", "")
    repo = db.query(Repository).filter(Repository.full_name == full_name).first()
    if not repo:
        return {"status": "skipped", "reason": "Repository not found"}

    # Find matching pipeline run by commit SHA
    pipeline_run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.repository_id == repo.id,
            PipelineRun.commit_sha == head_sha
        )
        .first()
    )

    if not pipeline_run:
        # Create pipeline run entry for direct workflow runs
        pipeline_run = PipelineRun(
            repository_id=repo.id,
            organization_id=repo.organization_id,
            commit_sha=head_sha,
            author=wf_run.get("actor", {}).get("login", "unknown"),
            workflow_name=wf_run.get("name", "CI"),
            trigger_type="workflow_run",
            grid_region=repo.runner_region,
            grid_intensity_gco2_kwh=Decimal("300.00"),
        )
        db.add(pipeline_run)
        db.commit()
        db.refresh(pipeline_run)

    # Compute actual telemetry
    actual_cost = calculate_compute_cost(actual_seconds, repo.cost_per_minute)
    actual_energy = calculate_energy(
        duration_seconds=actual_seconds,
        power_idle_watts=repo.power_idle_watts,
        power_max_watts=repo.power_max_watts,
        pue=repo.pue,
    )
    actual_carbon = calculate_carbon(actual_energy, pipeline_run.grid_intensity_gco2_kwh)

    pipeline_run.run_id = run_id
    pipeline_run.actual_duration_seconds = actual_seconds
    pipeline_run.actual_cost_usd = actual_cost
    pipeline_run.actual_energy_kwh = actual_energy
    pipeline_run.actual_carbon_g = actual_carbon
    pipeline_run.execution_status = "COMPLETED" if conclusion == "success" else "FAILED"

    # Record actual expenditure in Sprint Budget Ledger
    if pipeline_run.sprint_id:
        record_pipeline_ledger_entry(
            db=db,
            sprint_id=pipeline_run.sprint_id,
            pipeline_run_id=pipeline_run.id,
            amount_usd=actual_cost,
            carbon_g=actual_carbon,
            entry_type="ACTUAL_DEBIT",
        )

    db.commit()
    db.refresh(pipeline_run)

    # Update PR scorecard with Actuals & Variance if PR number exists
    if pipeline_run.pr_number and repo.owner and repo.name:
        sprint_summary = get_sprint_budget_summary(db, pipeline_run.sprint_id) if pipeline_run.sprint_id else None
        updated_scorecard = generate_pr_scorecard_markdown(
            pipeline_run=pipeline_run,
            sprint_summary=sprint_summary,
            is_actual=True,
        )
        github_service.post_or_update_pr_comment(repo.owner, repo.name, pipeline_run.pr_number, updated_scorecard)

    return {
        "status": "completed",
        "pipeline_run_id": pipeline_run.id,
        "actual_duration_seconds": float(actual_seconds),
        "actual_cost_usd": float(actual_cost),
        "actual_carbon_g": float(actual_carbon),
    }
