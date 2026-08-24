# VERTEX Institutional Demo Readiness

## Purpose

This demo data makes the existing VERTEX Decision Quality Pilot easy to show to an investor, institutional buyer, or program director. It is not a CRM layer, LMS, accelerator database, or prediction system.

The seeded path supports:

Dashboard -> Cohort -> Intervention queue -> Case comments -> Rubric scores -> Decision Memo -> Outcome Report

## Seed demo data

From the repo root:

```powershell
python scripts\seed_demo_cohort.py
```

The script creates a demo cohort in the active SQLite database configured by `VERTEX4D_DATABASE_PATH`. If that variable is not set, the app uses `vertex4d.db` in the repo root.

Artifacts are written under `VERTEX4D_RUNTIME_DIR`. If that variable is not set, artifacts are written under `.vertex_runtime\runs`.

## Reset demo data

```powershell
python scripts\seed_demo_cohort.py --reset-demo
```

Reset deletes only rows that match all demo markers:

- Cohort name: `Demo Cohort - Decision Quality Pilot`
- Institution name: `Northstar Entrepreneurship Center`
- Team names starting with `Demo:`
- Member emails ending in `@northstar-demo.example`
- Run IDs starting with `run_demo_`

If a target does not match the demo markers, reset aborts instead of deleting it.

## Start the app

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then sign in with the seeded facilitator account.

## Demo logins

Facilitator:

- Email: `facilitator@northstar-demo.example`
- Password: `vertex-demo-2026`

Founder/team accounts:

- `maya.ellis@northstar-demo.example` / `vertex-demo-2026` - Demo: CivicCart
- `jonah.park@northstar-demo.example` / `vertex-demo-2026` - Demo: SkillBridge Studio
- `ari.santos@northstar-demo.example` / `vertex-demo-2026` - Demo: ClinicFlow
- `nadia.chen@northstar-demo.example` / `vertex-demo-2026` - Demo: RepairLoop
- `leah.morgan@northstar-demo.example` / `vertex-demo-2026` - Demo: GreenLease

## Main URLs

The script prints the real `cohort_id` after seeding. Use that value in these URLs:

- Facilitator dashboard: `/dashboard/facilitator`
- Cohort case room: `/dashboard/facilitator/cohorts/{cohort_id}`
- Outcome report: `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report`
- Complete Decision Memo: `/dashboard/lab/decision-memo?run_id=run_demo_complete`
- Economics-changed Decision Memo: `/dashboard/lab/decision-memo?run_id=run_demo_economics_changed`

## Seeded case summary

| Run ID | Team | Demo purpose |
|---|---|---|
| `run_demo_complete` | Demo: CivicCart | Complete chain, locked baseline, DecisionRecord, resolved comment, before/post scores |
| `run_demo_intervention` | Demo: SkillBridge Studio | Locked baseline, partial artifacts, open facilitator comment, missing post score |
| `run_demo_baseline_risk` | Demo: ClinicFlow | Legacy-style case with no locked baseline, intentionally marked as intervention needed |
| `run_demo_economics_changed` | Demo: RepairLoop | Baseline price differs from financial scenario price and rubric score improves |
| `run_demo_decision_changed` | Demo: GreenLease | Baseline build decision changes to continue discovery in the DecisionRecord |

## What data is fake

All teams, people, institutions, case details, rubric scores, comments, financial values, and feedback are synthetic demo data. Emails use an example domain and should not be treated as real people.

## What not to claim

Do not claim that VERTEX predicts startup success, validates a startup, guarantees product-market fit, replaces expert facilitation, or produces real market evidence from synthetic demo data.

The defensible claim is:

VERTEX helps founder cohorts make decision quality visible by showing what changed between initial intuition and final decision, with traceability across assumptions, evidence, stakeholders, economics, facilitator interventions, and cohort outcomes.
