from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])


@router.get("", response_model=List[PolicyResponse])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).order_by(Policy.created_at.desc()).all()


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(pol_in: PolicyCreate, db: Session = Depends(get_db)):
    policy = Policy(**pol_in.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/{id}", response_model=PolicyResponse)
def get_policy(id: str, db: Session = Depends(get_db)):
    pol = db.query(Policy).filter(Policy.id == id).first()
    if not pol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return pol


@router.put("/{id}", response_model=PolicyResponse)
def update_policy(id: str, pol_in: PolicyUpdate, db: Session = Depends(get_db)):
    pol = db.query(Policy).filter(Policy.id == id).first()
    if not pol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    for field, val in pol_in.model_dump(exclude_unset=True).items():
        setattr(pol, field, val)
    db.commit()
    db.refresh(pol)
    return pol
