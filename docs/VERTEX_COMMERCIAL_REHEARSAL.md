# VERTEX Commercial Rehearsal

## Purpose

This is the preferred 10-minute buyer-facing rehearsal after the demo evidence review and research validation.

Do not demo every feature. Demo the transformation:

1. Start at the cohort so the buyer feels the institutional problem immediately.
2. Show where the facilitator needs to intervene.
3. Open one case to explain why the signal exists.
4. Show the locked before state.
5. Show the evidence, system, or economics shift.
6. Show the Decision Memo as the founder artifact.
7. Return to the cohort view.
8. Show the Cohort Outcome Report as the buyer artifact.

The buyer should not feel that VERTEX is a form builder, course platform, CRM, or generic AI assistant. The buyer should feel that VERTEX makes founder reasoning change visible enough to manage.

For the module-by-module student workspace and deliverables map, use `docs/VERTEX_ACCELERATOR_EDUCATIONAL_DEMO.md`.

Buyer promise:

"Know where to intervene. Show what changed."

Founder promise:

"Make the next decision with evidence, not just momentum."

## Commercial thesis

VERTEX has three connected value objects:

| Audience | Object | Buyer-readable value |
|---|---|---|
| Founder | Decision Case | "I understand my business better and know what to do next." |
| Facilitator | Intervention Radar | "I know which team needs help and why." |
| Institutional buyer | Cohort Outcome Report | "I can show what changed during the program." |

The Decision Memo proves individual value.

The Cohort Outcome Report proves institutional value.

Both matter, but the report may be the artifact that closes the institutional sale because it gives a program director something they can take to a sponsor, university leader, funder, or internal stakeholder.

Competitive framing:

"Accelerator software tells you where the startup is in the program. VERTEX is designed to show how the founder's decision changed, and what evidence and intervention sit behind that change."

## Timing

Target length: 10 minutes.

Hard stop: 12 minutes.

Do not explain implementation details, artifact schemas, or every module. Stay with one story.

## Setup

Seed demo data:

```powershell
python -m scripts.seed_demo_cohort --json
```

Start the app:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Sign in:

- Email: `facilitator@northstar-demo.example`
- Password: `vertex-demo-2026`

Recommended cases:

- Transformation story: `run_demo_economics_changed` / Demo: RepairLoop
- Intervention story: `run_demo_intervention` / Demo: SkillBridge Studio
- Baseline risk story: `run_demo_baseline_risk` / Demo: ClinicFlow

Visual rule:

Use the VERTEX 4D visual system in `docs/design/prompt-sistema-visual.md`. Color is semantic, not decorative: evidence is mint, hypothesis is lavender, risk is coral, and current action is purple. The dark theme is primary; the light theme must meet AA contrast with accent colors used as filled chips with dark ink, not pale text. Avoid generic gradients, ambient motion, leaderboard-style gamification, library-icon aesthetics, and low-contrast labels.

## 10-minute flow

### 0:00-0:45 - Open with the buyer problem

Screen: facilitator dashboard / cohort overview.

Say:

"Your program already tracks activity: workshops, mentor sessions, milestones and pitch outcomes. The harder question is what changed in the founder's reasoning, why it changed, and where your team should intervene before more resources are committed. VERTEX makes that decision trail visible across the cohort."

Buyer should understand:

- This is about program visibility, not founder productivity.
- The institution buys visibility into decision change.

Avoid:

- "AI predicts success."
- "VERTEX validates the startup."
- "This replaces facilitators."

### 0:45-1:30 - Show the Intervention Radar first

Screen: intervention queue.

Say:

"Before a facilitator meeting, I can see which cases need human judgment rather than checking every team manually. This is not a ranking of startups. It is a signal that a decision needs attention."

Point to:

- SkillBridge as the substantive intervention story.
- ClinicFlow as a baseline risk story.
- The distinction between decision intervention and workflow attention.

Buyer should notice:

- VERTEX creates facilitator prioritization.
- The strongest alerts are about business reasoning, not merely completion status.

### 1:30-2:15 - Open one flagged case

Screen: SkillBridge case or RepairLoop case.

Say:

"This case is not being flagged because the founder is a bad startup. It is being flagged because an important decision issue still needs evidence. The facilitator can see the gap and decide where to intervene."

If using SkillBridge:

"The school consent and approval path is unresolved. That is decision intelligence, not just a missing task."

If using RepairLoop:

"The pricing intuition changed once the operating assumptions were connected to the economics."

Buyer should notice:

- The alert points to a reason a human facilitator can act on.
- Workflow hygiene is visible, but decision intervention is the hero.

### 2:15-3:15 - Establish the before state

Screen: locked baseline / case details / Decision Memo for RepairLoop.

Say:

"VERTEX locks what the founder believed before the reasoning process begins. That matters because otherwise the starting intuition gets rewritten after the team learns more."

Point to:

- Initial problem interpretation
- Initial decision
- Initial price if relevant
- Locked baseline state

Buyer should notice:

- The baseline is not overwritten by later confidence.
- VERTEX preserves the assumptions that matter to the decision.

### 3:15-4:30 - Explain the Decision Case as an evidence file

Screen: RepairLoop case or Decision Memo.

Say:

"The founder is not just moving through modules. They are building one decision file through several lenses: the problem, the surrounding system, likely behavior, economics, and final decision."

Use this framing:

- What I currently believe
- What I know
- What I am assuming
- Who can make this work or fail
- What the economics imply
- What changed
- What I am deciding now

Buyer should notice:

- Alex, SynapMap, D-Predict, and Billie should feel like lenses on one case, not separate products.
- The product is revealing the business, not collecting worksheet answers.

Evidence Gate note:

"At each step, VERTEX should distinguish what the founder knows, what they infer, and what is still an assumption."

### 4:30-5:30 - Show the contradiction or economic shift

Screen: Decision Memo for RepairLoop.

Say:

"RepairLoop entered with one pricing intuition. Once the team connected operating assumptions to the economics, that price no longer supported the decision they were about to make. VERTEX is not saying the new price is correct or that this startup will succeed. It is showing why the original decision became harder to defend, what changed, and what needs to be tested next."

Point to:

- Pricing / financial insight
- Final decision
- Next experiment
- Evidence trail

Buyer should notice:

- The founder did not simply get a recommendation.
- The founder's decision became more evidence-backed.

### 5:30-6:30 - Show the Decision Memo

Screen: Decision Memo print view.

Say:

"This is what the founder leaves with. Not another canvas: a decision record. It shows what they initially believed, what evidence changed the picture, what uncertainty remains, what they are deciding now, and what experiment comes next."

Point to:

- Baseline locked status
- Initial decision
- Final decision
- Evidence table
- Methodology and disclaimer

Do not point to raw technical IDs unless asked. Translate them:

"The conclusions retain an evidence trail, so the facilitator can inspect where they came from."

Buyer should notice:

- This looks like a serious decision artifact.
- Missing data and uncertainty are not hidden.

### 6:30-7:15 - Return to Intervention Radar

Screen: intervention queue / cohort case room.

Say:

"Now I am the Program Director again. I do not have one founder; I have twenty. The same structure lets me see where human attention is actually needed."

Point to:

- Decision intervention
- Awaiting founder evidence
- Workflow incomplete

Buyer should notice:

- The B2B product is not an add-on. It has its own workflow.
- The institution can manage the cohort through decision readiness signals.

### 7:15-8:45 - Show the Cohort Outcome Report

Screen: Outcome Report print view.

Say:

"This is the institutional artifact. It shows what changed across the cohort: completion, locked baselines, DecisionRecords, stakeholder changes, pricing changes, decision changes, intervention needs, missing data, methodology, and disclaimer."

Point to:

- Completion rate
- Locked baselines
- DecisionRecords
- Stakeholder delta
- Price changes
- Decision changes
- Need intervention
- Missing data labels

Use the missing-data trust signal once:

"Where evidence is missing, VERTEX leaves it missing rather than manufacturing a synthetic outcome."

Buyer should notice:

- This is the artifact they can take to leadership, sponsors, or funders.
- It does not claim startup success.
- It does show program learning.

### 8:45-9:20 - Explain measurement honestly

Say:

"For the pilot, we can compare founder decision reasoning before and after using a pre-defined rubric. That tells us whether we observe structured change. It does not, by itself, prove that VERTEX caused every change, because founders are also learning from mentors, customers, workshops, and the rest of your program."

Then:

"What we want to learn is whether that measurement is credible and useful enough for your team to run the program differently."

Buyer should notice:

- VERTEX respects evidence discipline.
- The pilot is a behavioral and commercial test, not a causal claim.

### 9:20-10:00 - Close with the paid pilot ask

Say:

"The next step is not a software subscription. It is one paid 4-6 week Decision Quality Pilot with 10-20 teams. We capture the baseline, use VERTEX during the cohort to surface intervention needs, close each case with a DecisionRecord where possible, and finish with a cohort report for your debrief."

Then:

"The pilot succeeds commercially only if two things happen: founders' decisions become more explicit and evidence-backed, and your team considers that visibility valuable enough to use VERTEX again."

Ask:

- "Which upcoming cohort would be the most realistic place to test this?"
- "Who else would need to approve a EUR 5,500 pilot?"
- "What would this report have to show for you to fund the next cohort?"
- "What would stop you from running this with that cohort?"

Avoid ending with:

"Would this kind of visibility help you?"

That is too easy to answer politely without exposing budget, authority, timing, or urgency.

## Product interpretation after the rehearsal

Current state:

- VERTEX is no longer only a founder tool.
- The institutional flow is beginning to feel like product.
- The strongest B2B artifact is likely the Cohort Outcome Report.
- The strongest facilitator job-to-be-done is the Intervention Radar.
- The strongest founder artifact remains the Decision Memo.

Roadmap reading:

- Meses 0-2: largely closing.
- Meses 2-4: ready to begin with real Alpha/Beta pilots.
- Meses 4-6: partially pulled forward through print artifacts, buyer docs, proposal, and outcome reports.
- Meses 6-12: should wait until real pilot behavior and buyer willingness to pay are clearer.

Validation status:

- The institutional problem is credible enough to test.
- Decision quality is not yet a proven budget category; it is the wedge VERTEX must validate.
- The decisive evidence is a real Program Director naming a cohort, obtaining approval, paying, using Intervention Radar during delivery, using the final report afterward, and paying again.

## Do not build yet

Do not build these until real pilots justify them:

- Community
- Marketplace
- Complex certifications
- Full LMS
- Large course catalog
- Sophisticated benchmarking
- White-label
- SSO/SAML
- Sophisticated founder subscription
- Mentor matching
- Investor tooling

## Immediate product work

Do these before or around the commercial rehearsal:

1. Fix contrast and legibility in the light web UI.
2. Validate responsive behavior on mobile.
3. Make the Decision Memo web view calmer and more balanced.
4. Make the Evidence Gate explicit in the product journey.
5. Rehearse this commercial flow aloud until it consistently lands in 8-12 minutes.

6. Prepare a one-page Data and AI Governance appendix for buyers who ask.

The governance appendix should cover: data stored, access model, retention/deletion, AI disclosure, whether customer data is used for model training, human-vs-AI scoring, and basic security posture. Do not turn the main demo into a compliance walkthrough.

## Intervention signal taxonomy

Do not make missing tasks the hero of the Intervention Radar.

| Signal type | Example | Strategic value |
|---|---|---|
| Decision intervention | Critical payer or approver unresolved; price cannot support economics; evidence contradicts target customer; critical assumption unsupported | Core VERTEX value |
| Workflow attention | Baseline missing; post assessment incomplete; DecisionRecord not submitted | Necessary operations, but not differentiation |

In a live demo, show a decision intervention first. Keep missing-data handling as a trust signal in the report.

## UX direction

The founder should not perceive VERTEX as a sequence of modules.

The founder should perceive a progressively built decision file:

```text
Your Decision Case
  What I currently believe
  -> What I know
  -> What I am assuming
  -> Who can make this work or fail
  -> What the economics imply
  -> What changed
  -> What I am deciding now
```

Educational content should appear only when it helps the founder move their own decision forward.

Examples:

- Quick concept: `Problem != solution`
- Quick concept: `Revenue is not what you keep`
- Quick concept: `The buyer, user, payer, approver, and blocker may be different people`

Each concept should immediately return to the founder's case.

## Playful direction

Do not use consumer gamification patterns such as XP, streaks, leaderboards, or public rankings.

The game is discovering the business:

- Assumption uncovered
- System reveal
- Contradiction detected
- Decision changed
- Evidence gap found
- Blocker identified

This can feel satisfying and visual while preserving institutional seriousness.

## Evidence discipline

Keep this as an internal rule:

"Demo data must not be mixed with claims from real pilots."

This is not just a sales caveat. It is the product culture VERTEX should embody: know what is evidence, know what is hypothesis, and do not blur the two.

Also keep this rule:

"A negative pilot result is valid evidence, not a failed marketing exercise."

## First pilot measurement

Separate the pilot into three evidence layers.

| Layer | What to measure |
|---|---|
| Feasibility / product behavior | Completion rate, baseline capture before intervention, time per stage, drop-off, DecisionRecord completion, Decision Memo usefulness, facilitator use frequency |
| Proximal founder-reasoning change | Assumptions changed, new stakeholders/buyers/approvers identified, economic assumptions changed, decision changed, next experiment became more specific, evidence gaps became explicit |
| Institutional utility | Useful Intervention Radar alerts, time from signal to intervention, substantive interventions resolved, report usage, report replacement/improvement over existing process, repeat intent, willingness to pay |

Commercial north-star:

"A buyer observes credible founder decision progress, uses that information to run the program differently, and pays to have that visibility again."

## Rehearsal scorecard

After each live rehearsal, score:

| Question | Pass signal |
|---|---|
| Did the buyer understand what the institution buys? | They describe visibility into cohort decision change. |
| Did the Intervention Radar land? | They ask how facilitators would use it during the program. |
| Did the Outcome Report land? | They ask whether they can share/export/customize it. |
| Did the no-overclaim stance land? | They repeat that VERTEX does not predict startup success. |
| Did the paid pilot ask land? | They can name a cohort where this would be tested. |
| Did the sale move beyond politeness? | They name approval owner, budget friction, evidence threshold, or reason not to proceed. |
