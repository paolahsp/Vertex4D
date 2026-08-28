# VERTEX 4D — Cohort setup

Operational checklist for running a facilitated cohort or a founder pilot.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `VERTEX4D_SESSION_SECRET` | **yes, before any real cohort** | Signs session cookies. Leaving the default means sessions can be forged. |
| `VERTEX4D_FACILITATOR_EMAILS` | one of these two | Comma-separated allowlist of emails permitted to hold `facilitator` / `admin`. |
| `VERTEX4D_FACILITATOR_INVITE_CODE` | one of these two | Shared cohort code that grants the same roles at registration. |
| `OPENAI_API_KEY` | for SynapMap | Backs `/api/openai/chat`. |
| `ALEX_OPENAI_API_KEY` | for Alex | Backs `/api/alex/chat`. |
| `VERTEX4D_LLM_RUN_BUDGET` | no (default `20`) | Max LLM calls per run before the proxies return `429`. |
| `VERTEX4D_DATABASE_PATH` | no | SQLite location. |
| `VERTEX4D_RUNTIME_DIR` | no | Artifact store root (`.vertex_runtime/runs` by default). |

## Why the facilitator role is gated

A facilitator can do two things a founder cannot:

1. Sign a `DecisionRecord` — the artifact a founder shows an investor and an
   incubator archives. Its strongest claim is "a facilitator approved this."
2. Read **every team's run** in `/dashboard/facilitator` — problem statements,
   stakeholders, prices and financial scenarios across the whole cohort.

So the role is granted by the program, never self-selected. If neither
`VERTEX4D_FACILITATOR_EMAILS` nor `VERTEX4D_FACILITATOR_INVITE_CODE` is set,
registration **refuses** an elevated role with an explicit message rather than
quietly downgrading it — nobody should believe they hold an authority they were
not granted.

Without one of them configured, no account can sign a DecisionRecord and the
Golden Path cannot be completed. Set one before the cohort starts.

### Example (PowerShell)

```powershell
$env:VERTEX4D_SESSION_SECRET = "<a long random string>"
$env:VERTEX4D_FACILITATOR_EMAILS = "facilitadora@programa.org"
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Prefer the allowlist when facilitators are known in advance. Use the invite code
when a partner institution registers its own facilitators; rotate it per cohort.

## Regression check

```powershell
python scripts\validate_contracts.py
python scripts\smoke_vertex_golden_path.py
```

The first runs the contract suite plus its negative mutations. The second builds
a full chain — `ProjectRecord → ProblemFrame → SystemMap → PredictiveHypothesis
→ FinancialScenario → DecisionRecord` — in a temporary database, and asserts
that a founder is refused the final signature while an authorized facilitator is
not. Both must pass before a cohort session.
