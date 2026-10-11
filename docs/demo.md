# GreenOps SPM Academic Capstone Presentation & Demo Script

This document provides the step-by-step presentation script to demonstrate GreenOps to academic evaluators and engineering stakeholders.

---

## 🎭 Live Demonstration Flow

### Scene 1: Platform Overview & Problem Motivation (2 mins)
1. **Open Dashboard**: Navigate to `http://localhost:3000/dashboard`.
2. **Explain the Core Problem**:
   - Every commit in modern teams triggers non-critical CI jobs regardless of electricity grid carbon intensity or sprint budget constraints.
   - Traditional FinOps tools only analyze cloud costs *after the monthly bill arrives*.
   - GreenOps acts as an **upstream proactive gatekeeper** directly in the developer PR flow.
3. **Trigger One-Click Seed Data**: Click **"Seed SPM Demo Data"** to populate realistic multi-repository, multi-sprint telemetry.

---

### Scene 2: The 5 Demonstration Scenarios (5 mins)

#### Scenario A: Routine Pull Request (Under Budget & Green Grid) -> `APPROVED`
- Developer opens routine PR.
- GreenOps estimates runtime, compute cost (\$0.11), and energy footprint.
- Policy check passes -> **`APPROVED`** decision.
- Markdown scorecard posted directly into PR comments.

#### Scenario B: Routine Pull Request during Peak Grid Carbon Intensity -> `DEFERRED`
- Developer opens routine PR while regional grid intensity is high (440 gCO₂e/kWh > 380 g threshold).
- GreenOps Policy Engine detects non-critical PR -> **`DEFERRED`** decision.
- Job is scheduled into Redis/Celery queue for a lower-carbon execution window.
- Scorecard notifies the developer with clear explanation and scheduled time.

#### Scenario C: Production Hotfix during High Grid Carbon Intensity -> `APPROVED`
- Developer creates PR with `[HOTFIX]` tag.
- Even though grid intensity is high, **urgency overrides optimization**.
- GreenOps grants immediate **`APPROVED`** bypass to safeguard system reliability.

#### Scenario D: Sprint Financial Budget Exhaustion -> `FLAGGED`
- Sprint cloud allocation reaches 100%.
- Incoming large ML PR arrives.
- Policy Engine flags PR as **`FLAGGED`** requiring Lead Engineer sign-off before cloud funds are spent.

#### Scenario E: CI Completion & Actual Telemetry Variance
- GitHub Actions workflow completes.
- `workflow_run` webhook updates PostgreSQL with actual duration, cost, and Scope-2 emissions.
- System displays exact estimate vs. actual variance (e.g. +15s duration variance).

---

### Scene 3: SPM Burn-Down & Governance Analytics (3 mins)
1. **Sprint Burn-Down**: Review the ideal linear budget burn line vs actual compute spend in `http://localhost:3000/sprints`.
2. **Repository Ranking**: Compare cost and emissions across `backend-api`, `frontend-web`, and `ml-service` in `http://localhost:3000/repositories`.
3. **Quantified Savings**: Review carbon avoided (kg CO₂e) and compute cost savings achieved from deferred execution.
