from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.pipeline import PipelineRunResponse
from app.schemas.deferred_job import DeferredJobResponse


class DashboardOverview(BaseModel):
    # Financial & Carbon Cards
    financial_budget_usd: Decimal
    financial_consumed_usd: Decimal
    financial_remaining_usd: Decimal
    financial_percentage: float
    financial_over_budget: bool

    carbon_budget_kg: Decimal
    carbon_consumed_kg: Decimal
    carbon_remaining_kg: Decimal
    carbon_percentage: float
    carbon_over_budget: bool

    total_runs_count: int
    approved_runs_count: int
    deferred_runs_count: int
    flagged_runs_count: int

    estimated_savings_usd: Decimal
    carbon_avoided_kg: Decimal

    grid_region: str
    current_grid_intensity: Decimal
    is_grid_data_stale: bool
    is_demo_data: bool = False


class RepositoryRanking(BaseModel):
    id: str
    name: str
    owner: str
    full_name: str
    total_runs: int
    total_cost_usd: Decimal
    total_carbon_kg: Decimal
    deferred_count: int
    avg_duration_minutes: float


class CostTimeSeriesPoint(BaseModel):
    date: str
    cost_usd: float
    budget_limit_usd: float


class CarbonTimeSeriesPoint(BaseModel):
    date: str
    emissions_kg: float
    grid_intensity_gco2: float


class SavingsAnalysis(BaseModel):
    total_savings_usd: Decimal
    total_carbon_avoided_kg: Decimal
    deferred_jobs_executed: int
    green_window_efficiency_pct: float
    prevented_unnecessary_runs: int
