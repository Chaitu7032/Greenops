from decimal import Decimal
from typing import Optional
from app.models.pipeline_run import PipelineRun
from app.schemas.sprint import SprintBudgetSummary

SCORECARD_MARKER = "<!-- greenops-scorecard -->"


def generate_pr_scorecard_markdown(
    pipeline_run: PipelineRun,
    sprint_summary: Optional[SprintBudgetSummary] = None,
    estimation_method: str = "heuristic",
    confidence: float = 0.35,
    is_actual: bool = False,
) -> str:
    """
    Generate professional, GitHub-compatible Markdown scorecard for PR comments.
    """
    # Decision badge
    decision = pipeline_run.policy_decision.upper()
    if decision == "APPROVED":
        badge = "🟢 **APPROVED**"
    elif decision == "DEFERRED":
        badge = "🟡 **DEFERRED (Queued for Low-Carbon Window)**"
    else:
        badge = "🔴 **FLAGGED (Requires Review)**"

    # Durations
    if is_actual and pipeline_run.actual_duration_seconds:
        dur_min = float(pipeline_run.actual_duration_seconds) / 60.0
        dur_label = f"{dur_min:.1f} min *(Actual)*"
        cost_val = f"${pipeline_run.actual_cost_usd:.4f}" if pipeline_run.actual_cost_usd else "$0.00"
        energy_val = f"{pipeline_run.actual_energy_kwh:.4f} kWh" if pipeline_run.actual_energy_kwh else "0 kWh"
        carbon_val = f"{pipeline_run.actual_carbon_g:.1f} gCO₂e" if pipeline_run.actual_carbon_g else "0 g"
    else:
        dur_min = float(pipeline_run.estimated_duration_seconds or 0) / 60.0
        dur_label = f"{dur_min:.1f} min *(Est. via {estimation_method})*"
        cost_val = f"${pipeline_run.estimated_cost_usd:.4f}" if pipeline_run.estimated_cost_usd else "$0.00"
        energy_val = f"{pipeline_run.estimated_energy_kwh:.4f} kWh" if pipeline_run.estimated_energy_kwh else "0 kWh"
        carbon_val = f"{pipeline_run.estimated_carbon_g:.1f} gCO₂e" if pipeline_run.estimated_carbon_g else "0 g"

    # Sprint block
    if sprint_summary:
        sprint_block = f"""
### 📊 Sprint Budget Impact ({sprint_summary.sprint_name})
- **Cloud Budget:** ${sprint_summary.consumed_usd:.2f} / ${sprint_summary.budget_usd:.2f} ({sprint_summary.percentage_consumed}% consumed)
- **Carbon Budget:** {sprint_summary.consumed_carbon_kg:.2f} kg / {sprint_summary.carbon_budget_kg:.2f} kg ({sprint_summary.carbon_percentage_consumed}% consumed)
"""
    else:
        sprint_block = "_No active sprint linked to this execution._\n"

    # Variance row if both estimated and actual are present
    variance_block = ""
    if pipeline_run.actual_duration_seconds and pipeline_run.estimated_duration_seconds:
        dur_var = float(pipeline_run.actual_duration_seconds - pipeline_run.estimated_duration_seconds)
        cost_var = float((pipeline_run.actual_cost_usd or 0) - (pipeline_run.estimated_cost_usd or 0))
        carbon_var = float((pipeline_run.actual_carbon_g or 0) - (pipeline_run.estimated_carbon_g or 0))
        variance_block = f"""
### 🎯 Telemetry Variance (Actual vs Estimate)
| Metric | Estimate | Actual | Variance |
|---|---|---|---|
| Duration | {float(pipeline_run.estimated_duration_seconds)/60:.1f} min | {float(pipeline_run.actual_duration_seconds)/60:.1f} min | {dur_var:+.1f}s |
| Compute Cost | ${pipeline_run.estimated_cost_usd or 0:.4f} | ${pipeline_run.actual_cost_usd or 0:.4f} | ${cost_var:+.4f} |
| Carbon | {pipeline_run.estimated_carbon_g or 0:.1f} g | {pipeline_run.actual_carbon_g or 0:.1f} g | {carbon_var:+.1f} g |
"""

    scorecard_md = f"""{SCORECARD_MARKER}
## 🌱 GreenOps FinOps & Carbon CI Scorecard

### Decision: {badge}
**Reason:** {pipeline_run.policy_reason or "Automated policy evaluation completed."}

---

### ⚡ Pipeline Telemetry ({'Actual' if is_actual else 'Estimated'})
| Metric | Value |
|---|---:|
| **CI Execution Duration** | {dur_label} |
| **Cloud Compute Cost** | {cost_val} |
| **Energy Consumption** | {energy_val} |
| **Estimated Scope-2 Carbon** | {carbon_val} |
| **Regional Grid Intensity** | {pipeline_run.grid_intensity_gco2_kwh:.1f} gCO₂e/kWh ({pipeline_run.grid_region}) |
| **PR Urgency Level** | `{pipeline_run.urgency}` |

{sprint_block}
{variance_block}
---
*Automated Gatekeeper by [GreenOps](https://github.com) • FinOps & Sustainable Software Engineering*
"""
    return scorecard_md
