# VERTEX Institutional Buyer Demo Script

## Current recommended version

For the next commercial rehearsal, use `docs/VERTEX_COMMERCIAL_REHEARSAL.md` first.

This script remains a feature-complete institutional demo path. The commercial rehearsal is tighter: it tells one transformation story, then switches into the facilitator and buyer view through Intervention Radar and Cohort Outcome Report.

## 9-10 minute buyer demo flow

Rule:

Do not show how VERTEX works until the buyer has seen a decision change.

Target timing:

| Time | Moment |
| --- | --- |
| 0:00 | Buyer problem |
| 0:30 | Baseline belief |
| 1:15 | Decision changed |
| 2:30 | Decision Memo |
| 4:00 | Switch to Program Director |
| 4:30 | Intervention Radar |
| 6:15 | Cohort Outcome Report |
| 8:15 | What the pilot measures |
| 9:15 | Name the cohort + next step |

### Opening

Ask first:

"Before I show you anything: when a cohort ends, what can you demonstrate today about how founder decision-making changed beyond attendance, workshops and pitch decks?"

Pause.

Then say:

"That is what VERTEX is designed to make visible. I will show one founder decision changing, then switch into the Program Director view."

Avoid opening with:

- a feature tour;
- login;
- module explanations;
- schema IDs;
- claims that VERTEX improves outcomes.

### First aha: before -> after

Say:

"RepairLoop entered with this baseline belief: a price intuition, a stakeholder assumption and a current decision. VERTEX preserved that starting point. After the system and economics were reviewed, the team was no longer making the same decision."

Click:

- Open `/dashboard/lab/decision-memo?run_id=run_demo_economics_changed`.
- Point to `What changed?`.
- Point to baseline -> reviewed decision.
- Point to why it changed.

Buyer should notice:

- VERTEX does not claim the startup will succeed.
- VERTEX shows why the next commitment changed.
- The artifact is a decision record, not a chatbot answer.

Say:

"VERTEX did not validate the startup. It made explicit why the next commitment should change."

### Switch to Program Director

Say:

"That is useful for one founder. But the institutional job is different: if I am responsible for twenty teams, I cannot read twenty memos every Tuesday."

Click:

- Open `/dashboard/facilitator/cohorts/{cohort_id}`.

### Intervention Radar

Say:

"This is not a progress alert. The first card is a decision intervention. SkillBridge still has an unresolved school consent path. The team may be treating the user as if they are also payer and approver."

Point to:

- decision intervention first;
- workflow attention second.

Say:

"We separate decision intervention from workflow attention because missing post scores are administration. Payer confusion is VERTEX."

Avoid:

- adding a comment live;
- resolving a comment live;
- spending time on task-management behavior.

### Outcome Report

Say:

"This is what the Program Director can keep: not a dashboard screenshot, but a report of what changed, where intervention was needed, and what data is still missing."

Click:

- Open `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report`.
- Show paired cases, decision changes, interventions and missing paired data.
- Show observed movement in the decision-quality rubric.
- Show one before -> after case.

Say:

"Missing stays missing. VERTEX does not invent a post score to make the report look complete."

### Pilot scope

Say:

"The pilot does not try to prove causality. It tests feasibility, observed change, facilitator usefulness and whether this report is useful enough to run another cohort."

### Closing ask

Ask:

"Thinking about the next 90 days, which cohort would be the cleanest candidate to test this with real founders?"

If they name one:

"Good. The next step is to define that cohort, success criteria and your data/security review. For up to 15 teams, the pilot is EUR 5,500 fixed for 4-6 weeks. If that is within range, we can close scope in a 30-minute pilot planning session."

Do not close with:

"Would this visibility help?"

That produces polite interest, not a qualified opportunity.

## Feature-complete appendix flow

Audience: incubator director, university entrepreneurship center director, accelerator program manager, or economic-development program lead.

### 1. Opening buyer context

Say:

"Your program already tracks activity: workshops, mentor sessions, milestones and pitch outcomes. The harder question is what changed in the founder's reasoning, why it changed, and where your team should intervene before more resources are committed. VERTEX makes that decision trail visible across the cohort."

Click:

- Use an already-authenticated browser.
- Open `/dashboard/facilitator`.

Buyer should notice:

- This starts at the facilitator dashboard, not a founder worksheet.
- The language is about Decision Cases, baselines, comments, and DecisionRecords.

Avoid:

- "VERTEX predicts which startups will win."
- "The AI validates the business."
- "Your current systems cannot show outcomes."

### 2. Facilitator dashboard

Say:

"This is the program view. A facilitator can see how many Decision Cases exist, how many have locked snapshots, how many reached DecisionRecord, and where open comments remain."

Click:

- Point to Decision Cases, locked snapshots, open comments, completion rate.
- Open `Demo Cohort - Decision Quality Pilot`.

Buyer should notice:

- VERTEX shows workflow state and decision-readiness signals.
- It does not hide missing data.

### 3. Open demo cohort

Say:

"A cohort is the institutional container. It lets a program director review multiple founder cases without manually assembling a spreadsheet before every meeting."

Click:

- Open the cohort case room.
- Briefly scan the top totals.

Buyer should notice:

- Teams and cases are grouped around a program.
- The demo is about cohort operations, not CRM records.

### 4. Show intervention queue

Say:

"This queue is where VERTEX becomes useful during the cohort, not only at the end. It shows which teams need human attention and why. The strongest signals are not merely missing tasks; they are business reasoning risks that need facilitator judgment."

Click:

- Point to SkillBridge Studio.
- Point to ClinicFlow.

Buyer should notice:

- SkillBridge needs post-score and comment resolution.
- ClinicFlow has a baseline risk because it was imported without a locked baseline.
- The hero signal is the substantive unresolved decision issue, not workflow hygiene alone.

Fallback if data is missing:

"This is exactly what the product should show: missing data is marked as missing instead of being smoothed into a fake outcome."

### 5. Open a case that needs intervention

Say:

"SkillBridge has done some work, but the facilitator still has an open question: the school consent path is unresolved. That is a program intervention, not just a product status."

Click:

- Use `Open case` for `run_demo_intervention`.
- Show the open comment.

Buyer should notice:

- The comment is attached to the case and can point to an artifact.
- The founder is not simply filling a form; VERTEX is revealing the blocker in the business system.

### 6. Add or resolve comment

Use only in an appendix or second demo. Do not include this in the first commercial pass.

Say:

"A facilitator can add a note when judgment is needed, then resolve it when the team has addressed the issue. This creates traceability around intervention, not just private mentor memory."

Click:

- Resolve the existing SkillBridge comment, or add a short general comment if you want to preserve the seeded open comment.

Buyer should notice:

- The intervention queue changes because the case state changes.

### 7. Show rubric scores

Say:

"The score is not a startup score. It is a decision-quality rubric: framing, system awareness, evidence quality, behavioral logic, economic coherence, and decision action."

Click:

- Show SkillBridge baseline score with missing post score.
- Show RepairLoop baseline and post scores.

Buyer should notice:

- Before/post scoring creates a defensible improvement signal.
- Missing post score remains visible as missing.

Avoid:

- "This score ranks the best startup."
- "A high score means they will succeed."

### 8. Open Decision Memo

Say:

"The Decision Memo is the founder-level artifact. It summarizes the final decision, the original baseline decision, stakeholder system, evidence, risks, economics, and next experiment."

Click:

- Open `/dashboard/lab/decision-memo?run_id=run_demo_economics_changed`.
- Point to pricing insight: intuition price to modelled price.
- Point to traceability chips.
- Translate traceability as evidence provenance rather than raw IDs.

Buyer should notice:

- VERTEX connects baseline intuition to final decision.
- RepairLoop changed economic understanding before committing resources.
- The buyer can inspect where conclusions came from without buying technical identifiers.

### 9. Open Outcome Report

Say:

"The Outcome Report is the institutional artifact. It shows completion, baselines, DecisionRecords, stakeholder delta, price changes, decision changes, open intervention need, and missing data."

Click:

- Open `/dashboard/facilitator/cohorts/{cohort_id}/outcome-report`.
- Point to complete case, intervention case, baseline risk case, economics changed case, and decision changed case.

Buyer should notice:

- Cohort-level decision quality can be discussed without inventing outcomes.
- The report is useful for debriefs, sponsor updates, and program learning.

### 10. Closing pitch

Say:

"VERTEX is a decision-readiness system for founder cohorts. It helps the institution see what changed between initial intuition and final decision: where founders found evidence, where they discovered stakeholders or blockers, where economics changed the plan, and where facilitator intervention was needed. It does not predict startup success. It makes decision quality and cohort learning traceable enough to run a paid pilot."

Call to action:

"Thinking about the next 90 days, which cohort would be the cleanest candidate to test this with real founders?"

## Phrases to use

- "decision quality"
- "traceability"
- "before/after evidence"
- "intervention need"
- "cohort outcome"
- "missing data is marked as missing"
- "decision intervention, not workflow attention"
- "a traceable change, not an AI answer"
- "missing stays missing"

## Phrases to avoid

- "AI predicts success"
- "validated startup"
- "guaranteed product-market fit"
- "automated accelerator"
- "founder CRM"
- "the score says this company is good"
- "the method works"
- "nobody else can do this"
- "below the tender threshold"
