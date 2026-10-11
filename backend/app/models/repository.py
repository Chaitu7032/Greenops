import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.pipeline_run import PipelineRun
    from app.models.policy import Policy
    from app.models.deferred_job import DeferredJob


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)

    # Runner Compute & Power Profiles
    runner_type: Mapped[str] = mapped_column(String(100), default="ubuntu-latest", nullable=False)
    runner_region: Mapped[str] = mapped_column(String(100), default="US-EAST", nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    memory_gb: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("7.00"), nullable=False)
    cost_per_minute: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0.008000"), nullable=False)
    power_idle_watts: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("10.00"), nullable=False)
    power_max_watts: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("50.00"), nullable=False)
    pue: Mapped[Decimal] = mapped_column(Numeric(6, 3), default=Decimal("1.150"), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="repositories")
    pipeline_runs: Mapped[List["PipelineRun"]] = relationship("PipelineRun", back_populates="repository", cascade="all, delete-orphan")
    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="repository", cascade="all, delete-orphan")
    deferred_jobs: Mapped[List["DeferredJob"]] = relationship("DeferredJob", back_populates="repository", cascade="all, delete-orphan")
