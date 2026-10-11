from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.deferred_job import DeferredJob
from app.models.repository import Repository
from app.schemas.deferred_job import DeferredJobResponse
from app.services.github_service import github_service

router = APIRouter(prefix="/api/v1/deferred-jobs", tags=["Deferred Jobs"])


@router.get("", response_model=List[DeferredJobResponse])
def list_deferred_jobs(status_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(DeferredJob)
    if status_filter:
        query = query.filter(DeferredJob.status == status_filter.upper())
    jobs = query.order_by(DeferredJob.scheduled_for.asc()).all()

    output = []
    for j in jobs:
        item = DeferredJobResponse.model_validate(j)
        item.repository_name = j.repository.name if j.repository else None
        output.append(item)
    return output


@router.get("/{id}", response_model=DeferredJobResponse)
def get_deferred_job(id: str, db: Session = Depends(get_db)):
    job = db.query(DeferredJob).filter(DeferredJob.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deferred job not found")
    item = DeferredJobResponse.model_validate(job)
    item.repository_name = job.repository.name if job.repository else None
    return item


@router.post("/{id}/dispatch", response_model=DeferredJobResponse)
def manually_dispatch_job(id: str, db: Session = Depends(get_db)):
    job = db.query(DeferredJob).filter(DeferredJob.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deferred job not found")

    repo = db.query(Repository).filter(Repository.id == job.repository_id).first()
    if not repo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Repository not found")

    workflow_file = f"{job.workflow_name.lower().replace(' ', '-')}.yml"
    success = github_service.dispatch_workflow(
        owner=repo.owner,
        repo=repo.name,
        workflow_id=workflow_file,
        ref=job.target_ref,
        inputs={"pr_number": str(job.pr_number), "trigger_reason": "Manual GreenOps Dispatch"}
    )

    if success:
        job.status = "DISPATCHED"
        job.attempts += 1
    else:
        job.attempts += 1
        job.last_error = "Manual dispatch failed to trigger GitHub Actions"

    db.commit()
    db.refresh(job)

    item = DeferredJobResponse.model_validate(job)
    item.repository_name = repo.name
    return item
