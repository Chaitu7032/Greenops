import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.repository import Repository


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[Optional[str]] = mapped_column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True)
    repository_id: Mapped[Optional[str]] = mapped_column(GUID, ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=True)

    name: Mapped[str] = mapped_column(String(100), default="Standard Budget & Carbon Policy", nullable=False)
    max_cost_per_run_usd: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1.0000"), nullable=False)
    max_carbon_per_run_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("250.00"), nullable=False)
    budget_warning_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("80.00"), nullable=False)
    budget_block_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("100.00"), nullable=False)
    high_grid_intensity_threshold: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("350.00"), nullable=False)
    allow_deferred_execution: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="policies")
    repository: Mapped[Optional["Repository"]] = relationship("Repository", back_populates="policies")
