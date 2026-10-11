import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.pipeline_run import PipelineRun
    from app.models.budget_ledger import SprintBudgetLedger


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    external_sprint_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    budget_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("100.0000"), nullable=False)
    carbon_budget_kg: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("25.0000"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False) # ACTIVE, COMPLETED, PLANNED

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="sprints")
    pipeline_runs: Mapped[List["PipelineRun"]] = relationship("PipelineRun", back_populates="sprint")
    ledger_entries: Mapped[List["SprintBudgetLedger"]] = relationship("SprintBudgetLedger", back_populates="sprint", cascade="all, delete-orphan")
