# VERTEX Privacy And Data Handling

This is a practical pilot-readiness note, not an enterprise compliance claim. VERTEX is not yet an enterprise security/compliance product.

## What VERTEX stores locally

By default, VERTEX stores structured data in SQLite and artifacts as JSON files.

SQLite location:

- `VERTEX4D_DATABASE_PATH` if set
- otherwise `vertex4d.db`

Artifact runtime location:

- `VERTEX4D_RUNTIME_DIR` if set
- otherwise `.vertex_runtime\runs`

## Stored data categories

Teams and members:

- team name
- member names
- member emails
- member roles
- team password hash
- challenge description

Decision Cases/runs:

- run ID
- team ID
- title/case title
- stage/status
- mode/cohort ID
- deadline
- timestamps

Baseline snapshots:

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

Artifacts:

- ProjectRecord
- ProblemFrame
- SystemMap
- PredictiveHypothesis
- FinancialScenario
- DecisionRecord
- artifact IDs and local file paths

Comments:

- facilitator/founder comment text
- author email/role
- artifact type
- open/resolved status
- timestamps

Rubric scores:

- reviewer email
- baseline/post stage
- six score dimensions
- notes

Events:

- run creation
- baseline capture
- artifact save
- approvals
- pilot feedback
- other workflow events

AI usage:

- team ID
- run ID
- module
- token estimate/count
- timestamp

## Data that may be sensitive

Treat these as sensitive in a real pilot:

- founder names and emails
- venture descriptions
- customer, payer, approver, blocker details
- pricing assumptions
- financial scenarios
- comments from facilitators
- rubric scores
- evidence notes
- strategic decisions and next experiments

Avoid entering personal data about third parties unless the pilot has explicit consent and a clear need.

## Visibility model

Founder visibility:

- A founder sees their own team and runs.
- A founder can read comments on their own Decision Case.
- A founder should not be able to view other teams' cases through normal routes.

Facilitator/admin visibility:

- A facilitator/admin can view cohort-level dashboards and cases.
- A facilitator/admin can see all runs in facilitator metrics.
- A facilitator/admin can add/resolve comments and save rubric scores.
- A facilitator/admin can approve/sign the final DecisionRecord.

This visibility model is appropriate for a controlled pilot, but it is not a substitute for enterprise tenant isolation, audit administration, or compliance review.

## Demo data vs real pilot data

Demo data uses:

- team names starting with `Demo:`
- emails ending in `@northstar-demo.example`
- run IDs starting with `run_demo_`
- cohort name `Demo Cohort - Decision Quality Pilot`
- institution name `Northstar Entrepreneurship Center`

Demo reset deletes only demo-marked data. It is not a general deletion tool for real pilots.

## Environment variables

Set before a real cohort:

- `VERTEX4D_SESSION_SECRET`: required for real use. The default development secret is unsafe.
- `VERTEX4D_FACILITATOR_EMAILS` or `VERTEX4D_FACILITATOR_INVITE_CODE`: controls facilitator/admin registration.
- `VERTEX4D_DATABASE_PATH`: choose a known DB location.
- `VERTEX4D_RUNTIME_DIR`: choose a known artifact storage location.
- `VERTEX4D_LLM_RUN_BUDGET`: optional budget guard for LLM calls.

AI/API keys:

- `OPENAI_API_KEY`
- `ALEX_OPENAI_API_KEY`

Only set API keys in an environment where pilot data is allowed to be processed by those services. Do not paste keys into docs, screenshots, or shared terminals.

## Suggested pilot consent language

"During this pilot, VERTEX will store your team profile, Decision Case baseline, assumptions, evidence notes, stakeholder map, financial assumptions, facilitator comments, rubric scores, and final DecisionRecord. The institution's facilitator may view your case to support the cohort and prepare an outcome report. VERTEX is used to document decision quality and learning; it does not predict startup success or guarantee validation."

## Deletion/export caveats

Implemented today:

- browser print / Save as PDF for Decision Memo
- browser print / Save as PDF for Cohort Outcome Report
- demo-only reset for demo-marked data
- local DB/runtime files that can be backed up manually

Not implemented yet:

- full per-team data export package
- automated real-cohort deletion workflow
- retention policies
- enterprise audit logs
- SSO
- role administration UI
- data processing agreements
- automated redaction

## Buyer-facing privacy summary

VERTEX stores founder cohort decision data locally in SQLite and JSON artifact files. Facilitators can view cohort cases so they can support founders and produce outcome reports. Founders should be told what is stored and who can see it before the pilot starts. VERTEX is pilot-ready for controlled institutional use, but it is not yet an enterprise compliance platform.
