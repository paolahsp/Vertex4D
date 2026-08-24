# VERTEX Institutional Trust Pack

## Purpose

This document defines the minimum trust package VERTEX should prepare before selling or launching paid institutional pilots with universities, accelerators or public-sector entrepreneurship programs.

It is not a legal certification, DPA template, penetration-test report, SOC 2 claim or enterprise compliance statement.

It is a practical buyer/procurement readiness checklist.

## Commercial Boundary

VERTEX should currently be sold as:

```text
VERTEX Decision Quality Pilot
4-6 weeks
Up to 15 teams
Fixed pilot fee
Limited data scope
No LMS/SSO integration required
Outcome Review at the end
```

Do not sell it yet as:

- proven institutional platform;
- startup success prediction system;
- AI grading system;
- replacement for accelerator management software;
- enterprise compliance-ready SaaS.

## Required Buyer-Facing Statements

Use:

```text
VERTEX records and structures decision reasoning. It does not predict startup success.
```

```text
The pilot evaluates feasibility, observed reasoning change, facilitator usefulness and buyer value.
```

```text
Missing data stays missing. VERTEX does not infer or fabricate outcomes.
```

```text
For learning outcome claims in the pilot, scoring is human-reviewed; AI does not grade students or rank startups.
```

Avoid:

- "The AI validates the startup."
- "VERTEX proves decision quality improved."
- "The method works."
- "Below tender threshold."
- "No other platform can do this."

## Minimum Documents Before Paid Pilot

Prepare these before broad outreach:

1. Data Processing Addendum draft.
2. Subprocessor list.
3. Data retention and deletion policy.
4. Data location statement.
5. AI/data-use statement.
6. Security controls summary.
7. Access-control model.
8. Privacy and consent language for founders.
9. Accessibility QA note.
10. Pilot evaluation protocol.

## Data Processing Addendum Draft

Should cover:

- parties and roles;
- controller/processor relationship;
- categories of data;
- categories of data subjects;
- processing purpose;
- retention period;
- deletion or return at end of pilot;
- confidentiality;
- subprocessors;
- security measures;
- incident notification;
- audit/cooperation language.

Status:

```text
Needed before university procurement.
```

## Subprocessor List

Should include:

- hosting provider;
- database/storage provider if external;
- AI API provider if used;
- email provider if used;
- analytics provider if used;
- document/PDF provider if external.

For each:

- company name;
- service purpose;
- data processed;
- location/region if known;
- privacy/security link;
- whether data is used for model training.

Status:

```text
Needed before pilot launch.
```

## Data Retention And Deletion

Define:

- default retention for demo data;
- default retention for pilot data;
- deletion process after pilot;
- archive process for buyer report;
- deletion of runtime artifacts;
- deletion of SQLite/database records;
- deletion of generated PDFs/screenshots.

Recommended pilot language:

```text
Pilot data will be retained only for the pilot period and agreed evaluation window, then exported, archived or deleted according to the institution's written instruction.
```

## Data Location Statement

State plainly:

- where the app is hosted;
- where database files are stored;
- where generated artifacts live;
- whether data leaves the environment;
- whether AI/API calls are made;
- which regions are used if known.

If not decided:

```text
Data location will be confirmed during pilot setup and documented before founder onboarding.
```

## AI/Data-Use Statement

Must answer:

- Does VERTEX send founder data to external AI providers?
- Which modules use AI?
- Is AI used to score founders?
- Is data used to train models?
- Can AI be disabled for the pilot?
- What is human-reviewed?

Recommended stance:

```text
AI may help structure prompts, summaries or artifacts, but pilot learning-outcome claims rely on human-reviewed scoring. VERTEX should not be positioned as autonomous AI grading.
```

## Security Controls Summary

Minimum summary should include:

- authentication model;
- facilitator allowlist/invite-code control;
- role-based visibility;
- session secret requirement;
- local artifact storage;
- database backup responsibility;
- environment variables;
- logging/audit events;
- deletion process;
- known gaps.

Known current gaps to state honestly:

- no SSO/SAML yet;
- no formal penetration test yet;
- no SOC 2/ISO 27001 claim;
- no enterprise device-management integration;
- no formal accessibility certification.

## Access-Control Model

Current pilot model:

- founders can access their own team/run;
- facilitator/admin can view cohort cases;
- facilitator/admin can access Outcome Report;
- facilitator/admin can approve or review DecisionRecords;
- founder access to institutional reports should be restricted.

Document:

- who can see baseline data;
- who can see comments;
- who can see rubric scores;
- who can see Decision Memos;
- who can see Outcome Report.

## Founder Consent Language

Suggested language:

```text
During this pilot, VERTEX will store your team profile, baseline decision snapshot, assumptions, evidence notes, stakeholder map, financial assumptions, facilitator comments, rubric scores and final DecisionRecord. Your program facilitator may view this information to support the cohort and prepare a cohort outcome report. VERTEX is used to document decision quality and learning; it does not predict startup success or guarantee validation.
```

## Accessibility QA

Before broad university outreach, complete:

- contrast audit;
- keyboard navigation pass;
- mobile viewport pass;
- print artifact readability check;
- no overlapping controls;
- labels for icon-only buttons;
- visible focus states.

Current stance:

```text
Accessibility and responsive QA are pilot-hardening items. Do not overclaim WCAG compliance until tested.
```

## Pilot Evaluation Protocol

The pilot should measure:

- journey completion;
- baseline capture rate;
- DecisionRecord completion;
- paired baseline/post measurement;
- decision intervention usefulness;
- facilitator time spent;
- buyer usefulness of Outcome Report;
- rubric reliability if external raters are used;
- willingness to run another cohort.

Do not claim causality from a single-group pre/post pilot.

Use levels:

```text
Pilot level: observed change.
Repeated cohorts: repeated pattern and instrument reliability.
Causal level: requires comparative or randomized design.
```

## Procurement Language

Use:

```text
The pilot has deliberately limited scope and cost to support an experimental purchase where the institution's internal rules allow it. We confirm procurement, privacy and security requirements before contracting.
```

Avoid:

```text
This is below the tender threshold.
```

Reason:

Tender thresholds do not remove internal institutional procurement rules.

## Current GO / NO-GO

GO:

- sell paid Decision Quality Pilots;
- show demo with synthetic data;
- run limited pilots with clear data scope;
- use Decision Memo and Outcome Report as buyer artifacts.

NO-GO:

- sell as proven institutional platform;
- claim VERTEX improves decision quality causally;
- claim AI scoring validates students/founders;
- sell annual licenses before real paid-pilot evidence;
- scale into SSO/LMS/white-label before validating demand.

## Buyer Procurement Checklist

Before pilot launch:

- confirm cohort name and dates;
- confirm number of teams;
- confirm data owner/contact;
- confirm facilitator/admin users;
- confirm founder consent copy;
- confirm whether AI calls are enabled;
- confirm retention/deletion window;
- confirm whether security review is required;
- confirm whether accessibility review is required;
- confirm invoicing/procurement path.

## Pass Signal

A commercial rehearsal or buyer call is successful when the buyer can say:

```text
I have a cohort where this could be tested.
I understand what artifact I would receive.
I know who must approve data/security/procurement.
The pilot price does not kill the conversation.
```
