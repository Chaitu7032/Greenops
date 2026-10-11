from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DeferredJobBase(BaseModel):
    pipeline_run_id: str
    repository_id: str
    pr_number: int
    workflow_name: str
    target_ref: str
    scheduled_for: datetime
    reason: str
    priority: str = "ROUTINE"
    status: str = "PENDING"
    attempts: int = 0
    last_error: Optional[str] = None


class DeferredJobResponse(DeferredJobBase):
    id: str
    created_at: datetime
    updated_at: datetime
    repository_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
