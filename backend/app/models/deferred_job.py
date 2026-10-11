import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, utc_now

if TYPE_CHECKING:
    from app.models.pipeline_run import PipelineRun
    from app.models.repository import Repository


class DeferredJob(Base):
    __tablename__ = "deferred_jobs"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_run_id: Mapped[str] = mapped_column(GUID, ForeignKey("pipeline_runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    repository_id: Mapped[str] = mapped_column(GUID, ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False)

    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_for: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="ROUTINE", nullable=False) # HOTFIX, BLOCKING, ROUTINE
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False) # PENDING, SCHEDULED, DISPATCHED, COMPLETED, FAILED, CANCELLED
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    pipeline_run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="deferred_job")
    repository: Mapped["Repository"] = relationship("Repository", back_populates="deferred_jobs")
