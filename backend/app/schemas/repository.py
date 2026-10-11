from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RepositoryBase(BaseModel):
    owner: str
    name: str
    full_name: str
    default_branch: str = "main"
    runner_type: str = "ubuntu-latest"
    runner_region: str = "US-EAST"
    cpu_cores: int = 2
    memory_gb: Decimal = Decimal("7.00")
    cost_per_minute: Decimal = Decimal("0.008000")
    power_idle_watts: Decimal = Decimal("10.00")
    power_max_watts: Decimal = Decimal("50.00")
    pue: Decimal = Decimal("1.150")


class RepositoryCreate(RepositoryBase):
    organization_id: str
    github_repo_id: int


class RepositoryUpdate(BaseModel):
    owner: Optional[str] = None
    name: Optional[str] = None
    runner_region: Optional[str] = None
    cost_per_minute: Optional[Decimal] = None
    pue: Optional[Decimal] = None


class RepositoryResponse(RepositoryBase):
    id: str
    organization_id: str
    github_repo_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
