import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.sprint import Sprint
    from app.models.policy import Policy


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    monthly_budget_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("500.0000"))
    carbon_budget_kg: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("100.0000"))
    active_sprint_id: Mapped[Optional[str]] = mapped_column(GUID, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    repositories: Mapped[List["Repository"]] = relationship("Repository", back_populates="organization", cascade="all, delete-orphan")
    sprints: Mapped[List["Sprint"]] = relationship("Sprint", back_populates="organization", cascade="all, delete-orphan")
    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="organization", cascade="all, delete-orphan")
