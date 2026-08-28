# VERTEX 4D / Srsly Labs Deployment Readiness

This guide prepares a semi-private VERTEX 4D / Srsly Labs deployment without committing secrets or deploying by memory.

## 1. Deployment Readiness

Ready:

- Product branch is pushed and available in PR #1.
- VERTEX Quest and Srsly Labs Lab are separated.
- Accelerator Demo Mode is available for buyer/program review.
- Technical smoke tests and visual QA passed before this document was created.

Required before deploy:

- Configure host secrets and persistent storage paths.
- Install runtime dependencies.
- Seed the demo cohort once on the persistent deployment database.
- Run a post-deploy smoke pass.
- Prepare minimum trust copy for semi-private users.

Do not commit secrets. Do not paste API keys into chat, tickets, docs, screenshots, or committed files.

## 2. Required Environment Variables

| Variable | Status | Purpose | Example placeholder | Notes / risk |
| --- | --- | --- | --- | --- |
| `VERTEX4D_SESSION_SECRET` | Required | Signs user sessions. | `replace-with-a-long-random-secret` | The code has a development default; do not use it in deploy. |
| `VERTEX4D_DATABASE_PATH` | Required | SQLite application database path. | `/data/vertex4d.db` | Must be on persistent storage or accounts/demo data can disappear. |
| `VERTEX4D_RUNTIME_DIR` | Required | Saved Quest run artifacts. | `/data/runs` | Must persist with the DB or run artifacts can disappear. |
| `VERTEX4D_BILLIE_SCENARIO_DIR` | Recommended | Saved Ledger financial scenarios. | `/data/billie/financial_scenarios` | If omitted, defaults under local `.vertex_runtime/`, which may be ephemeral on hosts. |
| `VERTEX4D_FACILITATOR_EMAILS` | Required for facilitator demo | Comma-separated allowlist for facilitator/admin registration. | `facilitator@example.org` | Without allowlist or invite code, elevated facilitator registration is refused. |
| `VERTEX4D_FACILITATOR_INVITE_CODE` | Optional | Private invite code for elevated roles. | `replace-with-private-program-invite-code` | Treat as a secret. Do not share in buyer materials. |
| `OPENAI_API_KEY` | Required for general AI tools | Used by `/api/openai/chat`. | `replace-with-host-secret` | Required for SynapMap, Tangle, and Billie Storyteller AI calls. |
| `ALEX_OPENAI_API_KEY` | Required for Alex/Riddle | Used by `/api/alex/chat`. | `replace-with-host-secret` | Required for Alex and Riddle chat flows. |
| `VERTEX4D_LLM_RUN_BUDGET` | Recommended | Per run/team LLM call budget. | `20` | Helps control demo cost. Default is `20`. |
| `PORT` | Host dependent | Port used by the process manager command. | `8001` | The app does not read `PORT` directly; the start command passes it to Uvicorn. |

## 3. Persistence

Use persistent host storage for:

- SQLite DB via `VERTEX4D_DATABASE_PATH`.
- Quest run artifacts via `VERTEX4D_RUNTIME_DIR`.
- Ledger financial scenarios via `VERTEX4D_BILLIE_SCENARIO_DIR`.

The DB and runtime artifacts should be backed up together. A run row without its artifact JSON files can make Brief, Outcome Report, and Quest review flows incomplete.

Do not commit:

- `.env`
- `*.db`, `*.sqlite`, `*.sqlite3`
- `.vertex_runtime/`
- `.demo_hardening_runtime/`
- `.demo_rehearsal_runtime/`
- temporary screenshots or local QA output

The current `.gitignore` already covers the main DB and runtime patterns.

## 4. Install / Dependencies

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

Runtime dependencies in `requirements.txt` are based on imports used by the app:

- FastAPI
- Uvicorn
- Starlette
- httpx
- pypdf
- python-docx
- jsonschema
- python-multipart
- Jinja2
- itsdangerous

Optional QA/reporting scripts may require additional local tooling such as Playwright, Pillow, and ReportLab. Keep those separate unless the deploy host will run visual capture or report generation jobs.

## 5. Start Command

Recommended deploy command:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

Windows / PowerShell local equivalent:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port $env:PORT
```

If `PORT` is not supplied locally, use an explicit port:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

## 6. Demo Seed

Seed the institutional demo cohort:

```bash
python -m scripts.seed_demo_cohort
```

Run this once against the persistent deployment DB. The script resets existing demo-marked data before reseeding and prints the current `cohort_id`.

Demo facilitator:

```text
facilitator@northstar-demo.example / vertex-demo-2026
```

Demo founders:

```text
maya.ellis@northstar-demo.example / vertex-demo-2026
jonah.park@northstar-demo.example / vertex-demo-2026
ari.santos@northstar-demo.example / vertex-demo-2026
nadia.chen@northstar-demo.example / vertex-demo-2026
leah.morgan@northstar-demo.example / vertex-demo-2026
```

Save the printed `cohort_id`. Use it in buyer demo URLs:

```text
/dashboard/facilitator/cohorts/<cohort_id>/accelerator-demo
/dashboard/facilitator/cohorts/<cohort_id>/outcome-report
```

Keep demo credentials semi-private. Rotate or reseed before broader sharing.

## 7. AI / API Key Safety

Configure API keys only as host secrets or local uncommitted environment variables:

- `OPENAI_API_KEY`
- `ALEX_OPENAI_API_KEY`

Never hardcode keys. Never paste keys into chat, docs, screenshots, pull requests, or committed files.

AI routes and tools:

| Route | Tool | Endpoint used | Trigger |
| --- | --- | --- | --- |
| `/dashboard/lab/alex` | Alex | `/api/alex/chat` | User sends chat message. |
| `/dashboard/vertex/riddle` | Riddle | `/api/alex/chat` | User sends interview/chat message. |
| `/dashboard/lab/synapmap` | SynapMap | `/api/openai/chat` | User asks SynapMap to analyze entered/uploaded content. |
| `/dashboard/vertex/tangle` | Tangle | `/api/openai/chat` | User asks Tangle to analyze entered/uploaded content. |
| `/dashboard/lab/billie` | Billie Storyteller | `/api/openai/chat` | User clicks Generate narrative. |

Nothing should send data to OpenAI automatically on page load. SynapMap/Tangle file uploads can extract text from uploaded files; that extracted text may be sent to AI if the user then activates analysis.

## 8. Trust / Limits

Minimum trust language for semi-private demo:

- Do not paste sensitive data, third-party personal data, or confidential information without permission.
- AI outputs are assisted drafts for review.
- VERTEX does not predict startup success.
- VERTEX makes evidence and decision changes visible; it does not prove outcomes.
- D-Predict/MiroFish v1 is a scenario stress-test workbench, not factual prediction or market forecast.
- The Orbit v1 is manual/local and does not perform external monitoring, live signal feeds, or automatic matching.
- Ripple produces bounded `PredictiveHypothesis` artifacts, not real-world prediction claims.
- Ledger remains the Quest financial scenario module.
- Final decisions stay with the founder/facilitator, not the AI.

## 9. Post-Deploy Smoke Checklist

After deploy, log in and check:

- `/login`
- `/dashboard/lab`
- `/dashboard/lab/alex`
- `/dashboard/lab/synapmap`
- `/dashboard/lab/billie`
- `/dashboard/lab/d-predict`
- `/dashboard/orbit`
- `/dashboard/vertex/quest`
- `/dashboard/vertex/ripple`
- `/dashboard/vertex/ledger`
- `/dashboard/facilitator`
- `/dashboard/facilitator/accelerator-demo`
- `/dashboard/facilitator/cohorts/<cohort_id>/accelerator-demo`
- `/dashboard/facilitator/cohorts/<cohort_id>/outcome-report`

Post-deploy checks:

- App starts without using default session secret.
- Demo facilitator login works.
- Demo cohort appears in facilitator dashboard.
- Accelerator Demo Mode opens.
- Outcome Report opens.
- Brief opens for a run owned by the logged-in founder or accessible to facilitator.
- SynapMap mobile layout is usable.
- Billie Storyteller shows the sensitive-data warning.
- D-Predict/MiroFish and Orbit display local/manual/no-overclaim limits.
- First AI test returns a response only after user action.

## 10. Known Follow-Ups

- Prepare fuller trust pack: privacy, AI use, data retention, deletion, security, and limits.
- Deploy semi-private environment.
- Configure API keys as host secrets.
- Run buyer-facing rehearsal on the deployed URL.
- Define FinOps Central v1 as a hub over Ledger rather than duplicating Ledger.
- Audit deeper QBI/Atlas integration before connecting any heavier engine.
