import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.repository import Repository
from app.models.pipeline_run import PipelineRun
from app.models.deferred_job import DeferredJob
from app.services.scheduler_service import (
    schedule_deferred_job,
    claim_deferred_job,
    dispatch_single_job,
    dispatch_due_deferred_jobs,
    CLAIM_TIMEOUT_MINUTES,
    MAX_DISPATCH_ATTEMPTS,
)


@pytest.fixture
def sample_repo_and_run(db_session: Session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()

    repo = Repository(
        organization_id=org.id,
        github_repo_id=999,
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
    )
    db_session.add(repo)
    db_session.commit()

    run = PipelineRun(
        repository_id=repo.id,
        organization_id=org.id,
        pr_number=42,
        commit_sha="abcd1234ef",
        workflow_name="CI",
        estimated_duration_seconds=Decimal("120.0"),
        estimated_cost_usd=Decimal("0.0160"),
        estimated_energy_kwh=Decimal("0.0015"),
        estimated_carbon_g=Decimal("0.5700"),
        urgency="ROUTINE",
        policy_decision="DEFERRED",
        execution_status="PENDING",
    )
    db_session.add(run)
    db_session.commit()

    return repo, run


def test_eligible_job_discovered_and_dispatched(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    # Create job scheduled 10 minutes ago
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="High carbon intensity",
        delay_minutes=-10,
    )
    assert job.status == "PENDING"

    dispatched = dispatch_due_deferred_jobs(db_session)
    assert len(dispatched) == 1
    assert dispatched[0].id == job.id

    db_session.refresh(job)
    assert job.status == "DISPATCHED"
    assert job.attempts == 1


def test_future_scheduled_job_is_not_dispatched_early(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    # Scheduled 60 minutes in the future
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Peak grid hours",
        delay_minutes=60,
    )

    dispatched = dispatch_due_deferred_jobs(db_session)
    assert len(dispatched) == 0

    db_session.refresh(job)
    assert job.status == "PENDING"
    assert job.attempts == 0


def test_completed_or_cancelled_job_is_skipped(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Routine run",
        delay_minutes=-5,
    )
    job.status = "COMPLETED"
    db_session.commit()

    dispatched = dispatch_due_deferred_jobs(db_session)
    assert len(dispatched) == 0

    db_session.refresh(job)
    assert job.status == "COMPLETED"


def test_empty_eligible_job_set_handled_cleanly(db_session: Session):
    # No jobs in database
    dispatched = dispatch_due_deferred_jobs(db_session)
    assert dispatched == []


def test_repeated_scheduler_runs_do_not_duplicate_dispatch(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Routine run",
        delay_minutes=-5,
    )

    # First scheduler tick
    first_run = dispatch_due_deferred_jobs(db_session)
    assert len(first_run) == 1
    assert first_run[0].status == "DISPATCHED"

    # Second scheduler tick immediately following
    second_run = dispatch_due_deferred_jobs(db_session)
    assert len(second_run) == 0

    db_session.refresh(job)
    assert job.attempts == 1


def test_concurrent_claim_atomicity(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Testing concurrency",
        delay_minutes=-5,
    )

    # First worker claims
    first_claim = claim_deferred_job(db_session, job.id)
    assert first_claim is True

    # Second worker simultaneously attempts claim for same job
    second_claim = claim_deferred_job(db_session, job.id)
    assert second_claim is False

    db_session.refresh(job)
    assert job.status == "SCHEDULED"


def test_dispatch_failure_recovers_to_pending_before_max_attempts(
    db_session: Session, sample_repo_and_run, monkeypatch
):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Fail test",
        delay_minutes=-5,
    )

    # Mock github_service to return failure (e.g. transient 500 error from GitHub)
    from app.services.github_service import github_service
    monkeypatch.setattr(github_service, "dispatch_workflow", lambda **kwargs: False)

    res = dispatch_single_job(db_session, job.id)
    assert res is not None

    db_session.refresh(job)
    # Attempt failed, returned to PENDING for subsequent scheduler retry
    assert job.status == "PENDING"
    assert job.attempts == 1
    assert "GitHub Actions dispatch returned failure" in job.last_error


def test_dispatch_failure_marks_failed_after_max_attempts(
    db_session: Session, sample_repo_and_run, monkeypatch
):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Exhaustion test",
        delay_minutes=-5,
    )
    job.attempts = MAX_DISPATCH_ATTEMPTS - 1
    db_session.commit()

    from app.services.github_service import github_service
    monkeypatch.setattr(github_service, "dispatch_workflow", lambda **kwargs: False)

    res = dispatch_single_job(db_session, job.id)
    db_session.refresh(job)

    assert job.status == "FAILED"
    assert job.attempts == MAX_DISPATCH_ATTEMPTS


def test_stale_scheduled_job_is_recovered_after_timeout(db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Worker crash test",
        delay_minutes=-10,
    )
    # Simulate worker claimed it but crashed before dispatching
    job.status = "SCHEDULED"
    job.updated_at = datetime.now(timezone.utc) - timedelta(minutes=CLAIM_TIMEOUT_MINUTES + 1)
    db_session.commit()

    # Scheduler runs: stale job should be reclaimed and dispatched
    dispatched = dispatch_due_deferred_jobs(db_session)
    assert len(dispatched) == 1
    assert dispatched[0].id == job.id

    db_session.refresh(job)
    assert job.status == "DISPATCHED"


def test_manual_dispatch_endpoint_compatibility(client, db_session: Session, sample_repo_and_run):
    repo, run = sample_repo_and_run
    job = schedule_deferred_job(
        db=db_session,
        pipeline_run_id=run.id,
        repository_id=repo.id,
        pr_number=42,
        workflow_name="CI",
        target_ref="main",
        reason="Manual dispatch test",
        delay_minutes=30,
    )

    response = client.post(f"/api/v1/deferred-jobs/{job.id}/dispatch")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DISPATCHED"
    assert data["attempts"] == 1

    # Second manual attempt should return 400 because already DISPATCHED
    duplicate_res = client.post(f"/api/v1/deferred-jobs/{job.id}/dispatch")
    assert duplicate_res.status_code == 400
    assert "already in terminal or dispatched state" in duplicate_res.json()["detail"]
