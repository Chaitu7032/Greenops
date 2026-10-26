from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
import structlog

from app.models.deferred_job import DeferredJob
from app.models.pipeline_run import PipelineRun
from app.models.repository import Repository
from app.services.github_service import github_service

logger = structlog.get_logger()

# Maximum execution attempts before marking job FAILED
MAX_DISPATCH_ATTEMPTS = 3
# Timeout after which a claimed (SCHEDULED) job without completion is considered stale and recoverable
CLAIM_TIMEOUT_MINUTES = 5


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
        existing.updated_at = datetime.now(timezone.utc)
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


def claim_deferred_job(db: Session, job_id: str) -> bool:
    """
    Atomically claim a deferred job for dispatch using a database conditional update.
    Returns True if this worker won the claim, False otherwise.
    Allows claiming if status is PENDING, or if stuck in SCHEDULED beyond CLAIM_TIMEOUT_MINUTES.
    """
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(minutes=CLAIM_TIMEOUT_MINUTES)

    # Atomic compare-and-swap / conditional update
    rows_updated = (
        db.query(DeferredJob)
        .filter(
            DeferredJob.id == job_id,
            or_(
                DeferredJob.status == "PENDING",
                # Recover stale claimed jobs that never reached DISPATCHED or terminal state
                (DeferredJob.status == "SCHEDULED") & (DeferredJob.updated_at <= stale_threshold)
            )
        )
        .update(
            {
                DeferredJob.status: "SCHEDULED",
                DeferredJob.updated_at: now,
            },
            synchronize_session="fetch",
        )
    )
    db.commit()
    return rows_updated > 0


def dispatch_single_job(
    db: Session,
    job_id: str,
    trigger_reason: str = "GreenOps Deferred Job Dispatch"
) -> Optional[DeferredJob]:
    """
    Atomically claim and dispatch a single deferred job to GitHub Actions.
    Reused by both the periodic background scheduler and manual REST endpoint.
    """
    # 1. Attempt atomic claim
    claimed = claim_deferred_job(db, job_id)
    if not claimed:
        logger.info("Deferred job claim skipped: already claimed or completed", job_id=job_id)
        return None

    job = db.query(DeferredJob).filter(DeferredJob.id == job_id).first()
    if not job:
        return None

    repo = db.query(Repository).filter(Repository.id == job.repository_id).first()
    if not repo:
        job.status = "FAILED"
        job.last_error = "Repository not found"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    try:
        workflow_file = f"{job.workflow_name.lower().replace(' ', '-')}.yml"
        success = github_service.dispatch_workflow(
            owner=repo.owner,
            repo=repo.name,
            workflow_id=workflow_file,
            ref=job.target_ref,
            inputs={"pr_number": str(job.pr_number), "trigger_reason": trigger_reason}
        )

        job.attempts += 1
        job.updated_at = datetime.now(timezone.utc)

        if success:
            job.status = "DISPATCHED"
            job.last_error = None
            logger.info("Successfully dispatched deferred job", job_id=job.id, attempts=job.attempts)
        else:
            job.last_error = "GitHub Actions dispatch returned failure"
            if job.attempts >= MAX_DISPATCH_ATTEMPTS:
                job.status = "FAILED"
                logger.error("Deferred job reached max attempts and failed", job_id=job.id, attempts=job.attempts)
            else:
                # Return to PENDING so subsequent scheduler ticks can retry with backoff
                job.status = "PENDING"
                logger.warning("Deferred job dispatch attempt failed; returned to PENDING", job_id=job.id, attempts=job.attempts)

    except Exception as e:
        job.attempts += 1
        job.last_error = str(e)
        job.updated_at = datetime.now(timezone.utc)
        if job.attempts >= MAX_DISPATCH_ATTEMPTS:
            job.status = "FAILED"
            logger.error("Deferred job exception reached max attempts", job_id=job.id, error=str(e))
        else:
            job.status = "PENDING"
            logger.warning("Deferred job exception during dispatch; returned to PENDING", job_id=job.id, error=str(e))

    db.commit()
    db.refresh(job)
    return job


def dispatch_due_deferred_jobs(db: Session, batch_size: int = 50) -> List[DeferredJob]:
    """
    Find eligible PENDING deferred jobs whose scheduled_for timestamp has passed,
    or stale SCHEDULED jobs, and dispatch them with bounded batch processing.
    """
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(minutes=CLAIM_TIMEOUT_MINUTES)

    # Bounded query for eligible candidates
    eligible_jobs = (
        db.query(DeferredJob)
        .filter(
            or_(
                (DeferredJob.status == "PENDING") & (DeferredJob.scheduled_for <= now),
                (DeferredJob.status == "SCHEDULED") & (DeferredJob.updated_at <= stale_threshold)
            )
        )
        .order_by(DeferredJob.scheduled_for.asc())
        .limit(batch_size)
        .all()
    )

    if not eligible_jobs:
        return []

    logger.info("Discovered eligible deferred jobs for dispatch", count=len(eligible_jobs))
    dispatched = []

    for job in eligible_jobs:
        result = dispatch_single_job(db, job.id)
        if result and result.status == "DISPATCHED":
            dispatched.append(result)

    return dispatched
