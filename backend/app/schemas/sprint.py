from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SprintBase(BaseModel):
    name: str
    external_sprint_id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    budget_usd: Decimal = Decimal("100.0000")
    carbon_budget_kg: Decimal = Decimal("25.0000")
    status: str = "ACTIVE"


class SprintCreate(SprintBase):
    organization_id: str


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    budget_usd: Optional[Decimal] = None
    carbon_budget_kg: Optional[Decimal] = None
    status: Optional[str] = None


class SprintResponse(SprintBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SprintBudgetSummary(BaseModel):
    sprint_id: str
    sprint_name: str
    budget_usd: Decimal
    consumed_usd: Decimal
    remaining_usd: Decimal
    percentage_consumed: float
    over_budget: bool
    overspend_usd: Decimal

    carbon_budget_kg: Decimal
    consumed_carbon_kg: Decimal
    remaining_carbon_kg: Decimal
    carbon_percentage_consumed: float
    carbon_over_budget: bool
    carbon_overspend_kg: Decimal


class BurnDownPoint(BaseModel):
    date: str
    budget_remaining_usd: float
    actual_spent_usd: float
    ideal_burn_usd: float
