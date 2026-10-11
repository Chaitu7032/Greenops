from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PolicyBase(BaseModel):
    organization_id: Optional[str] = None
    repository_id: Optional[str] = None
    name: str = "Standard Budget & Carbon Policy"
    max_cost_per_run_usd: Decimal = Decimal("1.0000")
    max_carbon_per_run_g: Decimal = Decimal("250.00")
    budget_warning_percent: Decimal = Decimal("80.00")
    budget_block_percent: Decimal = Decimal("100.00")
    high_grid_intensity_threshold: Decimal = Decimal("350.00")
    allow_deferred_execution: bool = True


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    max_cost_per_run_usd: Optional[Decimal] = None
    max_carbon_per_run_g: Optional[Decimal] = None
    budget_warning_percent: Optional[Decimal] = None
    budget_block_percent: Optional[Decimal] = None
    high_grid_intensity_threshold: Optional[Decimal] = None
    allow_deferred_execution: Optional[bool] = None


class PolicyResponse(PolicyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
