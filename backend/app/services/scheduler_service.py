from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
import structlog

from app.models.deferred_job import DeferredJob
from app.models.pipeline_run import PipelineRun
from app.models.repository import Repository
from app.services.github_service import github_service

logger = structlog.get_logger()


def schedule_deferred_job(
    db: Session,
    pipeline_run_id: str,
    repository_id: str,
    pr_number: int,
    workflow_name: str,
    target_ref: str,
    reason: str,
    delay_minutes: int = 60,
    priority: str = "ROUTINE",
) -> DeferredJob:
    """Schedule a non-critical workflow run for lower-carbon execution."""
    scheduled_for = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)

    # Check if existing deferred job exists for this pipeline run
    existing = db.query(DeferredJob).filter(DeferredJob.pipeline_run_id == pipeline_run_id).first()
    if existing:
        existing.scheduled_for = scheduled_for
        existing.reason = reason
        existing.status = "PENDING"
        db.commit()
        db.refresh(existing)
        return existing

    deferred_job = DeferredJob(
        pipeline_run_id=pipeline_run_id,
        repository_id=repository_id,
        pr_number=pr_number,
        workflow_name=workflow_name,
        target_ref=target_ref,
        scheduled_for=scheduled_for,
        reason=reason,
        priority=priority,
        status="PENDING",
    )
    db.add(deferred_job)

    # Update pipeline run status
    run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
    if run:
        run.execution_status = "DEFERRED"

    db.commit()
    db.refresh(deferred_job)
    logger.info("Scheduled deferred CI job", job_id=deferred_job.id, scheduled_for=scheduled_for.isoformat())
    return deferred_job


def dispatch_due_deferred_jobs(db: Session) -> List[DeferredJob]:
    """Find all PENDING deferred jobs whose scheduled_for timestamp is reached and dispatch them."""
    now = datetime.now(timezone.utc)
    due_jobs = (
        db.query(DeferredJob)
        .filter(
            DeferredJob.status == "PENDING",
            DeferredJob.scheduled_for <= now
        )
        .all()
    )

    dispatched = []
    for job in due_jobs:
        repo = db.query(Repository).filter(Repository.id == job.repository_id).first()
        if not repo:
            job.status = "FAILED"
            job.last_error = "Repository not found"
            db.commit()
            continue

        try:
            workflow_file = f"{job.workflow_name.lower().replace(' ', '-')}.yml"
            success = github_service.dispatch_workflow(
                owner=repo.owner,
                repo=repo.name,
                workflow_id=workflow_file,
                ref=job.target_ref,
                inputs={"pr_number": str(job.pr_number), "trigger_reason": "GreenOps Deferred Job Dispatch"}
            )
            if success:
                job.status = "DISPATCHED"
                job.attempts += 1
                dispatched.append(job)
            else:
                job.attempts += 1
                job.last_error = "GitHub Actions dispatch returned failure"
                if job.attempts >= 3:
                    job.status = "FAILED"
        except Exception as e:
            job.attempts += 1
            job.last_error = str(e)
            if job.attempts >= 3:
                job.status = "FAILED"

        db.commit()

    return dispatched
