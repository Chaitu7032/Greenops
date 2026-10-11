from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str
    monthly_budget_usd: Decimal = Decimal("500.0000")
    carbon_budget_kg: Decimal = Decimal("100.0000")
    active_sprint_id: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    monthly_budget_usd: Optional[Decimal] = None
    carbon_budget_kg: Optional[Decimal] = None
    active_sprint_id: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
