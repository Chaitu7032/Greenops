from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class WebhookEventResponse(BaseModel):
    id: str
    github_delivery_id: str
    event_type: str
    processed: bool
    processing_error: Optional[str] = None
    received_at: datetime
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WebhookProcessingResult(BaseModel):
    status: str
    message: str
    event_type: str
    delivery_id: str
    pipeline_run_id: Optional[str] = None
    policy_decision: Optional[str] = None
    reason: Optional[str] = None
