from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.models.repository import Repository
from app.models.organization import Organization
from app.services.budget_service import get_sprint_budget_summary


class PolicyDecisionResult:
    def __init__(
        self,
        decision: str,  # "APPROVED", "DEFERRED", "FLAGGED"
        reason: str,
        rule_violated: Optional[str] = None,
        can_defer: bool = False,
        deferral_delay_minutes: int = 0
    ):
        self.decision = decision
        self.reason = reason
        self.rule_violated = rule_violated
        self.can_defer = can_defer
        self.deferral_delay_minutes = deferral_delay_minutes

    def to_dict(self):
        return {
            "decision": self.decision,
            "reason": self.reason,
            "rule_violated": self.rule_violated,
            "can_defer": self.can_defer,
            "deferral_delay_minutes": self.deferral_delay_minutes,
        }


def get_applicable_policy(db: Session, repository_id: str, organization_id: str) -> Policy:
    """Find repo-specific policy or fallback to organization policy, or create sensible default."""
    policy = db.query(Policy).filter(Policy.repository_id == repository_id).first()
    if not policy:
        policy = db.query(Policy).filter(Policy.organization_id == organization_id).first()
    if not policy:
        policy = Policy(
            organization_id=organization_id,
            name="Default Standard Policy",
            max_cost_per_run_usd=Decimal("1.5000"),
            max_carbon_per_run_g=Decimal("250.00"),
            budget_warning_percent=Decimal("80.00"),
            budget_block_percent=Decimal("100.00"),
            high_grid_intensity_threshold=Decimal("350.00"),
            allow_deferred_execution=True,
        )
    return policy


def evaluate_policy_gatekeeper(
    db: Session,
    repository_id: str,
    organization_id: str,
    sprint_id: Optional[str],
    estimated_cost_usd: Decimal,
    estimated_carbon_g: Decimal,
    grid_intensity_gco2_kwh: Decimal,
    urgency: str = "ROUTINE",  # "HOTFIX", "BLOCKING", "ROUTINE"
) -> PolicyDecisionResult:
    """
    Deterministic FinOps & Carbon Policy Gatekeeper:
    1. HOTFIX: Always APPROVED immediately to prevent critical downtime.
    2. BLOCKING: Prioritized; APPROVED unless hard budget ceiling is strictly breached.
    3. ROUTINE:
       - If sprint budget is exceeded (>= 100%): FLAGGED
       - If grid intensity is high (> threshold) and deferral is allowed: DEFERRED
       - If single run exceeds max_carbon_per_run_g: FLAGGED
       - If single run exceeds max_cost_per_run_usd: FLAGGED
       - Otherwise: APPROVED
    """
    policy = get_applicable_policy(db, repository_id, organization_id)
    norm_urgency = urgency.upper().strip()

    # Rule 1: Emergency Hotfix Override
    if norm_urgency == "HOTFIX":
        return PolicyDecisionResult(
            decision="APPROVED",
            reason="Hotfix priority override: Bypassed carbon/budget optimization gates for urgent production remediation.",
        )

    # Check Sprint Budget Status if active sprint is linked
    sprint_summary = None
    if sprint_id:
        sprint_summary = get_sprint_budget_summary(db, sprint_id)

    if sprint_summary:
        # Check hard budget block
        if sprint_summary.over_budget or (sprint_summary.percentage_consumed >= float(policy.budget_block_percent)):
            if norm_urgency == "BLOCKING":
                return PolicyDecisionResult(
                    decision="APPROVED",
                    reason=f"Blocking PR approved under emergency variance despite sprint budget exhaustion (${sprint_summary.consumed_usd:.2f} / ${sprint_summary.budget_usd:.2f}).",
                    rule_violated="BUDGET_OVERRUN_EXCEPTION",
                )
            return PolicyDecisionResult(
                decision="FLAGGED",
                reason=f"Sprint financial budget exhausted (${sprint_summary.consumed_usd:.2f} / ${sprint_summary.budget_usd:.2f}, {sprint_summary.percentage_consumed}% consumed). Requires Engineering Lead sign-off.",
                rule_violated="SPRINT_FINANCIAL_BUDGET_EXCEEDED",
            )

        # Check sprint carbon budget exhaustion
        if sprint_summary.carbon_over_budget:
            if norm_urgency == "ROUTINE" and policy.allow_deferred_execution:
                return PolicyDecisionResult(
                    decision="DEFERRED",
                    reason=f"Sprint carbon budget reached ({sprint_summary.consumed_carbon_kg:.2f} kg / {sprint_summary.carbon_budget_kg:.2f} kg). Routine PR deferred to off-peak lower carbon window.",
                    rule_violated="SPRINT_CARBON_BUDGET_REACHED",
                    can_defer=True,
                    deferral_delay_minutes=120,
                )

    # Rule 2: Grid Carbon Intensity Gate for Routine PRs
    if norm_urgency == "ROUTINE" and policy.allow_deferred_execution:
        if grid_intensity_gco2_kwh >= policy.high_grid_intensity_threshold:
            return PolicyDecisionResult(
                decision="DEFERRED",
                reason=f"Current regional grid carbon intensity ({grid_intensity_gco2_kwh:.1f} gCO2e/kWh) exceeds green threshold ({policy.high_grid_intensity_threshold:.1f} gCO2e/kWh). Queued for lower-carbon execution window.",
                rule_violated="HIGH_GRID_CARBON_INTENSITY",
                can_defer=True,
                deferral_delay_minutes=60,
            )

    # Rule 3: Single Run Carbon Cap
    if estimated_carbon_g > policy.max_carbon_per_run_g:
        return PolicyDecisionResult(
            decision="FLAGGED",
            reason=f"Estimated carbon footprint ({estimated_carbon_g:.1f} gCO2e) exceeds single-run limit of {policy.max_carbon_per_run_g:.1f} gCO2e.",
            rule_violated="MAX_SINGLE_RUN_CARBON_EXCEEDED",
        )

    # Rule 4: Single Run Cost Cap
    if estimated_cost_usd > policy.max_cost_per_run_usd:
        return PolicyDecisionResult(
            decision="FLAGGED",
            reason=f"Estimated CI compute cost (${estimated_cost_usd:.4f}) exceeds single-run limit of ${policy.max_cost_per_run_usd:.2f}.",
            rule_violated="MAX_SINGLE_RUN_COST_EXCEEDED",
        )

    # Default: APPROVED
    return PolicyDecisionResult(
        decision="APPROVED",
        reason="Within configured sprint financial budget and carbon intensity thresholds.",
    )
