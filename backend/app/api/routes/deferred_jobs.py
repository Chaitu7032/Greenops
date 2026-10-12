from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.deferred_job import DeferredJob
from app.models.repository import Repository
from app.schemas.deferred_job import DeferredJobResponse
from app.services.scheduler_service import dispatch_single_job

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

    if job.status in ("DISPATCHED", "COMPLETED"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job already in terminal or dispatched state: {job.status}"
        )

    dispatched_job = dispatch_single_job(
        db=db,
        job_id=job.id,
        trigger_reason="Manual GreenOps REST Dispatch"
    )

    if not dispatched_job:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is currently claimed or locked by an active background worker."
        )

    item = DeferredJobResponse.model_validate(dispatched_job)
    repo = db.query(Repository).filter(Repository.id == dispatched_job.repository_id).first()
    item.repository_name = repo.name if repo else None
    return item
