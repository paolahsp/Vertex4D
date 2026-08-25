# VERTEX Pedagogical Direction System + Decision Artifacts

## Purpose

This document defines how VERTEX should evolve from a set of powerful modules into a guided pedagogical decision system.

The goal is not to add a generic course layer, LMS, CRM, chatbot, or content portal.

The goal is to make VERTEX feel like a decision coach that always tells the founder and facilitator:

1. What to do now.
2. Why this step matters.
3. What decision skill is being developed.
4. What artifact must be produced.
5. What to do if the team is stuck.
6. How the facilitator should intervene.
7. What the buyer can keep as evidence.

Core product principle:

> The user should never feel they are filling VERTEX. They should feel VERTEX is revealing their business.

## Product Thesis

VERTEX should not behave like a repository of tools. It should behave like a structured decision-learning environment.

The current Golden Path already creates the operational spine:

```text
Decision Case
-> Locked Baseline
-> Alex / ProblemFrame
-> SynapMap / SystemMap
-> Approval Gate
-> D-Predict / PredictiveHypothesis + QBI lite
-> Billie / FinancialScenario
-> DecisionRecord
-> Decision Memo
-> Cohort Outcome Report
```

The missing layer is pedagogical direction.

That layer should sit above the modules and explain what the next useful action is, why it matters, and what evidence will be produced.

For the page-by-page audit method that governs this layer, see `docs/VERTEX_PRODUCT_UX_BUSINESS_AUDIT_SYSTEM.md`.

## UX Model

VERTEX should organize every founder and facilitator experience into five visible layers:

```text
Layer 1: What do I do now?
Layer 2: Why does this matter?
Layer 3: What decision skill am I developing?
Layer 4: What artifact should exist after this step?
Layer 5: What should I do if I am stuck?
```

This solves the main failure mode found in dense learning portals: they show what exists, but not what matters next.

## User Types

VERTEX has three practical users in this layer:

1. Founder
2. Facilitator
3. Institutional buyer / program director

Each user sees the same evidence chain, but through a different job.

### Founder Job

The founder needs to make a better decision.

The founder should see:

- next best action;
- current stage;
- why the stage matters;
- expected artifact;
- evidence gaps;
- facilitator comments;
- final Decision Memo.

### Facilitator Job

The facilitator needs to know where to intervene and why.

The facilitator should see:

- decision interventions;
- workflow attention;
- decision skill affected;
- recommended facilitator move;
- unresolved comments;
- rubric baseline/post movement;
- case-level Decision Memo.

### Buyer Job

The institutional buyer needs to understand what changed across the cohort.

The buyer should see:

- completion;
- locked baselines;
- DecisionRecords;
- decision changes;
- stakeholder deltas;
- pricing deltas;
- intervention needs;
- cohort-level decision skill movement;
- Outcome Report.

## Founder Journey

### Step 0: Enter VERTEX

Current state:

The founder can start a Decision Case and move into Golden Path.

Desired improvement:

Show a clear founder command panel:

```text
Next Best Action
Create a Decision Case and lock your starting snapshot.

Why now
VERTEX needs to preserve what you believe before the method changes your thinking.

Decision skill
Baseline clarity.

Expected artifact
ProjectRecord + Locked Baseline.

If stuck
Do not polish. Write what you currently believe.
```

System behavior:

- If no active `run_id`, recommend creating a Decision Case.
- If a run exists but baseline is not locked, recommend completing baseline.
- If baseline is locked, recommend the next incomplete Golden Path stage.

Data needed:

- active run;
- baseline status;
- artifact completion state;
- facilitator comments;
- current stage.

### Step 1: Baseline Snapshot

Founder task:

Capture the team's starting belief.

Fields:

- initial problem statement;
- customer;
- user;
- payer;
- approver;
- blocker;
- stakeholders;
- assumptions;
- evidence;
- intuition price;
- current decision;
- confidence;
- biggest uncertainty;
- next test.

Pedagogical purpose:

The founder learns that a decision must have a starting point before it can improve.

Decision skill:

Baseline clarity.

Artifact:

`ProjectRecord` plus locked baseline.

System rule:

The baseline must be timestamped and preserved. Later artifacts should not overwrite it.

UX improvement:

Add a panel:

```text
This is not a grade.
This snapshot lets VERTEX show what changed by the end.
```

### Step 2: Alex

Founder task:

Stress-test the problem.

Pedagogical purpose:

Alex prevents premature solutioning.

Decision skill:

Problem framing.

Artifact:

`ProblemFrame`

Expected learning:

The founder should leave this stage with:

- clearer problem statement;
- assumptions surfaced;
- unknowns preserved;
- tensions visible;
- evidence separated from belief.

System direction panel:

```text
Next Best Action
Save a ProblemFrame.

Why now
D-Predict and Billie should not reason from a vague problem.

Decision skill
Framing.

Expected artifact
ProblemFrame.

If stuck
Answer: what decision are you trying to make next?
```

Facilitator intervention triggers:

- problem is a solution in disguise;
- user/customer/payer are conflated;
- assumptions are missing;
- unknowns are too vague;
- no evidence is referenced.

### Step 3: SynapMap

Founder task:

Map stakeholders, relationships, dependencies, bottlenecks and RACI signals.

Pedagogical purpose:

The founder learns that a venture decision changes a system, not only a customer.

Decision skill:

System awareness.

Artifact:

`SystemMap`

Expected learning:

The founder should leave this stage with:

- stakeholder map;
- payer/approver/blocker visibility;
- dependencies;
- tensions;
- evidence references;
- system unknowns.

System direction panel:

```text
Next Best Action
Save a SystemMap.

Why now
D-Predict can only read behavior after the system is visible.

Decision skill
System awareness.

Expected artifact
SystemMap.

If stuck
Start with user, payer, approver and blocker.
```

Facilitator intervention triggers:

- payer is missing;
- approver is missing;
- blocker path is unclear;
- stakeholder map only lists customers;
- dependencies are not named;
- evidence is weak or absent.

### Step 4: Approval Gate

Founder task:

Choose which assumptions are allowed to feed D-Predict and Billie.

Pedagogical purpose:

The founder learns that not every belief should carry decision weight.

Decision skill:

Evidence discipline.

Artifact:

Updated `ProblemFrame` and `SystemMap` assumption approvals.

System direction panel:

```text
Next Best Action
Approve only the assumptions you are willing to let downstream modules use.

Why now
D-Predict and Billie must not treat unreviewed assumptions as facts.

Decision skill
Evidence discipline.

Expected artifact
Approved assumptions.

If stuck
Ask: would I be comfortable making a decision if this assumption turns out false?
```

System rules:

- D-Predict consumes only assumptions marked `approved_for_predictive_processing`.
- Billie consumes only assumptions marked `approved_for_financial_processing`.
- Downstream artifacts must not invent, alter or escalate assumptions.

Facilitator intervention triggers:

- no assumptions approved;
- all assumptions approved without evidence;
- financial assumptions are mixed with behavioral assumptions;
- founder treats approval as validation.

### Step 5: D-Predict

Founder task:

Explore adoption, resistance, undecided behavior and QBI lite uncertainty.

Pedagogical purpose:

The founder learns that different stakeholders can interpret the same idea differently.

Decision skill:

Behavioral logic.

Artifact:

`PredictiveHypothesis`

Current QBI lite artifact:

`qbi_reading`

QBI lite captures:

- coexisting interpretation states;
- actor correlations;
- context-loss vectors;
- commitment pressure.

System direction panel:

```text
Next Best Action
Create a PredictiveHypothesis.

Why now
Your stakeholder map now needs a behavior reading: who may adopt, resist or stay undecided?

Decision skill
Behavioral logic + QBI lite.

Expected artifact
PredictiveHypothesis.

If stuck
Return to Approval Gate and approve at least one predictive assumption.
```

Important boundary:

D-Predict must not claim to predict startup success.

It should say:

```text
This is a bounded hypothesis, not evidence or a factual prediction.
```

Facilitator intervention triggers:

- founder treats hypothesis as proof;
- resistance is ignored;
- undecided stakeholders are not discussed;
- context-loss risk is high;
- commitment pressure is high before enough evidence exists.

### Step 6: Billie

Founder task:

Read pricing, margin, break-even and survival signals.

Pedagogical purpose:

The founder learns that numbers are not punishment; they are survival signals.

Decision skill:

Economic coherence.

Artifact:

`FinancialScenario`

System direction panel:

```text
Next Best Action
Create a FinancialScenario.

Why now
Before committing resources, check whether the idea can survive its own economics.

Decision skill
Economic coherence.

Expected artifact
FinancialScenario.

If stuck
Use conservative ranges. Billie needs explicit assumptions, not perfect forecasts.
```

Facilitator intervention triggers:

- price is unsupported;
- variable cost is missing;
- contribution margin is impossible;
- model depends on unrealistic volume;
- founder ignores cash requirement.

### Step 7: DecisionRecord

Founder task:

Make a reviewed next commitment.

Pedagogical purpose:

The founder learns to collapse uncertainty into a bounded decision without pretending all uncertainty disappeared.

Decision skill:

Decision action.

Artifact:

`DecisionRecord`

System direction panel:

```text
Next Best Action
Save a DecisionRecord.

Why now
The method has surfaced problem, system, behavior, economics and unknowns. Now the team must choose the next bounded action.

Decision skill
Decision action.

Expected artifact
DecisionRecord.

If stuck
Choose a limited experiment instead of a full launch.
```

Facilitator intervention triggers:

- selected decision does not follow evidence;
- risks are missing;
- next experiment is vague;
- DecisionRecord converts hypotheses into facts;
- facilitator approval is missing.

### Step 8: Decision Memo

Founder task:

Review the final decision artifact.

Pedagogical purpose:

The founder sees what changed between baseline and final decision.

Artifact:

Decision Memo print/export.

Memo should include:

- baseline belief;
- final decision;
- problem statement;
- stakeholder system;
- adoption/resistance hypothesis;
- QBI lite summary;
- financial insight;
- evidence trail;
- remaining risks and unknowns;
- next experiment;
- artifact IDs.

System direction panel:

```text
This is what you can keep.
It is not a pitch deck, worksheet or chatbot transcript.
It is a traceable decision artifact.
```

## Facilitator Journey

### Facilitator Dashboard

Current job:

Show program-level health.

Needed improvement:

Add a decision-coaching layer:

```text
Today focus on:
1. Cases with unresolved decision interventions.
2. Cases near DecisionRecord without post score.
3. Cases with missing baseline.
```

Recommended dashboard metrics:

- total cases;
- locked baselines;
- DecisionRecords;
- decision interventions;
- workflow attention;
- rubric baseline/post delta;
- open comments;
- cases missing post score.

### Cohort Page

The cohort page should not only show case status. It should guide facilitation time.

Each case should answer:

```text
What is wrong?
Why does it matter?
Which decision skill is affected?
What should the facilitator do next?
```

### Intervention Radar

Split interventions into two types.

#### Decision Intervention

These are core VERTEX value.

Examples:

- payer/approver unresolved;
- consent path unclear;
- critical assumption unsupported;
- D-Predict resistance ignored;
- Billie price breaks the economics;
- DecisionRecord does not follow evidence;
- high QBI context-loss risk.

Card pattern:

```text
Decision Intervention
SkillBridge Studio

Why it matters
School consent path is unresolved. The founder may be treating the user as the buyer.

Decision skill affected
System awareness / behavioral logic.

Recommended facilitator move
Ask the team to identify payer, approver and blocker before DecisionRecord.
```

#### Workflow Attention

These are operational, not differentiating.

Examples:

- baseline missing;
- post score missing;
- DecisionRecord not submitted;
- feedback not captured;
- print artifact not reviewed.

Card pattern:

```text
Workflow Attention
Post score missing.

Why it matters
Outcome Report will mark post-assessment as missing.

Recommended facilitator move
Capture post rubric after DecisionRecord review.
```

## Rubric Connection

The rubric should become the visible skill model.

Current dimensions:

- framing;
- system awareness;
- evidence quality;
- behavioral logic;
- economic coherence;
- decision action.

Each dimension should map to a Golden Path stage:

| Rubric Dimension | Stage | Artifact |
| --- | --- | --- |
| Framing | Alex | ProblemFrame |
| System awareness | SynapMap | SystemMap |
| Evidence quality | Approval Gate | Approved assumptions |
| Behavioral logic | D-Predict | PredictiveHypothesis |
| Economic coherence | Billie | FinancialScenario |
| Decision action | DecisionRecord | DecisionRecord |

The rubric UI should show:

```text
Score
What raised it
What blocked it
Recommended next move
Evidence/artifact linked
```

## Buyer Journey

The buyer does not need every artifact detail.

The buyer needs proof that the program changed founder reasoning.

Outcome Report should answer:

```text
What changed across the cohort?
Where did facilitators intervene?
Which decision skills improved?
Which cases stayed incomplete?
What evidence can leadership/funders keep?
```

Recommended additions to Outcome Report:

- decision skill movement summary;
- top decision interventions;
- common blocker patterns;
- number of cases with QBI context-loss risk;
- before/after decision examples;
- artifact completion table;
- methodology and disclaimer.

Buyer language:

```text
VERTEX does not predict startup success.
It shows how founder reasoning changed from initial belief to reviewed decision.
```

## System Requirements

### Direction Engine

Create a small server-side or client-side helper that computes `next_best_action`.

Inputs:

- run exists;
- baseline locked;
- artifact summaries;
- approved assumptions count;
- open comments;
- rubric status;
- current route;
- user role.

Output:

```json
{
  "next_action": "Create PredictiveHypothesis",
  "why_now": "D-Predict can only run after SystemMap and approved predictive assumptions exist.",
  "decision_skill": "Behavioral logic",
  "expected_artifact": "PredictiveHypothesis",
  "if_stuck": "Return to Approval Gate and approve at least one predictive assumption.",
  "severity": "required"
}
```

### Artifact Readiness Rules

Rules:

- No D-Predict before `ProblemFrame`, `SystemMap` and predictive approvals.
- No Billie before `ProblemFrame`, `SystemMap` and financial approvals.
- No DecisionRecord before `PredictiveHypothesis` and `FinancialScenario`.
- No final report should infer missing data.
- Missing data must be labelled honestly.

### Intervention Classification

Interventions should be classified as:

```text
decision_intervention
workflow_attention
```

Decision interventions should be shown first.

Workflow attention should be visible but not treated as the core product value.

## Screen-by-Screen Implementation

### 1. Founder / Start Golden Path

Add:

- Next Best Action panel;
- baseline explanation;
- expected artifact;
- if stuck guidance.

### 2. Golden Path Axis

Add to each station:

- artifact status;
- decision skill;
- blocked/unblocked state.

Example:

```text
D-Predict
Behavioral logic
Blocked: no approved predictive assumptions
```

### 3. Alex

Add compact panel:

```text
Why this matters
Alex protects the team from solving the wrong problem.

Artifact expected
ProblemFrame.
```

### 4. SynapMap

Add compact panel:

```text
Why this matters
The decision changes a stakeholder system.

Artifact expected
SystemMap.
```

### 5. Approval Gate

Add:

- warning against approving everything;
- separation of predictive vs financial assumptions;
- count of approved assumptions;
- next module readiness.

### 6. D-Predict

Already added:

- QBI lite reading;
- qbi_reading artifact field;
- QBI summary in Decision Memo.

Add next:

- blocked state before approvals;
- facilitator note when context-loss risk is high.

### 7. Billie

Add:

- baseline intuition price comparison;
- economic coherence explanation;
- if stuck guidance for conservative estimates.

### 8. DecisionRecord

Add:

- readiness checklist;
- unresolved hypothesis warning;
- facilitator approval explanation.

### 9. Decision Memo

Already includes:

- final decision;
- problem;
- risk;
- next test;
- evidence provenance;
- QBI lite summary;
- artifact IDs.

Add next:

- "What changed from baseline" block.
- "Decision skill developed" block.

### 10. Cohort Management

Already improved:

- Intervention Radar distinguishes decision interventions and workflow attention.

Add next:

- recommended facilitator move per case;
- affected decision skill;
- suggested comment template.

### 11. Outcome Report

Add:

- cohort skill movement;
- top intervention categories;
- missing data warnings;
- examples of before/after reasoning.

## Data Model Extensions

Avoid large schema changes at first.

Use derived data where possible.

Suggested derived fields:

```text
next_best_action
decision_skill_current
artifact_readiness
blocked_reason
recommended_facilitator_move
decision_intervention_type
workflow_attention_type
```

Possible future persisted object:

```json
{
  "run_id": "run_...",
  "stage": "d_predict",
  "decision_skill": "behavioral_logic",
  "next_best_action": "Create PredictiveHypothesis",
  "blocked_reason": null,
  "recommended_facilitator_move": "Review whether resistance has been converted into an experiment.",
  "updated_at": "..."
}
```

## Implementation Plan

### Phase 1: Direction Copy and Rules

Scope:

- Create a shared stage metadata map.
- Add direction panels to Start Golden Path, D-Predict, Billie and DecisionRecord.
- Keep copy short and product-facing.

Files likely affected:

- `main.py`
- `templates/lab/_path_bar.html`
- `templates/lab/start_golden_path.html`
- `templates/lab/d_predict.html`
- `templates/lab/billie.html`
- `templates/lab/decision_record.html`
- `static/css/vertex4d.css`

### Phase 2: Next Best Action Engine

Scope:

- Compute next action from run/artifact/baseline state.
- Return same object to founder and facilitator views.
- Use it in dashboard and stage pages.

Rules:

```text
No run -> create Decision Case
No locked baseline -> lock baseline
No ProblemFrame -> go to Alex
No SystemMap -> go to SynapMap
No predictive approvals -> go to Approval Gate
No PredictiveHypothesis -> go to D-Predict
No financial approvals -> go to Approval Gate
No FinancialScenario -> go to Billie
No DecisionRecord -> go to DecisionRecord
Complete -> review Decision Memo
```

### Phase 3: Facilitator Coaching Layer

Scope:

- Add affected skill to intervention cards.
- Add recommended facilitator move.
- Separate decision interventions from workflow attention more clearly.

Decision intervention categories:

- framing_confusion;
- stakeholder_gap;
- evidence_gap;
- approval_path_gap;
- behavioral_resistance_gap;
- qbi_context_loss_risk;
- economic_viability_gap;
- decision_record_mismatch.

### Phase 4: Rubric as Skill Model

Scope:

- Show rubric dimensions as decision skills.
- Connect each score to artifacts.
- Show what blocked improvement.

Example:

```text
Behavioral logic: 2.8 -> 4.1
Raised by: saved PredictiveHypothesis and QBI lite reading.
Still blocked by: high context-loss risk.
```

### Phase 5: Buyer Artifact Upgrade

Scope:

- Add cohort-level skill movement to Outcome Report.
- Add top decision intervention patterns.
- Add before/after reasoning examples.

Buyer-facing message:

```text
This cohort did not just complete tasks.
VERTEX shows how their decision reasoning changed.
```

## Success Criteria

This layer is successful when:

- a founder always knows what to do next;
- a founder understands why each stage matters;
- each session produces a named artifact;
- facilitator comments become targeted interventions, not generic notes;
- the buyer can see reasoning change at cohort level;
- missing data is visible and not hidden;
- no screen claims VERTEX predicts startup success.

## What Not To Build

Do not build:

- LMS content library;
- broad course player;
- generic AI tutor overlay;
- gamified streak system;
- CRM;
- mentor marketplace;
- certification engine;
- automated grading;
- startup success scoring.

VERTEX should stay focused:

```text
decision quality
traceability
intervention need
founder reasoning change
cohort outcome evidence
```

## Final Target Experience

The ideal user experience should feel like this:

```text
Founder:
I know what decision I am working on.
I know what changed in my thinking.
I know what evidence I have.
I know what I still do not know.
I know what to do next.

Facilitator:
I know which teams need help.
I know why they need help.
I know which decision skill is weak.
I know what intervention to make.

Buyer:
I know what changed across the cohort.
I know where facilitation mattered.
I know what artifacts I can keep.
I know what this pilot proved and did not prove.
```

That is the product shape: a pedagogical direction system powered by decision artifacts.
