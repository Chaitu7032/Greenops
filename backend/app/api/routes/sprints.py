from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.sprint import Sprint
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintResponse, SprintBudgetSummary, BurnDownPoint
from app.services.budget_service import get_sprint_budget_summary, get_sprint_burn_down

router = APIRouter(prefix="/api/v1/sprints", tags=["Sprints"])


@router.get("", response_model=List[SprintResponse])
def list_sprints(db: Session = Depends(get_db)):
    return db.query(Sprint).order_by(Sprint.start_date.desc()).all()


@router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
def create_sprint(sprint_in: SprintCreate, db: Session = Depends(get_db)):
    sprint = Sprint(**sprint_in.model_dump())
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint


@router.get("/{id}", response_model=SprintResponse)
def get_sprint(id: str, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == id).first()
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return sprint


@router.get("/{id}/budget", response_model=SprintBudgetSummary)
def get_sprint_budget(id: str, db: Session = Depends(get_db)):
    summary = get_sprint_budget_summary(db, id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return summary


@router.get("/{id}/burn-down", response_model=List[BurnDownPoint])
def get_sprint_burn_down_chart(id: str, db: Session = Depends(get_db)):
    return get_sprint_burn_down(db, id)
