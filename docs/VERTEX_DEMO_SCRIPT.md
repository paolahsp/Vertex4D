# VERTEX Institutional Buyer Demo Script

## 8-12 minute flow

Audience: incubator director, university entrepreneurship center director, accelerator program manager, or economic-development program lead.

### 1. Opening buyer context

Say:

"Most founder programs can see attendance, mentor notes, and pitch outcomes. What is harder to see is whether founders made better decisions by the end of the cohort. VERTEX is built around that question: what changed between initial intuition and final decision, and what evidence supports the change?"

Click:

- Sign in as `facilitator@northstar-demo.example`.
- Open `/dashboard/facilitator`.

Buyer should notice:

- This starts at the facilitator dashboard, not a founder worksheet.
- The language is about Decision Cases, baselines, comments, and DecisionRecords.

Avoid:

- "VERTEX predicts which startups will win."
- "The AI validates the business."

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

"This queue is where VERTEX becomes useful during the cohort, not only at the end. It shows which teams need intervention and why."

Click:

- Point to SkillBridge Studio.
- Point to ClinicFlow.

Buyer should notice:

- SkillBridge needs post-score and comment resolution.
- ClinicFlow has a baseline risk because it was imported without a locked baseline.

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

Buyer should notice:

- VERTEX connects baseline intuition to final decision.
- RepairLoop changed economic understanding before committing resources.

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

"The next step I would propose is a paid 4-6 week pilot with one cohort, using VERTEX to capture baselines, facilitator interventions, DecisionRecords, and a final outcome report for the program debrief."

## Phrases to use

- "decision quality"
- "traceability"
- "before/after evidence"
- "intervention need"
- "cohort outcome"
- "missing data is marked as missing"

## Phrases to avoid

- "AI predicts success"
- "validated startup"
- "guaranteed product-market fit"
- "automated accelerator"
- "founder CRM"
- "the score says this company is good"
