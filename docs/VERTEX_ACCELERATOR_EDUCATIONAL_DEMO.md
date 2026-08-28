# VERTEX Accelerator Educational Demo

## Purpose

This document explains how to present VERTEX to accelerators as a working educational decision system.

The demo should not position VERTEX as an LMS, course library, CRM, mentor marketplace or startup prediction engine.

VERTEX does not predict startup success.

Position it as:

```text
A decision-readiness workspace for founder cohorts.
Founders work through one Decision Case.
Facilitators see where to intervene.
Accelerators keep evidence of what changed.
```

## Core Educational Proposal

VERTEX teaches inside the founder's real decision work.

The student does not consume separate lessons.

The student works on a live Decision Case and produces artifacts that reveal:

- what they believed at the beginning;
- what assumptions they were carrying;
- who matters in the stakeholder system;
- what evidence is strong, weak or missing;
- where adoption may resist;
- whether the economics make sense;
- what decision they are willing to commit to next;
- what changed from baseline to reviewed decision.

Founder-facing promise:

```text
Make the next decision with evidence, not just momentum.
```

Facilitator-facing promise:

```text
Know where to intervene and why.
```

Accelerator-facing promise:

```text
Show what changed across the cohort.
```

## Where Students Work

Students work in the VERTEX Golden Path.

Entry point:

```text
/dashboard/lab/start-golden-path
```

Core workspace:

```text
Decision Case
-> Alex
-> SynapMap
-> Approval Gate
-> D-Predict + QBI lite
-> Billie
-> DecisionRecord
-> Decision Memo
```

Each module now shows a direction layer:

```text
Next action
Why it matters
What VERTEX should reveal
Where this goes
Gate / risk note
```

This keeps the student oriented without turning the product into a lesson player.

## Module And Deliverable Map

| Student module | Student job | What VERTEX reveals | Deliverable | Used later by |
|---|---|---|---|---|
| Decision Case / Baseline | Capture the first belief state | What the team believes before evidence pushes back | Locked Baseline + `ProjectRecord` | Alex, Decision Memo, Outcome Report |
| Alex | Stress-test the problem | Whether the team is solving a real problem or describing a solution | `ProblemFrame` | SynapMap, Approval Gate, DecisionRecord |
| SynapMap | Map actors and dependencies | Who uses, pays, approves, blocks or carries risk | `SystemMap` | Approval Gate, D-Predict, Intervention Radar |
| Approval Gate | Choose what may propagate | Which assumptions can carry decision weight | Approved assumption register | D-Predict, Billie, traceability |
| D-Predict + QBI lite | Read adoption, resistance and context risk | Where behavior may resist the plan | `PredictiveHypothesis` + `qbi_reading` | DecisionRecord, Decision Memo |
| Billie | Test price, margin and survival signals | Whether pricing intuition conflicts with economics | `FinancialScenario` | DecisionRecord, Decision Memo, Outcome Report |
| DecisionRecord | Commit to the next bounded decision | What decision follows from the reviewed chain | `DecisionRecord` | Decision Memo, facilitator review, Outcome Report |
| Decision Memo | Review and export the case | What changed from baseline to reviewed decision | Print-ready Decision Memo | Founder, facilitator, buyer |

## Facilitator Workspace

Facilitators do not work primarily inside the student modules.

They work in:

```text
/dashboard/facilitator
/dashboard/facilitator/cohorts/{cohort_id}
```

The facilitator sees:

- cohort cases;
- baseline lock status;
- DecisionRecord status;
- open comments;
- rubric baseline/post status;
- Decision Intervention;
- Workflow Attention;
- case-level Decision Memo links;
- Outcome Report links.

The key commercial distinction:

```text
Decision Intervention = substantive founder reasoning issue.
Workflow Attention = operational missing data or incomplete step.
```

Example:

```text
Workflow Attention:
Post rubric score is missing.

Decision Intervention:
The founder assumes the school pays, but the SystemMap does not identify who controls budget.
```

That distinction is what makes VERTEX more than task management.

## Accelerator / Buyer Workspace

The accelerator should mostly see:

```text
Cohort Outcome Report
Decision Memo examples
Intervention Radar
```

Buyer artifact:

```text
/dashboard/facilitator/cohorts/{cohort_id}/outcome-report
```

The report should answer:

- How many cases completed?
- How many baselines were locked?
- How many DecisionRecords exist?
- Where was intervention needed?
- What decision changes happened?
- What pricing/economic movement happened?
- What rubric movement was observed?
- What data is still missing?
- Which before/after case can be shown?

Use careful language:

```text
observed movement in the decision-quality rubric
change in reviewed reasoning
missing data remains missing
```

Avoid:

```text
VERTEX proves founders learned the skill.
VERTEX validates startups.
AI predicts success.
```

## What Works Technically Today

Current validated core:

- Decision Case creation;
- locked baseline;
- Golden Path artifact chain;
- `ProjectRecord`;
- `ProblemFrame`;
- `SystemMap`;
- approved assumptions;
- `PredictiveHypothesis`;
- QBI lite reading;
- `FinancialScenario`;
- `DecisionRecord`;
- Decision Memo;
- facilitator cohort management;
- Intervention Radar;
- comments;
- baseline/post rubric scores;
- Cohort Outcome Report;
- print routes for Memo and Outcome Report;
- demo seed/reset workflow.

Validation commands:

```powershell
python -m compileall main.py database.py artifacts.py contracts_runtime.py scripts
python scripts\validate_contracts.py
python scripts\smoke_vertex_golden_path.py
python scripts\smoke_demo_cohort.py
python scripts\smoke_pilot_readiness.py
```

## What Is Demo-Ready

Ready for a guided accelerator conversation:

- one synthetic demo cohort;
- five demo cases;
- facilitator login;
- founder demo logins;
- full golden path smoke;
- cohort outcome smoke;
- print routes;
- commercial rehearsal script;
- trust-pack checklist;
- educational direction architecture;
- visible direction strip in student modules.

Use this as a guided demo, not yet as a public self-serve demo.

## What Still Needs Product Work

Before a polished accelerator-facing pilot:

1. Make the direction layer dynamic.
   It currently explains the module job. Next, it should read case state and show contextual contradictions.

2. Improve contradiction detection.
   Examples:
   - payer/approver mismatch;
   - price unsupported by evidence;
   - D-Predict resistance ignored;
   - Billie economics contradict baseline price;
   - DecisionRecord not aligned with evidence.

3. Strengthen facilitator coaching.
   Intervention cards should show:
   - reason;
   - decision-quality dimension;
   - recommended facilitator move;
   - artifact link.

4. Validate rubric reliability.
   Do not claim skill acquisition until inter-rater reliability and buyer usefulness are tested.

5. Create real trust documents.
   The current trust pack is a checklist. Paid pilots need actual DPA, subprocessors, retention, AI data-use and security summaries.

6. Create a stable demo environment.
   A public or semi-private URL should come after the guided demo flow is clean.

## Demo Narrative For Accelerators

Suggested flow:

1. Start with the accelerator problem:

```text
You already know who attended sessions.
The harder question is what changed in founder reasoning and where facilitators should intervene.
```

2. Show facilitator cohort view.

3. Show Intervention Radar.

4. Open one case with a decision issue.

5. Show the student artifact chain.

6. Show Decision Memo.

7. Show Outcome Report.

8. Close with pilot ask:

```text
Run one 4-6 week Decision Quality Pilot with 8-12 teams.
We measure completion, intervention usefulness, observed reasoning change,
buyer usefulness of the report and willingness to run another cohort.
```

## Current Readiness Verdict

```text
Ready for guided accelerator demo: yes.
Ready for paid pilot discovery: yes, with scoped claims.
Ready for public self-serve demo: not yet.
Ready to claim proven educational impact: no.
```
