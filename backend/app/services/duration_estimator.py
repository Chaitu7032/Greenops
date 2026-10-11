import statistics
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.pipeline_run import PipelineRun
from app.services.diff_analyzer import DiffAnalysisResult


class DurationEstimateResult:
    def __init__(self, estimated_seconds: Decimal, method: str, confidence: float):
        self.estimated_seconds = estimated_seconds
        self.method = method  # "historical_median" or "heuristic"
        self.confidence = confidence

    def to_dict(self) -> Dict:
        return {
            "estimated_seconds": float(self.estimated_seconds),
            "method": self.method,
            "confidence": self.confidence,
        }


def estimate_duration_heuristic(diff: DiffAnalysisResult) -> Decimal:
    """
    Deterministic conservative heuristic:
    Base: 60s
    + 12s per source file
    + 20s per test file
    + 45s per integration test file
    + 30s per CI/infra configuration file
    + 0.05s per line modified (added + deleted)
    Capped at 3600s (1 hour).
    """
    total_lines = diff.lines_added + diff.lines_deleted
    seconds = (
        60.0
        + (diff.source_files_count * 12.0)
        + (diff.test_files_count * 20.0)
        + (diff.integration_files_count * 45.0)
        + (diff.configuration_files_count * 30.0)
        + (total_lines * 0.05)
    )

    # Documentation-only optimization: if only doc files changed, baseline is minimal
    if (
        diff.documentation_files_count > 0
        and diff.source_files_count == 0
        and diff.test_files_count == 0
        and diff.integration_files_count == 0
        and diff.configuration_files_count == 0
    ):
        seconds = max(30.0, diff.documentation_files_count * 5.0)

    clamped_seconds = min(3600.0, max(20.0, seconds))
    return Decimal(str(round(clamped_seconds, 2)))


def estimate_duration(
    db: Session,
    repository_id: str,
    diff: DiffAnalysisResult,
    workflow_name: str = "CI"
) -> DurationEstimateResult:
    """
    Look up historical actual durations for the repository and workflow.
    If >= 3 runs exist, use median of past runs adjusted conservatively for diff size.
    Otherwise fallback to heuristic.
    """
    historical_runs = (
        db.query(PipelineRun.actual_duration_seconds)
        .filter(
            PipelineRun.repository_id == repository_id,
            PipelineRun.workflow_name == workflow_name,
            PipelineRun.actual_duration_seconds.isnot(None),
            PipelineRun.actual_duration_seconds > 0,
            PipelineRun.execution_status == "COMPLETED"
        )
        .order_by(PipelineRun.created_at.desc())
        .limit(20)
        .all()
    )

    run_durations = [float(r[0]) for r in historical_runs if r[0] is not None]

    if len(run_durations) >= 3:
        hist_median = statistics.median(run_durations)
        confidence = min(0.95, round(0.40 + (len(run_durations) * 0.03), 2))

        # Adjust slightly if diff is significantly larger than typical
        heuristic_val = float(estimate_duration_heuristic(diff))
        if heuristic_val > hist_median * 1.8:
            blended = (hist_median * 0.6) + (heuristic_val * 0.4)
            return DurationEstimateResult(
                estimated_seconds=Decimal(str(round(blended, 2))),
                method="historical_median_adjusted",
                confidence=confidence,
            )

        return DurationEstimateResult(
            estimated_seconds=Decimal(str(round(hist_median, 2))),
            method="historical_median",
            confidence=confidence,
        )

    # Fallback to heuristic
    heuristic_seconds = estimate_duration_heuristic(diff)
    return DurationEstimateResult(
        estimated_seconds=heuristic_seconds,
        method="heuristic",
        confidence=0.35,
    )
