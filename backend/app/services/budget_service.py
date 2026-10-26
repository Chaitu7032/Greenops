from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sprint import Sprint
from app.models.budget_ledger import SprintBudgetLedger
from app.models.pipeline_run import PipelineRun
from app.schemas.sprint import SprintBudgetSummary, BurnDownPoint


def get_sprint_budget_summary(db: Session, sprint_id: str) -> Optional[SprintBudgetSummary]:
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        return None

    # Calculate consumed USD and Carbon from ledger
    ledger_totals = (
        db.query(
            func.coalesce(func.sum(SprintBudgetLedger.amount_usd), Decimal("0")),
            func.coalesce(func.sum(SprintBudgetLedger.carbon_g), Decimal("0"))
        )
        .filter(SprintBudgetLedger.sprint_id == sprint_id)
        .first()
    )

    consumed_usd = Decimal(str(ledger_totals[0]))
    consumed_carbon_g = Decimal(str(ledger_totals[1]))
    consumed_carbon_kg = consumed_carbon_g / Decimal("1000")

    # Financial budget math
    budget_usd = sprint.budget_usd
    if consumed_usd > budget_usd:
        remaining_usd = Decimal("0.0000")
        over_budget = True
        overspend_usd = consumed_usd - budget_usd
    else:
        remaining_usd = budget_usd - consumed_usd
        over_budget = False
        overspend_usd = Decimal("0.0000")

    pct_consumed = float((consumed_usd / budget_usd * Decimal("100")) if budget_usd > 0 else 0)

    # Carbon budget math
    carbon_budget_kg = sprint.carbon_budget_kg
    if consumed_carbon_kg > carbon_budget_kg:
        remaining_carbon_kg = Decimal("0.0000")
        carbon_over = True
        carbon_overspend_kg = consumed_carbon_kg - carbon_budget_kg
    else:
        remaining_carbon_kg = carbon_budget_kg - consumed_carbon_kg
        carbon_over = False
        carbon_overspend_kg = Decimal("0.0000")

    carbon_pct = float((consumed_carbon_kg / carbon_budget_kg * Decimal("100")) if carbon_budget_kg > 0 else 0)

    return SprintBudgetSummary(
        sprint_id=sprint.id,
        sprint_name=sprint.name,
        budget_usd=budget_usd,
        consumed_usd=consumed_usd,
        remaining_usd=remaining_usd,
        percentage_consumed=round(pct_consumed, 2),
        over_budget=over_budget,
        overspend_usd=overspend_usd,
        carbon_budget_kg=carbon_budget_kg,
        consumed_carbon_kg=consumed_carbon_kg,
        remaining_carbon_kg=remaining_carbon_kg,
        carbon_percentage_consumed=round(carbon_pct, 2),
        carbon_over_budget=carbon_over,
        carbon_overspend_kg=carbon_overspend_kg,
    )


def record_pipeline_ledger_entry(
    db: Session,
    sprint_id: str,
    pipeline_run_id: str,
    amount_usd: Decimal,
    carbon_g: Decimal,
    entry_type: str = "ACTUAL_DEBIT"
) -> SprintBudgetLedger:
    # Idempotency check: prevent duplicate debit if same pipeline run and entry type already exists
    ledger_entry = (
        db.query(SprintBudgetLedger)
        .filter(
            SprintBudgetLedger.sprint_id == sprint_id,
            SprintBudgetLedger.pipeline_run_id == pipeline_run_id,
            SprintBudgetLedger.entry_type == entry_type,
        )
        .first()
    )
    if ledger_entry:
        ledger_entry.amount_usd = amount_usd
        ledger_entry.carbon_g = carbon_g
    else:
        ledger_entry = SprintBudgetLedger(
            sprint_id=sprint_id,
            pipeline_run_id=pipeline_run_id,
            amount_usd=amount_usd,
            carbon_g=carbon_g,
            entry_type=entry_type,
        )
        db.add(ledger_entry)

    db.commit()
    db.refresh(ledger_entry)
    return ledger_entry


def get_sprint_burn_down(db: Session, sprint_id: str) -> List[BurnDownPoint]:
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        return []

    # Calculate days in sprint
    start_dt = sprint.start_date
    end_dt = sprint.end_date
    total_days = max(1, (end_dt - start_dt).days)
    budget_total = float(sprint.budget_usd)

    # Query all pipeline runs or ledger entries grouped by date
    entries = (
        db.query(
            func.date(SprintBudgetLedger.created_at).label("day"),
            func.sum(SprintBudgetLedger.amount_usd).label("daily_cost")
        )
        .filter(SprintBudgetLedger.sprint_id == sprint_id)
        .group_by("day")
        .order_by("day")
        .all()
    )

    cost_by_day = {str(e.day): float(e.daily_cost) for e in entries if e.day}

    points = []
    cumulative_spent = 0.0
    curr = start_dt
    day_idx = 0

    while curr <= end_dt and day_idx <= total_days:
        day_str = curr.strftime("%Y-%m-%d")
        daily_cost = cost_by_day.get(day_str, 0.0)
        cumulative_spent += daily_cost

        # Linear ideal burn
        ideal_remaining = max(0.0, budget_total * (1.0 - (day_idx / total_days)))
        actual_remaining = max(0.0, budget_total - cumulative_spent)

        points.append(
            BurnDownPoint(
                date=day_str,
                budget_remaining_usd=round(actual_remaining, 2),
                actual_spent_usd=round(cumulative_spent, 2),
                ideal_burn_usd=round(ideal_remaining, 2),
            )
        )
        curr += timedelta(days=1)
        day_idx += 1

    return points
