# VERTEX Pilot Operator Checklist

Use this checklist to run a real institutional Decision Quality Pilot. The goal is to help a buyer keep useful artifacts: Decision Memos, a Cohort Outcome Report, and a clear debrief.

## Before pilot setup

- Confirm buyer, cohort dates, facilitator owner, and expected team count.
- Decide whether this is a design-partner pilot, standard paid pilot, or high-touch pilot.
- Set the pilot promise: VERTEX shows decision quality and before/after learning. It does not predict startup success.
- Confirm where the SQLite database and runtime artifact store will live.
- Set `VERTEX4D_SESSION_SECRET` before any real cohort.
- Set either `VERTEX4D_FACILITATOR_EMAILS` or `VERTEX4D_FACILITATOR_INVITE_CODE`.
- Confirm API keys only if live AI-assisted modules will be used: `OPENAI_API_KEY` and/or `ALEX_OPENAI_API_KEY`.
- Run regression checks:

```powershell
python -m compileall main.py database.py artifacts.py contracts_runtime.py scripts
python scripts\validate_contracts.py
python scripts\smoke_vertex_golden_path.py
```

## Cohort setup

- Start the app:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

- Create or register the facilitator/admin account.
- Open `/dashboard/facilitator`.
- Create the cohort with institution name, start date, end date, and status.
- Add teams as cohort members when accounts exist.
- Use `/dashboard/facilitator/cohorts/{cohort_id}` as the cohort case room.

## Demo/data privacy check

- For demo rehearsal, seed only synthetic demo data:

```powershell
python scripts\seed_demo_cohort.py
```

- Reset demo data before real pilot work:

```powershell
python scripts\seed_demo_cohort.py --reset-demo
```

- Confirm founder names, emails, venture descriptions, comments, and artifacts are real pilot data only after consent has been captured.

## Founder onboarding

- Use `docs/FOUNDER_ONBOARDING_SCRIPT.md`.
- Tell founders that the baseline is a snapshot, not a test.
- Ask founders to bring their current problem, customer, stakeholders, assumptions, evidence, price intuition, biggest uncertainty, and next test.
- Direct founders to start a Decision Case and complete the Golden Path.

## Baseline capture

- Baseline must be captured before the founder edits through VERTEX.
- Required baseline fields for a useful pilot:
  - problem statement
  - customer/user/payer/approver/blocker
  - stakeholders
  - assumptions
  - evidence
  - intuition price
  - current decision
  - confidence score
  - biggest uncertainty
  - next test
- If a baseline is missing, mark it honestly as missing. Do not reconstruct it later from memory.

## Facilitator review cadence

- Review `/dashboard/facilitator` at least weekly.
- Open `/dashboard/facilitator/cohorts/{cohort_id}` for intervention work.
- Check:
  - baseline not locked
  - DecisionRecord missing
  - open facilitator comments
  - baseline score missing
  - post score missing
- Add comments only when a facilitator judgment or blocker needs traceability.
- Resolve comments only after the founder has addressed the issue.

## Rubric scoring cadence

- Score baseline after the initial snapshot.
- Score post after the DecisionRecord or final review point.
- Use the same reviewer standard for baseline and post.
- Scores are decision-quality scores, not startup scores.

## Decision Memo review

- Open `/dashboard/lab/decision-memo?run_id={run_id}`.
- Print/export via `/dashboard/lab/decision-memo/print?run_id={run_id}`.
- Review:
  - baseline status
  - initial decision
  - final decision
  - problem statement
  - stakeholder system
  - adoption/resistance hypothesis
  - financial insight
  - evidence
  - risks/unknowns
  - next experiment
  - artifact IDs
- If the memo has missing data, keep the missing label. Do not fill the memo manually outside VERTEX.

## Cohort Outcome Report review

- Open `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report`.
- Print/export via `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report/print`.
- Review:
  - completion rate
  - locked baselines
  - DecisionRecords
  - stakeholder deltas
  - price changes
  - decision changes
  - founder feedback
  - AI usage
  - cases needing intervention
  - average rubric baseline/post/delta

## Buyer debrief

- Start with what the cohort changed, not what VERTEX features exist.
- Show 2-3 Decision Memos.
- Show the Outcome Report.
- Name missing data and intervention needs plainly.
- Ask whether the buyer would run another cohort and what artifact mattered most.

## Reset/archive notes

- Demo reset only removes demo-marked data.
- Real pilot deletion/export is manual today. Back up the SQLite DB and `.vertex_runtime\runs` before any archive/deletion work.
- Do not run demo reset against real cohort data expecting it to archive anything.

## If data is missing

- Say: "VERTEX marks this as missing instead of fabricating an outcome."
- For a missing baseline, do not infer the baseline from later artifacts.
- For a missing DecisionRecord, keep the case in intervention.
- For missing rubric scores, schedule reviewer scoring before buyer debrief.
- For missing feedback, note that founder feedback was not captured.
