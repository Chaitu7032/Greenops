from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.repository import Repository
from app.models.pipeline_run import PipelineRun
from app.schemas.repository import RepositoryCreate, RepositoryUpdate, RepositoryResponse
from app.schemas.pipeline import PipelineRunResponse

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])


@router.get("", response_model=List[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).order_by(Repository.full_name).all()


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(repo_in: RepositoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Repository).filter(Repository.full_name == repo_in.full_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Repository already registered")
    repo = Repository(**repo_in.model_dump())
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.get("/{id}", response_model=RepositoryResponse)
def get_repository(id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo


@router.get("/{id}/pipelines", response_model=List[PipelineRunResponse])
def get_repository_pipelines(id: str, limit: int = 50, db: Session = Depends(get_db)):
    runs = (
        db.query(PipelineRun)
        .filter(PipelineRun.repository_id == id)
        .order_by(PipelineRun.created_at.desc())
        .limit(limit)
        .all()
    )
    res = []
    for r in runs:
        item = PipelineRunResponse.model_validate(r)
        item.repository_name = r.repository.name if r.repository else None
        res.append(item)
    return res
