import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.sprint import Sprint
    from app.models.pipeline_run import PipelineRun


class SprintBudgetLedger(Base):
    __tablename__ = "sprint_budget_ledger"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    sprint_id: Mapped[str] = mapped_column(GUID, ForeignKey("sprints.id", ondelete="CASCADE"), index=True, nullable=False)
    pipeline_run_id: Mapped[Optional[str]] = mapped_column(GUID, ForeignKey("pipeline_runs.id", ondelete="SET NULL"), index=True, nullable=True)

    amount_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    carbon_g: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(50), default="ACTUAL_DEBIT", nullable=False) # ESTIMATED_HOLD, ACTUAL_DEBIT, REVERSAL

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="ledger_entries")
    pipeline_run: Mapped[Optional["PipelineRun"]] = relationship("PipelineRun", back_populates="ledger_entries")
