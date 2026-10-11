from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.pipeline_run import PipelineRun
from app.schemas.pipeline import PipelineRunResponse

router = APIRouter(prefix="/api/v1/pipelines", tags=["Pipelines"])


@router.get("", response_model=List[PipelineRunResponse])
def list_pipelines(
    repository_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
    policy_decision: Optional[str] = None,
    execution_status: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(PipelineRun)
    if repository_id:
        query = query.filter(PipelineRun.repository_id == repository_id)
    if sprint_id:
        query = query.filter(PipelineRun.sprint_id == sprint_id)
    if policy_decision:
        query = query.filter(PipelineRun.policy_decision == policy_decision.upper())
    if execution_status:
        query = query.filter(PipelineRun.execution_status == execution_status.upper())

    runs = query.order_by(PipelineRun.created_at.desc()).offset(offset).limit(limit).all()

    output = []
    for r in runs:
        item = PipelineRunResponse.model_validate(r)
        item.repository_name = r.repository.name if r.repository else None
        if r.actual_duration_seconds is not None and r.estimated_duration_seconds is not None:
            item.duration_variance_seconds = r.actual_duration_seconds - r.estimated_duration_seconds
        if r.actual_cost_usd is not None and r.estimated_cost_usd is not None:
            item.cost_variance_usd = r.actual_cost_usd - r.estimated_cost_usd
        if r.actual_carbon_g is not None and r.estimated_carbon_g is not None:
            item.carbon_variance_g = r.actual_carbon_g - r.estimated_carbon_g
        output.append(item)

    return output


@router.get("/{id}", response_model=PipelineRunResponse)
def get_pipeline_run(id: str, db: Session = Depends(get_db)):
    run = db.query(PipelineRun).filter(PipelineRun.id == id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run not found")
    item = PipelineRunResponse.model_validate(run)
    item.repository_name = run.repository.name if run.repository else None
    if run.actual_duration_seconds is not None and run.estimated_duration_seconds is not None:
        item.duration_variance_seconds = run.actual_duration_seconds - run.estimated_duration_seconds
    if run.actual_cost_usd is not None and run.estimated_cost_usd is not None:
        item.cost_variance_usd = run.actual_cost_usd - run.estimated_cost_usd
    if run.actual_carbon_g is not None and run.estimated_carbon_g is not None:
        item.carbon_variance_g = run.actual_carbon_g - run.estimated_carbon_g
    return item
