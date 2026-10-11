# Policy Gatekeeper Rules & Decision Matrix

## Decision Outcomes
1. **`APPROVED`**: Immediate execution permitted. Scorecard posted to PR with positive badge.
2. **`DEFERRED`**: Non-critical routine PR queued in Redis/Celery for scheduled execution during lower-carbon grid hours.
3. **`FLAGGED`**: Violates single-run or sprint budget ceilings; requires engineering lead override.

## Gatekeeper Rule Evaluation Matrix
```
Inputs: Urgency (HOTFIX | BLOCKING | ROUTINE), EstCost, EstCarbon, SprintBudgetRemaining, GridIntensity, PolicyRules

1. IF Urgency == 'HOTFIX':
     -> APPROVED ("Hotfix priority override: Bypassed carbon/budget optimization gates for urgent production remediation.")

2. ELSE IF Urgency == 'BLOCKING' AND SprintBudgetRemaining >= EstCost:
     -> APPROVED

3. ELSE IF SprintBudgetRemaining < EstCost:
     -> FLAGGED ("Sprint financial budget exhausted. Requires Engineering Lead sign-off.")

4. ELSE IF Urgency == 'ROUTINE' AND Policy.AllowDeferral == True:
     IF GridIntensity >= Policy.HighGridIntensityThreshold:
       -> DEFERRED ("Current regional grid carbon intensity exceeds green threshold. Queued for lower-carbon window.")
     ELSE IF EstCarbon > Policy.MaxCarbonPerRun:
       -> FLAGGED ("Estimated carbon footprint exceeds single-run limit.")
     ELSE IF EstCost > Policy.MaxCostPerRun:
       -> FLAGGED ("Estimated CI compute cost exceeds single-run limit.")
     ELSE:
       -> APPROVED ("Within configured sprint financial budget and carbon intensity thresholds.")
```
