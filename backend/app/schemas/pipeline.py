from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PipelineRunBase(BaseModel):
    repository_id: str
    organization_id: str
    sprint_id: Optional[str] = None
    pr_number: Optional[int] = None
    commit_sha: str
    author: str = "unknown"
    workflow_id: Optional[str] = None
    workflow_name: str = "CI"
    run_id: Optional[int] = None
    trigger_type: str = "pull_request"

    changed_files_count: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    source_files_count: int = 0
    test_files_count: int = 0
    documentation_files_count: int = 0
    configuration_files_count: int = 0
    integration_files_count: int = 0

    estimated_duration_seconds: Optional[Decimal] = None
    actual_duration_seconds: Optional[Decimal] = None

    estimated_cost_usd: Optional[Decimal] = None
    actual_cost_usd: Optional[Decimal] = None

    estimated_energy_kwh: Optional[Decimal] = None
    actual_energy_kwh: Optional[Decimal] = None

    grid_region: str = "US-EAST"
    grid_intensity_gco2_kwh: Decimal = Decimal("300.00")

    estimated_carbon_g: Optional[Decimal] = None
    actual_carbon_g: Optional[Decimal] = None

    urgency: str = "ROUTINE"
    policy_decision: str = "APPROVED"
    policy_reason: Optional[str] = None
    execution_status: str = "PENDING"


class PipelineRunCreate(PipelineRunBase):
    pass


class PipelineRunResponse(PipelineRunBase):
    id: str
    created_at: datetime
    updated_at: datetime
    repository_name: Optional[str] = None
    duration_variance_seconds: Optional[Decimal] = None
    cost_variance_usd: Optional[Decimal] = None
    carbon_variance_g: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)
