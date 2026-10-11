import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.sprint import Sprint
    from app.models.budget_ledger import SprintBudgetLedger
    from app.models.deferred_job import DeferredJob


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id: Mapped[str] = mapped_column(GUID, ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False)
    organization_id: Mapped[str] = mapped_column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    sprint_id: Mapped[Optional[str]] = mapped_column(GUID, ForeignKey("sprints.id", ondelete="SET NULL"), index=True, nullable=True)

    pr_number: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    commit_sha: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    author: Mapped[str] = mapped_column(String(100), default="unknown", nullable=False)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    workflow_name: Mapped[str] = mapped_column(String(255), default="CI", nullable=False)
    run_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), default="pull_request", nullable=False)

    # Diff analysis metrics
    changed_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    test_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    documentation_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    configuration_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    integration_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Estimated vs Actual Telemetry
    estimated_duration_seconds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    actual_duration_seconds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    estimated_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    actual_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)

    estimated_energy_kwh: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    actual_energy_kwh: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)

    grid_region: Mapped[str] = mapped_column(String(100), default="US-EAST", nullable=False)
    grid_intensity_gco2_kwh: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("300.00"), nullable=False)

    estimated_carbon_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    actual_carbon_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)

    # Governance & Policy Decision
    urgency: Mapped[str] = mapped_column(String(50), default="ROUTINE", nullable=False) # HOTFIX, BLOCKING, ROUTINE
    policy_decision: Mapped[str] = mapped_column(String(50), default="APPROVED", nullable=False) # APPROVED, DEFERRED, FLAGGED
    policy_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False) # PENDING, RUNNING, COMPLETED, DEFERRED, CANCELLED, FAILED

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="pipeline_runs")
    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint", back_populates="pipeline_runs")
    ledger_entries: Mapped[List["SprintBudgetLedger"]] = relationship("SprintBudgetLedger", back_populates="pipeline_run", cascade="all, delete-orphan")
    deferred_job: Mapped[Optional["DeferredJob"]] = relationship("DeferredJob", back_populates="pipeline_run", uselist=False, cascade="all, delete-orphan")
