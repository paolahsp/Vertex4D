# Facilitator Run Of Show

## Kickoff agenda

1. Set the frame: VERTEX measures decision quality, not startup success.
2. Explain the baseline snapshot.
3. Explain the Golden Path:
   - Decision Case
   - Locked Baseline
   - ProjectRecord
   - ProblemFrame
   - SystemMap
   - PredictiveHypothesis
   - FinancialScenario
   - DecisionRecord
   - Decision Memo
4. Explain facilitator comments.
5. Explain rubric scoring.
6. Confirm what the buyer will receive at the end: Decision Memos and Cohort Outcome Report.

## Weekly cadence

Week 1:

- confirm all teams are created
- confirm baseline snapshots are locked
- identify teams with missing baseline data

Week 2:

- review ProblemFrame and SystemMap progress
- add comments where stakeholder or evidence gaps are visible

Week 3:

- review assumptions, adoption/resistance hypotheses, and financial scenarios
- score baseline if not already scored

Week 4:

- push teams toward DecisionRecord
- resolve comments that have been addressed
- capture post scores for completed cases

Weeks 5-6 if used:

- complete remaining DecisionRecords
- review Decision Memos
- prepare Outcome Report and buyer debrief

## What to monitor in dashboard

Open `/dashboard/facilitator`.

Monitor:

- total Decision Cases
- locked snapshots
- open comments
- DecisionRecord completion
- price changes
- decision changes
- feedback captured
- AI calls

## How to use intervention queue

Open `/dashboard/facilitator/cohorts/{cohort_id}`.

The queue should guide facilitation time. Prioritize:

1. baseline not locked
2. open facilitator comments
3. missing DecisionRecord near the end of pilot
4. missing post score before buyer debrief
5. missing feedback before outcome review

## When to comment

Comment when:

- the baseline is too vague to compare later
- stakeholder roles are missing
- evidence is being treated as stronger than it is
- a financial assumption needs review
- the next experiment does not follow from the decision
- an approval or blocker needs traceability

Do not comment just to create activity.

## How to resolve comments

Resolve comments only when:

- the founder has updated the relevant artifact
- the missing evidence has been added
- the decision has been clarified
- the blocker has been acknowledged in the next experiment

## How to score rubric

Use 1-5 for each field:

- framing
- system awareness
- evidence quality
- behavioral logic
- economic coherence
- decision action

Baseline score should reflect the starting snapshot. Post score should reflect the final or latest DecisionRecord-ready state.

Do not present rubric score as a startup ranking.

## When to open Decision Memos

Open `/dashboard/lab/decision-memo?run_id={run_id}` when a case has a DecisionRecord or when you need to show honestly what is still missing.

Use print/export:

`/dashboard/lab/decision-memo/print?run_id={run_id}`

## How to read Outcome Report

Open `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report`.

Use print/export:

`/dashboard/facilitator/cohorts/{cohort_id}/outcome-report/print`

Read it as:

- what the cohort completed
- what changed
- where intervention was needed
- where data is missing
- what the buyer can keep as evidence of program learning

## Buyer debrief structure

1. Restate that VERTEX does not predict startup success.
2. Show cohort totals and completion.
3. Show intervention needs.
4. Show one complete Decision Memo.
5. Show one case with missing data honestly marked.
6. Show price/decision changes where present.
7. Ask what artifact was most useful.
8. Ask whether to run a paid next cohort.
