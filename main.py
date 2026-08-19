from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import json
from pathlib import Path
import database
import artifacts
import contracts_runtime
import httpx
import io
from pypdf import PdfReader
from docx import Document
from jsonschema import Draft202012Validator, FormatChecker
from datetime import datetime, timezone

app = FastAPI(title="Vertex 4D", description="Private 4D client profile portal")

# Add Session Middleware
SESSION_SECRET = os.getenv("VERTEX4D_SESSION_SECRET", "vertex4d-secret-key-change-me")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

BASE_DIR = Path(__file__).resolve().parent
GOLDEN_CASE_DIR = BASE_DIR / "fixtures" / "golden-case" / "v1"
FINANCIAL_SCENARIO_SCHEMA_PATH = BASE_DIR / "contracts" / "v1" / "financial-scenario.schema.json"
BILLIE_SCENARIO_DIR = Path(os.getenv("VERTEX4D_BILLIE_SCENARIO_DIR", BASE_DIR / ".vertex_runtime" / "billie" / "financial_scenarios"))
GOLDEN_CASE_FILES = {
    "project_record": "project-record.json",
    "problem_frame": "problem-frame.json",
    "system_map": "system-map.json",
    "predictive_hypothesis": "predictive-hypothesis.json",
    "financial_scenario": "financial-scenario.json",
    "decision_record": "decision-record.json",
}

# Dependency to get current user from session
def get_current_user(request: Request):
    user = request.session.get("user")
    return user

def load_vertex_golden_case():
    artifacts = {}
    for key, filename in GOLDEN_CASE_FILES.items():
        artifact_path = GOLDEN_CASE_DIR / filename
        artifacts[key] = json.loads(artifact_path.read_text(encoding="utf-8"))
    return artifacts

def validate_financial_scenario_schema(artifact: dict):
    schema = json.loads(FINANCIAL_SCENARIO_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(artifact), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "root"
        errors.append({"path": path, "message": error.message})
    return errors

def billie_team_dir(user: dict) -> Path:
    team_id = str(user.get("team_id", "unknown"))
    safe_team_id = "".join(ch for ch in team_id if ch.isalnum() or ch in {"_", "-"}) or "unknown"
    return BILLIE_SCENARIO_DIR / f"team_{safe_team_id}"

def require_safe_artifact_id(artifact_id: str) -> str:
    if not isinstance(artifact_id, str) or not artifact_id:
        raise HTTPException(status_code=400, detail="artifact_id is required")
    if not artifact_id[0].isalnum() or any(not (ch.isalnum() or ch in {"_", "-"}) for ch in artifact_id):
        raise HTTPException(status_code=400, detail="artifact_id is not safe for local storage")
    return artifact_id

def financial_scenario_summary(artifact: dict) -> dict:
    return {
        "artifact_id": artifact.get("artifact_id"),
        "scenario_name": artifact.get("scenario_name"),
        "currency": artifact.get("currency"),
        "status": artifact.get("status"),
        "approval_state": artifact.get("approval_state"),
        "time_horizon": artifact.get("time_horizon"),
        "updated_at": artifact.get("updated_at"),
        "revenue_projection": artifact.get("revenue_projection", {}).get("value"),
        "cash_requirement": artifact.get("cash_requirement", {}).get("value"),
        "uncertainty_level": artifact.get("uncertainty", {}).get("level"),
    }

def get_team_id(user: dict) -> int:
    try:
        return int(user.get("team_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid team session")


VALID_APPROVER_ROLES = {"founder", "facilitator", "admin"}


def get_user_role(user: dict) -> str:
    role = str((user or {}).get("role") or "founder").strip().lower()
    return role if role in VALID_APPROVER_ROLES else "founder"


# --- Program control over elevated roles ---
# A facilitator can sign DecisionRecords and read every team's run in the cohort
# dashboard, so the role must be granted by the program, never self-selected.
ELEVATED_ROLES = {"facilitator", "admin"}


def facilitator_email_allowlist() -> set[str]:
    raw = os.getenv("VERTEX4D_FACILITATOR_EMAILS", "")
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def facilitator_invite_code() -> str:
    return os.getenv("VERTEX4D_FACILITATOR_INVITE_CODE", "").strip()


def program_role_control_configured() -> bool:
    return bool(facilitator_email_allowlist() or facilitator_invite_code())


def authorize_member_roles(requested_members: list[dict], invite_code: str) -> tuple[list[dict], str | None]:
    """Resolve requested member roles against program authorization.

    Elevated roles are refused with an explicit error rather than silently
    downgraded, so nobody believes they hold an authority they were not granted.
    """
    allowlist = facilitator_email_allowlist()
    expected_code = facilitator_invite_code()
    supplied_code = str(invite_code or "").strip()
    resolved = []

    for member in requested_members:
        email = str(member.get("email") or "").strip()
        role = str(member.get("role") or "founder").strip().lower()

        if role not in VALID_APPROVER_ROLES:
            return [], f"Unknown role '{member.get('role')}' requested for {email or 'a member'}."

        if role in ELEVATED_ROLES:
            if not program_role_control_configured():
                return [], (
                    f"The {role} role is not available on this deployment yet. "
                    "A program administrator must configure VERTEX4D_FACILITATOR_EMAILS "
                    "or VERTEX4D_FACILITATOR_INVITE_CODE before a facilitator can be registered."
                )
            authorized = email.lower() in allowlist or (
                bool(expected_code) and supplied_code == expected_code
            )
            if not authorized:
                return [], (
                    f"{email or 'This member'} is not authorized for the {role} role. "
                    "A facilitator must be on the program allowlist or register with a valid program invite code."
                )

        resolved.append({"name": member.get("name"), "email": email, "role": role})

    return resolved, None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def approved_human_approval(role: str, note: str, now: str) -> dict:
    return {
        "required": True,
        "state": "approved",
        "approved_by_role": role,
        "approved_at": now,
        "notes": note or "Approved for bounded VERTEX processing.",
    }


def normalize_approved_gate_from_session(gate: dict | None, role: str) -> None:
    if isinstance(gate, dict) and gate.get("state") == "approved":
        gate["approved_by_role"] = role


def artifact_with_session_approval(artifact: dict, user: dict) -> dict:
    normalized = json.loads(json.dumps(artifact))
    role = get_user_role(user)
    normalize_approved_gate_from_session(normalized.get("human_approval"), role)
    normalize_approved_gate_from_session(normalized.get("facilitator_approval"), role)
    return normalized


def approval_selection_map(payload: dict) -> dict:
    raw_approvals = payload.get("approvals") if isinstance(payload, dict) else None
    if isinstance(raw_approvals, dict):
        iterable = []
        for key, value in raw_approvals.items():
            if not isinstance(value, dict):
                raise HTTPException(status_code=400, detail="approval object values must be objects")
            iterable.append({"assumption_id": key, **value})
    elif isinstance(raw_approvals, list):
        iterable = raw_approvals
    else:
        raise HTTPException(status_code=400, detail="approvals must be a list or object")

    selections = {}
    for item in iterable:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="approval entries must be objects")
        assumption_id = str(item.get("assumption_id") or "").strip()
        if not assumption_id:
            raise HTTPException(status_code=400, detail="approval entry missing assumption_id")
        selections[assumption_id] = {
            "predictive": bool(item.get("approved_for_predictive_processing", item.get("predictive", False))),
            "financial": bool(item.get("approved_for_financial_processing", item.get("financial", False))),
        }
    if not any(item["predictive"] or item["financial"] for item in selections.values()):
        raise HTTPException(status_code=400, detail="Approve at least one assumption for processing")
    return selections


def get_current_run_or_404(run_id: str, user: dict) -> dict:
    run = database.get_run(run_id, get_team_id(user))
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def artifact_response(run_id: str, artifact_type: str, artifact: dict) -> dict:
    return {
        "run_id": run_id,
        "artifact_type": artifact_type,
        "artifact": artifact,
        "summary": artifacts.artifact_summary(artifact),
    }


def split_founder_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    items = []
    for chunk in str(raw).replace(";", "\n").replace(",", "\n").splitlines():
        value = chunk.strip()
        if value:
            items.append(value)
    return items


def build_metric_baseline(payload: dict) -> dict:
    price_raw = payload.get("baseline_intuition_price")
    try:
        intuition_price = float(price_raw) if str(price_raw or "").strip() else None
    except (TypeError, ValueError):
        intuition_price = None
    stakeholders = split_founder_list(payload.get("baseline_stakeholders"))
    return {
        "source": "start_golden_path",
        "initial_problem_statement": str(payload.get("baseline_problem_statement") or "").strip(),
        "initial_stakeholders": stakeholders,
        "initial_stakeholder_count": len(stakeholders),
        "intuition_price": intuition_price,
        "intuition_price_currency": str(payload.get("baseline_price_currency") or payload.get("currency") or "").strip().upper(),
        "intuition_pricing_note": str(payload.get("baseline_pricing_note") or "").strip(),
    }


def latest_event_payload(events: list[dict], event_type: str) -> dict:
    for event in reversed(events):
        if event.get("event_type") == event_type:
            payload = event.get("payload")
            return payload if isinstance(payload, dict) else {}
    return {}


def stakeholder_label(item: dict) -> str:
    for key in ("name", "label", "stakeholder_name", "title", "stakeholder_id"):
        value = item.get(key) if isinstance(item, dict) else None
        if value:
            return str(value).strip()
    return ""


def first_pricing_value(financial_scenario: dict | None) -> float | None:
    """Headline price of a FinancialScenario.

    Matching on label text alone is brittle: it works for Billie's own
    "Suggested price" but silently returns nothing for any scenario worded
    differently (the golden case included), which would blank the price-change
    metric without any error. Prefer Billie's stable assumption_id, then fall
    back to the first pricing assumption by position -- the same one Billie's UI
    treats as the price -- and only then to label text.
    """
    if not financial_scenario:
        return None
    items = [item for item in (financial_scenario.get("pricing_assumptions") or []) if isinstance(item, dict)]
    if not items:
        return None

    def numeric(item: dict) -> float | None:
        try:
            return float(item.get("value"))
        except (TypeError, ValueError):
            return None

    for item in items:
        if str(item.get("assumption_id") or "") == "fin_price_suggested":
            value = numeric(item)
            if value is not None:
                return value

    for item in items:
        label = str(item.get("label") or "").lower()
        if "suggested" in label:
            value = numeric(item)
            if value is not None:
                return value

    return numeric(items[0])


def build_facilitator_metrics(user: dict) -> dict:
    role = get_user_role(user)
    team_id = get_team_id(user)
    include_all = role in {"facilitator", "admin"}
    runs = database.list_runs_for_facilitator(team_id, include_all=include_all)
    run_ids = [run["run_id"] for run in runs]
    events_by_run = database.list_events_for_runs(run_ids)
    ai_usage_by_run = database.get_ai_usage_by_runs(run_ids)
    rows = []
    totals = {"runs": len(runs), "complete": 0, "stakeholder_delta": 0, "ai_calls": 0, "would_pay": 0, "would_recommend": 0, "feedback_captured": 0}

    for run in runs:
        run_id = run["run_id"]
        events = events_by_run.get(run_id, [])
        baseline = latest_event_payload(events, "metric_baseline_captured")
        feedback = latest_event_payload(events, "pilot_feedback_captured")
        problem_frame = artifacts.load_artifact(run_id, "problem_frame")
        system_map = artifacts.load_artifact(run_id, "system_map")
        financial_scenario = artifacts.load_artifact(run_id, "financial_scenario")
        decision_record = artifacts.load_artifact(run_id, "decision_record")

        initial_problem = baseline.get("initial_problem_statement") or ""
        final_problem = ((problem_frame or {}).get("reframed_problem") or {}).get("statement") or ""
        initial_stakeholders = baseline.get("initial_stakeholders") or []
        mapped_stakeholders = [stakeholder_label(item) for item in ((system_map or {}).get("stakeholders") or [])]
        mapped_stakeholders = [item for item in mapped_stakeholders if item]
        initial_set = {str(item).strip().lower() for item in initial_stakeholders if str(item).strip()}
        mapped_set = {item.lower() for item in mapped_stakeholders}
        new_stakeholders = sorted(mapped_set - initial_set)
        stakeholder_delta = max(0, len(mapped_set) - len(initial_set))
        intuition_price = baseline.get("intuition_price")
        billie_price = first_pricing_value(financial_scenario)
        price_changed = intuition_price is not None and billie_price is not None and round(float(intuition_price), 2) != round(float(billie_price), 2)
        ai_usage = ai_usage_by_run.get(run_id, {"calls": 0, "tokens": 0})
        complete = decision_record is not None
        if complete:
            totals["complete"] += 1
        totals["stakeholder_delta"] += stakeholder_delta
        totals["ai_calls"] += ai_usage["calls"]
        if feedback:
            totals["feedback_captured"] += 1
            if feedback.get("would_pay") == "yes":
                totals["would_pay"] += 1
            if feedback.get("would_recommend") == "yes":
                totals["would_recommend"] += 1
        rows.append({
            "run_id": run_id,
            "team_name": run.get("team_name") or user.get("team_name") or "Team",
            "title": run.get("title"),
            "stage": run.get("stage"),
            "created_at": run.get("created_at"),
            "artifacts_saved": len(run.get("artifacts") or {}),
            "baseline_captured": bool(baseline),
            "initial_problem": initial_problem,
            "final_problem": final_problem,
            "problem_changed": bool(initial_problem and final_problem and initial_problem.strip().lower() != final_problem.strip().lower()),
            "initial_stakeholder_count": len(initial_set),
            "mapped_stakeholder_count": len(mapped_set),
            "stakeholder_delta": stakeholder_delta,
            "new_stakeholders": new_stakeholders[:5],
            "intuition_price": intuition_price,
            "billie_price": billie_price,
            "price_currency": baseline.get("intuition_price_currency") or (financial_scenario or {}).get("currency") or "",
            "price_changed": price_changed,
            "decision": ((decision_record or {}).get("selected_decision") or {}).get("statement") or "",
            "ai_calls": ai_usage["calls"],
            "ai_tokens": ai_usage["tokens"],
            "feedback_captured": bool(feedback),
            "would_pay": feedback.get("would_pay") or "",
            "would_recommend": feedback.get("would_recommend") or "",
            "feedback_note": feedback.get("note") or "",
            "feedback_role": feedback.get("respondent_role") or "",
        })

    totals["completion_rate"] = round((totals["complete"] / totals["runs"] * 100), 1) if totals["runs"] else 0
    answered = totals["feedback_captured"]
    totals["would_pay_rate"] = round((totals["would_pay"] / answered * 100), 1) if answered else 0
    totals["would_recommend_rate"] = round((totals["would_recommend"] / answered * 100), 1) if answered else 0
    return {"role": role, "include_all": include_all, "runs": rows, "totals": totals}
def build_vertex_golden_case_view_model():
    artifacts = load_vertex_golden_case()
    project = artifacts["project_record"]
    problem = artifacts["problem_frame"]
    system_map = artifacts["system_map"]
    prediction = artifacts["predictive_hypothesis"]
    finance = artifacts["financial_scenario"]
    decision = artifacts["decision_record"]

    stages = [
        {
            "key": "project_record",
            "label": "ProjectRecord",
            "agent": "VERTEX",
            "artifact_id": project["artifact_id"],
            "status": project["status"],
            "headline": project["project_name"],
            "summary": project["challenge_statement"],
        },
        {
            "key": "problem_frame",
            "label": "ProblemFrame",
            "agent": "Alex",
            "artifact_id": problem["artifact_id"],
            "status": problem["status"],
            "headline": problem["reframed_problem"]["statement"],
            "summary": f"{len(problem['assumptions'])} assumptions, {len(problem['unknowns'])} unknown preserved.",
        },
        {
            "key": "system_map",
            "label": "SystemMap",
            "agent": "SynapMap",
            "artifact_id": system_map["artifact_id"],
            "status": system_map["status"],
            "headline": f"{len(system_map['stakeholders'])} stakeholders mapped",
            "summary": f"{len(system_map['relationships'])} relationships, {len(system_map['dependencies'])} dependencies, {len(system_map['tensions'])} tensions.",
        },
        {
            "key": "predictive_hypothesis",
            "label": "PredictiveHypothesis",
            "agent": "D-Predict",
            "artifact_id": prediction["artifact_id"],
            "status": prediction["status"],
            "headline": prediction["scenario_question"],
            "summary": f"Bounded scenario with {prediction['uncertainty']['level']} uncertainty and {prediction['confidence']:.0%} confidence.",
        },
        {
            "key": "financial_scenario",
            "label": "FinancialScenario",
            "agent": "FinOps",
            "artifact_id": finance["artifact_id"],
            "status": finance["status"],
            "headline": finance["scenario_name"],
            "summary": f"{finance['time_horizon']} model in {finance['currency']} using approved assumption references.",
        },
        {
            "key": "decision_record",
            "label": "DecisionRecord",
            "agent": "Facilitator",
            "artifact_id": decision["artifact_id"],
            "status": decision["status"],
            "headline": decision["selected_decision"]["statement"],
            "summary": decision["rationale"],
        },
    ]

    return {
        "project": {
            "name": project["project_name"],
            "id": project["project_id"],
            "stage": project["venture_stage"],
            "description": project["venture_description"],
        },
        "stages": stages,
        "metrics": {
            "artifacts_loaded": len(stages),
            "stakeholders": len(system_map["stakeholders"]),
            "assumptions": len(problem["assumptions"]),
            "success_criteria": len(decision["success_criteria"]),
        },
        "decision": decision["selected_decision"],
        "next_experiment": decision["next_experiment"],
        "success_criteria": decision["success_criteria"],
        "stakeholder_responses": prediction["simulated_stakeholder_responses"],
        "risks": decision["risks"],
        "unknowns": decision["unknowns"],
        "financial": {
            "artifact_id": finance["artifact_id"],
            "scenario_name": finance["scenario_name"],
            "time_horizon": finance["time_horizon"],
            "currency": finance["currency"],
            "revenue": finance["revenue_projection"],
            "cost": finance["cost_projection"],
            "cash_requirement": finance["cash_requirement"],
            "approved_assumption_references": finance["approved_assumption_references"],
            "pricing_assumptions": finance["pricing_assumptions"],
            "cost_assumptions": finance["cost_assumptions"],
            "volume_assumptions": finance["volume_assumptions"],
            "sustainability_indicators": finance["sustainability_indicators"],
            "sensitivity_notes": finance["sensitivity_notes"],
            "uncertainty": finance["uncertainty"],
        },
        "warning": prediction["warning"],
        "integration_state": "Fixture-backed contract UI. External adapters are not started.",
    }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request, "index.html", {"user": user})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.png")

# --- Authentication Routes ---

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")

@app.post("/register")
async def register(
    request: Request,
    team_name: str = Form(...),
    password: str = Form(...),
    member1_name: str = Form(...),
    member1_email: str = Form(...),
    member1_role: str = Form("founder"),
    member2_name: str = Form(None),
    member2_email: str = Form(None),
    member2_role: str = Form("founder"),
    member3_name: str = Form(None),
    member3_email: str = Form(None),
    member3_role: str = Form("founder"),
    facilitator_invite_code: str = Form(""),
    challenge_desc: str = Form(None),
    photo_url: str = Form(None)
):
    # Collect members
    requested_members = [{"name": member1_name, "email": member1_email.strip(), "role": member1_role}]
    if member2_name and member2_email:
        requested_members.append({"name": member2_name, "email": member2_email.strip(), "role": member2_role})
    if member3_name and member3_email:
        requested_members.append({"name": member3_name, "email": member3_email.strip(), "role": member3_role})

    members, role_error = authorize_member_roles(requested_members, facilitator_invite_code)
    if role_error:
        return templates.TemplateResponse(request, "auth/register.html", {"error": role_error})

    success, message, team_id = database.create_team(team_name, password, members, challenge_desc, photo_url)
    
    if success:
        # Auto login as the first member using the role saved in team_members.
        team_data = database.login_data_for_email(member1_email.strip()) or database.get_team_by_id(team_id)
        request.session["user"] = team_data
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request, "auth/register.html", {"error": message})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    success, message, team_data = database.verify_login(email.strip(), password.strip())
    
    if success:
        request.session["user"] = team_data
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request, "auth/login.html", {"error": message})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# --- Protected Routes ---

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/course_home.html", {"user": user})

@app.get("/dashboard/phases/sketch", response_class=HTMLResponse)
async def sketch_phase(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/phases/sketch.html", {"user": user})

@app.get("/dashboard/roadmap", response_class=HTMLResponse)
async def roadmap(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/roadmap.html", {"user": user})


@app.get("/dashboard/lab", response_class=HTMLResponse)
async def lab_home(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "lab/base.html", {"user": user})

@app.get("/how-vertex-thinks", response_class=HTMLResponse)
async def how_vertex_thinks_public(request: Request):
    return templates.TemplateResponse(
        request,
        "lab/how_vertex_thinks.html",
        {
            "user": None,
            "back_href": "/",
            "back_label": "Back to home",
            "access_href": "/register",
            "access_label": "Create profile",
        },
    )

@app.get("/dashboard/lab/how-vertex-thinks", response_class=HTMLResponse)
async def how_vertex_thinks(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request,
        "lab/how_vertex_thinks.html",
        {
            "user": user,
            "back_href": "/dashboard/lab",
            "back_label": "Back to 4D Lab",
            "access_href": "/dashboard/lab/golden-path",
            "access_label": "Open Golden Path",
        },
    )
@app.get("/start-golden-path", response_class=HTMLResponse)
async def start_golden_path_public(request: Request):
    return templates.TemplateResponse(request, "lab/start_golden_path.html", {"user": None})
@app.get("/dashboard/lab/start-golden-path", response_class=HTMLResponse)
async def start_golden_path(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/start_golden_path.html", {"user": user})
@app.get("/dashboard/lab/synapmap", response_class=HTMLResponse)
async def synapmap(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/synapmap.html", {"user": user})

@app.get("/dashboard/lab/synapmap-test", response_class=HTMLResponse)
async def synapmap_test(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/synapmap_simple.html", {"user": user})


@app.get("/dashboard/lab/alex", response_class=HTMLResponse)
async def alex(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/alex.html", {"user": user})


@app.get("/dashboard/lab/assumption-approval", response_class=HTMLResponse)
async def assumption_approval(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/assumption_approval.html", {"user": user})

@app.get("/dashboard/lab/d-predict", response_class=HTMLResponse)
async def d_predict(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/d_predict.html", {"user": user})

@app.get("/dashboard/lab/dpredict", response_class=HTMLResponse)
async def dpredict_alias(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard/lab/d-predict", status_code=303)

@app.get("/dashboard/lab/billie", response_class=HTMLResponse)
async def billie(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/billie.html", {"user": user})

@app.get("/dashboard/lab/finops", response_class=HTMLResponse)
async def finops_alias(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard/lab/billie", status_code=303)

@app.get("/dashboard/lab/decision-record", response_class=HTMLResponse)
async def decision_record(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/decision_record.html", {"user": user})

@app.get("/dashboard/lab/decision", response_class=HTMLResponse)
async def decision_record_alias(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard/lab/decision-record", status_code=303)

@app.get("/dashboard/lab/golden-path", response_class=HTMLResponse)
async def vertex_golden_path(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/golden_path.html", {"user": user})

@app.post("/api/vertex/runs")
async def create_vertex_run(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    title = str(payload.get("title") or user.get("challenge_desc") or "Untitled VERTEX run").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Run title is required")
    run_id = artifacts.create_run_id()
    team_id = get_team_id(user)
    run = database.create_run(run_id, team_id, title)
    project_record = artifacts.build_project_record(run_id, user, title, payload)
    errors = contracts_runtime.validate_artifact("project_record", project_record)
    if errors:
        return JSONResponse(status_code=422, content={"created": False, "errors": errors})
    path = artifacts.save_artifact(run_id, "project_record", project_record)
    database.upsert_run_artifact(run_id, "project_record", project_record["artifact_id"], str(path), project_record["status"])
    baseline = build_metric_baseline(payload)
    database.record_event(team_id, "run_created", {"title": title, "project_record_id": project_record["artifact_id"]}, run_id)
    if any([baseline["initial_problem_statement"], baseline["initial_stakeholders"], baseline["intuition_price"] is not None]):
        database.record_event(team_id, "metric_baseline_captured", baseline, run_id)
    run = database.get_run(run_id, team_id)
    return {"created": True, "run": run, "project_record": artifacts.artifact_summary(project_record), "baseline": baseline}


@app.get("/api/vertex/runs")
async def list_vertex_runs(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"runs": database.list_runs(get_team_id(user))}


@app.get("/api/vertex/runs/{run_id}")
async def get_vertex_run(run_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    run = get_current_run_or_404(run_id, user)
    artifact_summaries = {}
    for artifact_type in contracts_runtime.ARTIFACT_ORDER:
        artifact = artifacts.load_artifact(run_id, artifact_type)
        if artifact is not None:
            artifact_summaries[artifact_type] = artifacts.artifact_summary(artifact)
    return {"run": run, "artifacts": artifact_summaries, "artifact_order": contracts_runtime.ARTIFACT_ORDER}


@app.post("/api/vertex/runs/{run_id}/artifacts/{artifact_type}/validate")
async def validate_vertex_run_artifact(run_id: str, artifact_type: str, payload: dict = Body(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    get_current_run_or_404(run_id, user)
    try:
        artifacts.safe_artifact_type(artifact_type)
        payload = artifact_with_session_approval(payload, user)
        upstream = artifacts.load_upstream(run_id, artifact_type)
        errors = contracts_runtime.validate_artifact(artifact_type, payload, upstream)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"valid": len(errors) == 0, "errors": errors, "artifact": payload}


@app.post("/api/vertex/runs/{run_id}/artifacts/{artifact_type}/save")
async def save_vertex_run_artifact(run_id: str, artifact_type: str, payload: dict = Body(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    run = get_current_run_or_404(run_id, user)
    try:
        artifacts.safe_artifact_type(artifact_type)
        payload = artifact_with_session_approval(payload, user)
        upstream = artifacts.load_upstream(run_id, artifact_type)
        errors = contracts_runtime.validate_artifact(artifact_type, payload, upstream)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if errors:
        return JSONResponse(status_code=422, content={"saved": False, "valid": False, "errors": errors})
    path = artifacts.save_artifact(run_id, artifact_type, payload)
    database.upsert_run_artifact(run_id, artifact_type, payload["artifact_id"], str(path), payload.get("status", "draft"))
    database.record_event(get_team_id(user), "artifact_saved", {"artifact_type": artifact_type, "artifact_id": payload["artifact_id"]}, run_id)
    return {"saved": True, "valid": True, "run_id": run["run_id"], "artifact": artifacts.artifact_summary(payload)}


@app.post("/api/vertex/runs/{run_id}/assumption-approvals")
async def save_vertex_assumption_approvals(run_id: str, payload: dict = Body(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    run = get_current_run_or_404(run_id, user)
    selections = approval_selection_map(payload)
    note = str(payload.get("note") or "Approved for bounded VERTEX processing.").strip()
    role = get_user_role(user)
    now = utc_now_iso()

    problem_frame = artifacts.load_artifact(run_id, "problem_frame")
    system_map = artifacts.load_artifact(run_id, "system_map")
    if problem_frame is None or system_map is None:
        raise HTTPException(status_code=404, detail="ProblemFrame and SystemMap are required before approvals")

    problem_assumptions = problem_frame.get("assumptions") or []
    known_assumption_ids = {item.get("assumption_id") for item in problem_assumptions if isinstance(item, dict)}
    unknown_selection_ids = sorted(set(selections) - known_assumption_ids)
    if unknown_selection_ids:
        raise HTTPException(status_code=422, detail=f"Unknown assumption_id in approval payload: {', '.join(unknown_selection_ids)}")

    next_problem = json.loads(json.dumps(problem_frame))
    next_problem["assumptions"] = []
    for item in problem_assumptions:
        selected = selections.get(item.get("assumption_id"), {"predictive": False, "financial": False})
        next_item = dict(item)
        next_item["approved_for_predictive_processing"] = selected["predictive"]
        next_item["approved_for_financial_processing"] = selected["financial"]
        next_item["approval_state"] = "approved" if selected["predictive"] or selected["financial"] else "pending"
        next_problem["assumptions"].append(next_item)
    next_problem["status"] = "approved"
    next_problem["approval_state"] = "approved_for_system_mapping"
    next_problem["human_approval"] = approved_human_approval(role, note, now)
    next_problem["revision"] = int(next_problem.get("revision") or 1) + 1
    next_problem["updated_at"] = now

    next_system = json.loads(json.dumps(system_map))
    next_system["approved_assumptions"] = [
        {
            "assumption_id": item.get("assumption_id"),
            "source_artifact_id": next_problem.get("artifact_id"),
            "statement": item.get("statement"),
            "approved_for_predictive_processing": bool(item.get("approved_for_predictive_processing")),
            "approved_for_financial_processing": bool(item.get("approved_for_financial_processing")),
            "approval_state": item.get("approval_state", "pending"),
        }
        for item in next_problem.get("assumptions", [])
    ]
    next_system["status"] = "approved"
    next_system["human_approval"] = approved_human_approval(role, note, now)
    next_system["revision"] = int(next_system.get("revision") or 1) + 1
    next_system["updated_at"] = now

    problem_upstream = artifacts.load_upstream(run_id, "problem_frame")
    problem_errors = contracts_runtime.validate_artifact("problem_frame", next_problem, problem_upstream)
    system_upstream = dict(artifacts.load_upstream(run_id, "system_map"))
    system_upstream["problem_frame"] = next_problem
    system_errors = contracts_runtime.validate_artifact("system_map", next_system, system_upstream)
    if problem_errors or system_errors:
        return JSONResponse(
            status_code=422,
            content={
                "saved": False,
                "valid": False,
                "errors": {"problem_frame": problem_errors, "system_map": system_errors},
            },
        )

    problem_path = artifacts.save_artifact(run_id, "problem_frame", next_problem)
    system_path = artifacts.save_artifact(run_id, "system_map", next_system)
    database.upsert_run_artifact(run_id, "problem_frame", next_problem["artifact_id"], str(problem_path), next_problem.get("status", "approved"))
    database.upsert_run_artifact(run_id, "system_map", next_system["artifact_id"], str(system_path), next_system.get("status", "approved"))
    database.record_event(
        get_team_id(user),
        "assumptions_approved",
        {"approved_by_role": role, "approved_count": len(selections)},
        run_id,
    )
    return {
        "saved": True,
        "valid": True,
        "run_id": run["run_id"],
        "approved_by_role": role,
        "problem_frame": artifacts.artifact_summary(next_problem),
        "system_map": artifacts.artifact_summary(next_system),
    }


PILOT_FEEDBACK_CHOICES = {"yes", "no", "maybe"}


@app.post("/api/vertex/runs/{run_id}/pilot-feedback")
async def save_vertex_pilot_feedback(run_id: str, payload: dict = Body(...), user: dict = Depends(get_current_user)):
    """Capture pilot validation metrics 4 and 5 once a run has a DecisionRecord.

    The respondent role is recorded because "would you pay" is a founder's
    answer, not the facilitator's, even though the facilitator signs the record.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    get_current_run_or_404(run_id, user)

    if artifacts.load_artifact(run_id, "decision_record") is None:
        raise HTTPException(status_code=409, detail="Pilot feedback opens once the run has a saved DecisionRecord.")

    def choice(field: str) -> str:
        value = str(payload.get(field) or "").strip().lower()
        if value not in PILOT_FEEDBACK_CHOICES:
            raise HTTPException(status_code=422, detail=f"{field} must be one of: yes, no, maybe")
        return value

    feedback = {
        "would_pay": choice("would_pay"),
        "would_recommend": choice("would_recommend"),
        "note": str(payload.get("note") or "").strip()[:2000],
        "respondent_role": get_user_role(user),
        "captured_at": utc_now_iso(),
    }
    database.record_event(get_team_id(user), "pilot_feedback_captured", feedback, run_id)
    return {"saved": True, "feedback": feedback}


@app.get("/api/vertex/runs/{run_id}/artifacts/{artifact_type}")
async def get_vertex_run_artifact(run_id: str, artifact_type: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    get_current_run_or_404(run_id, user)
    try:
        artifact = artifacts.load_artifact(run_id, artifact_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact_response(run_id, artifact_type, artifact)

@app.get("/api/vertex/golden-case")
async def vertex_golden_case(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return build_vertex_golden_case_view_model()

@app.post("/api/billie/financial-scenario/validate")
async def validate_billie_financial_scenario(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    raise HTTPException(
        status_code=410,
        detail="Legacy Billie draft validation is disabled. Create a Golden Path run and use /api/vertex/runs/{run_id}/artifacts/financial_scenario/validate.",
    )

@app.post("/api/billie/financial-scenario/save")
async def save_billie_financial_scenario(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    raise HTTPException(
        status_code=410,
        detail="Legacy Billie draft saving is disabled. Create a Golden Path run and use /api/vertex/runs/{run_id}/artifacts/financial_scenario/save.",
    )

@app.get("/api/billie/financial-scenarios")
async def list_billie_financial_scenarios(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    team_dir = billie_team_dir(user)
    scenarios = []
    if team_dir.exists():
        for item in sorted(team_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                artifact = json.loads(item.read_text(encoding="utf-8"))
                scenarios.append(financial_scenario_summary(artifact))
            except json.JSONDecodeError:
                continue
    return {"scenarios": scenarios}

@app.get("/api/billie/financial-scenario/{artifact_id}")
async def get_billie_financial_scenario(artifact_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    safe_artifact_id = require_safe_artifact_id(artifact_id)
    target = billie_team_dir(user) / f"{safe_artifact_id}.json"
    if not target.exists():
        raise HTTPException(status_code=404, detail="FinancialScenario draft not found")
    return json.loads(target.read_text(encoding="utf-8"))

@app.get("/dashboard/facilitator", response_class=HTMLResponse)
async def facilitator_dashboard(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    metrics = build_facilitator_metrics(user)
    return templates.TemplateResponse(request, "facilitator.html", {"user": user, "metrics": metrics})


@app.get("/api/vertex/facilitator/metrics")
async def facilitator_metrics(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return build_facilitator_metrics(user)


@app.get("/dashboard/orbit", response_class=HTMLResponse)
async def orbit(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    teams = database.get_all_teams()
    return templates.TemplateResponse(request, "orbit.html", {"user": user, "teams": teams})

@app.get("/dashboard/bookings", response_class=HTMLResponse)
async def bookings(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "bookings.html", {"user": user})


def estimate_llm_tokens(payload: dict) -> int:
    return max(1, len(json.dumps(payload, sort_keys=True)) // 4)


def require_llm_budget(user: dict, module: str, payload: dict) -> tuple[str | None, int]:
    team_id = get_team_id(user)
    run_id = payload.get("run_id") or payload.get("vertex_run_id")
    if run_id:
        get_current_run_or_404(str(run_id), user)
        run_id = str(run_id)
    limit = int(os.getenv("VERTEX4D_LLM_RUN_BUDGET", "20"))
    usage = database.get_ai_usage_summary(team_id, run_id)
    if usage["calls"] >= limit:
        scope = f"run {run_id}" if run_id else "team"
        raise HTTPException(status_code=429, detail=f"LLM budget exceeded for {scope}: {usage['calls']} calls used of {limit}.")
    return run_id, estimate_llm_tokens(payload)


def record_llm_usage(user: dict, module: str, run_id: str | None, estimated_tokens: int, response_payload: dict) -> None:
    usage = response_payload.get("usage") if isinstance(response_payload, dict) else None
    total_tokens = estimated_tokens
    if isinstance(usage, dict):
        total_tokens = int(usage.get("total_tokens") or estimated_tokens)
    database.record_ai_usage(get_team_id(user), module, total_tokens, run_id)

# --- OpenAI API Proxy (Secure) ---

# API keys must come from environment variables.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ALEX_OPENAI_API_KEY = os.getenv("ALEX_OPENAI_API_KEY", "")

@app.post("/api/openai/chat")
async def openai_proxy(
    request: Request,
    payload: dict = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Secure proxy endpoint for OpenAI API calls.
    Requires user authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    run_id, estimated_tokens = require_llm_budget(user, "openai", payload)
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key is not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
            
            response_payload = response.json()
            record_llm_usage(user, "openai", run_id, estimated_tokens, response_payload)
            return response_payload
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenAI API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alex/chat")
async def alex_proxy(
    request: Request,
    payload: dict = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Secure proxy endpoint for Alex API calls using a specific key.
    Requires user authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    run_id, estimated_tokens = require_llm_budget(user, "alex", payload)
    if not ALEX_OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="Alex API key is not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {ALEX_OPENAI_API_KEY}"
                },
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
            
            response_payload = response.json()
            record_llm_usage(user, "alex", run_id, estimated_tokens, response_payload)
            return response_payload
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenAI API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    content = ""
    filename = file.filename.lower()
    
    try:
        contents = await file.read()
        file_obj = io.BytesIO(contents)
        
        if filename.endswith('.pdf'):
            reader = PdfReader(file_obj)
            for page in reader.pages:
                content += page.extract_text() + "\n"
                
        elif filename.endswith('.docx'):
            doc = Document(file_obj)
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        elif filename.endswith('.txt') or filename.endswith('.md'):
            content = contents.decode('utf-8')
            
        else:
            # Fallback for other text-based files
            try:
                content = contents.decode('utf-8')
            except:
                return JSONResponse(
                    status_code=400, 
                    content={"error": "Unsupported file type. Please upload PDF, DOCX, or TXT."}
                )
                
        return {"filename": file.filename, "content": content.strip()}
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return JSONResponse(status_code=500, content={"error": f"Error processing file: {str(e)}"})


if __name__ == "__main__":
    database.init_database()
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
