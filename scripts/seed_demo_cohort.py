"""Seed a safe institutional demo cohort for VERTEX.

The script only creates rows with explicit demo markers and the reset path only
deletes rows that still match those markers.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path

import artifacts
import contracts_runtime
import database

REPO_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_DIR / "fixtures" / "golden-case" / "v1"

DEMO_MARKER = "Demo:"
DEMO_COHORT_NAME = "Demo Cohort - Decision Quality Pilot"
DEMO_INSTITUTION_NAME = "Northstar Entrepreneurship Center"
DEMO_DOMAIN = "northstar-demo.example"
DEMO_PASSWORD = "vertex-demo-2026"
FACILITATOR_EMAIL = f"facilitator@{DEMO_DOMAIN}"
FACILITATOR_TEAM = "Demo: Northstar Facilitator"
BASE_URL = "http://127.0.0.1:8000"

ARTIFACT_TYPES = [
    "project_record",
    "problem_frame",
    "system_map",
    "predictive_hypothesis",
    "financial_scenario",
    "decision_record",
]


DEMO_CASES = [
    {
        "key": "complete",
        "team_name": "Demo: CivicCart",
        "founder_name": "Maya Ellis",
        "email": f"maya.ellis@{DEMO_DOMAIN}",
        "title": "CivicCart procurement pilot",
        "challenge": "Small public agencies want local vendor purchasing, but teams fear procurement friction and compliance risk.",
        "baseline": {
            "initial_problem_statement": "Agencies need a marketplace for local vendors.",
            "initial_customer": "municipal procurement teams",
            "initial_user": "department coordinators",
            "initial_payer": "city innovation office",
            "initial_approver": "procurement director",
            "initial_blocker": "legal/compliance review",
            "initial_stakeholders": ["procurement teams", "local vendors"],
            "initial_assumptions": ["vendors will self-onboard", "procurement can approve a light workflow"],
            "initial_evidence": ["five vendor interviews", "one procurement workshop"],
            "intuition_price": 2500,
            "intuition_price_currency": "USD",
            "main_variable_costs": ["vendor verification", "support"],
            "main_fixed_costs": ["compliance templates", "onboarding"],
            "current_decision": "test",
            "confidence_score": 6,
            "biggest_uncertainty": "whether procurement will accept a limited vendor category first",
            "next_test": "run a two-department purchasing simulation",
        },
        "problem_after": "The core problem is not vendor discovery alone; it is whether procurement teams can approve a narrow, compliant local-vendor workflow without adding review burden.",
        "stakeholders": ["procurement director", "department coordinator", "local vendors", "legal reviewer", "finance controller"],
        "price": 3200,
        "final_decision_type": "limited_pilot",
        "final_decision": "Run a limited two-department procurement pilot before expanding categories.",
        "predictive": "May support a bounded pilot if the first category has clear approval rules and no new compliance exceptions.",
        "risk": "Legal review could slow the pilot if vendor eligibility is not constrained.",
        "next_experiment": "Run a 30-day simulation with two departments and one approved vendor category.",
        "scores": [("baseline", 3), ("post", 4)],
        "feedback": {"would_pay": "yes", "would_recommend": "yes", "note": "The memo gave us a defensible next step."},
        "comments": [{"text": "Procurement category narrowed and resolved before the pilot gate.", "artifact_type": "system_map", "resolved": True}],
    },
    {
        "key": "intervention",
        "team_name": "Demo: SkillBridge Studio",
        "founder_name": "Jonah Park",
        "email": f"jonah.park@{DEMO_DOMAIN}",
        "title": "SkillBridge apprenticeship matching",
        "challenge": "Regional employers want apprentice pipelines, but readiness signals are scattered across schools and workforce partners.",
        "baseline": {
            "initial_problem_statement": "Employers need better apprentice matching.",
            "initial_customer": "mid-market employers",
            "initial_user": "workforce counselors",
            "initial_payer": "regional workforce board",
            "initial_approver": "program director",
            "initial_blocker": "school data-sharing policy",
            "initial_stakeholders": ["employers", "workforce board"],
            "initial_assumptions": ["schools can share readiness data", "employers will review candidates weekly"],
            "initial_evidence": ["two employer calls", "one counselor interview"],
            "intuition_price": 1200,
            "intuition_price_currency": "USD",
            "main_variable_costs": ["candidate support", "employer success"],
            "main_fixed_costs": ["school onboarding"],
            "current_decision": "build",
            "confidence_score": 5,
            "biggest_uncertainty": "data-sharing permission from schools",
            "next_test": "interview school administrators about consent and reporting",
        },
        "problem_after": "The first bottleneck is not matching; it is whether schools, employers and counselors can agree on a small set of readiness signals.",
        "stakeholders": ["employer hiring lead", "workforce board", "school administrator", "career counselor"],
        "price": 1500,
        "partial_artifacts": ["problem_frame", "system_map"],
        "scores": [("baseline", 2)],
        "comments": [{"text": "Clarify the school consent path before approving post-score or DecisionRecord.", "artifact_type": "problem_frame", "resolved": False}],
    },
    {
        "key": "baseline_risk",
        "team_name": "Demo: ClinicFlow",
        "founder_name": "Ari Santos",
        "email": f"ari.santos@{DEMO_DOMAIN}",
        "title": "ClinicFlow intake assistant",
        "challenge": "Community clinics want less intake admin, but the case was imported before locked baselines existed.",
        "baseline": None,
        "legacy_event": {
            "initial_problem_statement": "Clinics need faster intake.",
            "current_decision": "build",
        },
        "partial_artifacts": [],
        "comments": [{"text": "Imported legacy case. Capture a real baseline before comparing outcomes.", "artifact_type": None, "resolved": False}],
    },
    {
        "key": "economics_changed",
        "team_name": "Demo: RepairLoop",
        "founder_name": "Nadia Chen",
        "email": f"nadia.chen@{DEMO_DOMAIN}",
        "title": "RepairLoop circular parts exchange",
        "challenge": "Independent repair shops want access to refurbished parts, but logistics fees may erase margin.",
        "baseline": {
            "initial_problem_statement": "Repair shops need cheaper refurbished parts.",
            "initial_customer": "independent repair shops",
            "initial_user": "shop technicians",
            "initial_payer": "shop owners",
            "initial_approver": "operations manager",
            "initial_blocker": "parts warranty expectations",
            "initial_stakeholders": ["repair shops", "parts suppliers"],
            "initial_assumptions": ["shops will pay a subscription", "returns can be batched weekly"],
            "initial_evidence": ["three shop interviews", "supplier price sheet"],
            "intuition_price": 49,
            "intuition_price_currency": "USD",
            "main_variable_costs": ["reverse logistics", "inspection"],
            "main_fixed_costs": ["catalog setup", "supplier onboarding"],
            "current_decision": "test",
            "confidence_score": 6,
            "biggest_uncertainty": "whether margin survives return handling",
            "next_test": "model one category with real return costs",
        },
        "problem_after": "The decision depends on whether a single high-frequency parts category can absorb inspection and return handling costs.",
        "stakeholders": ["shop owner", "technician", "parts supplier", "warranty desk", "logistics partner"],
        "price": 89,
        "final_decision_type": "limited_pilot",
        "final_decision": "Pilot one parts category at USD 89 per month before adding inventory breadth.",
        "predictive": "Shops may accept a higher monthly fee if warranty replacement time falls and return rules are explicit.",
        "risk": "Reverse logistics cost could still erase contribution margin.",
        "next_experiment": "Run a four-week parts-category pilot with five shops and track replacement time plus return cost.",
        "scores": [("baseline", 2), ("post", 4)],
        "feedback": {"would_pay": "yes", "would_recommend": "maybe", "note": "The price changed after the financial scenario."},
        "comments": [],
    },
    {
        "key": "decision_changed",
        "team_name": "Demo: GreenLease",
        "founder_name": "Leah Morgan",
        "email": f"leah.morgan@{DEMO_DOMAIN}",
        "title": "GreenLease retrofit financing",
        "challenge": "Small landlords want efficiency retrofits, but incentives differ between owners, tenants and lenders.",
        "baseline": {
            "initial_problem_statement": "Landlords need simple retrofit financing.",
            "initial_customer": "small landlords",
            "initial_user": "property managers",
            "initial_payer": "landlords",
            "initial_approver": "building owner",
            "initial_blocker": "tenant disruption",
            "initial_stakeholders": ["landlords", "contractors"],
            "initial_assumptions": ["owners will build immediately", "lenders can approve fast"],
            "initial_evidence": ["two contractor calls", "one landlord survey"],
            "intuition_price": 700,
            "intuition_price_currency": "USD",
            "main_variable_costs": ["energy audit", "contractor coordination"],
            "main_fixed_costs": ["lender templates"],
            "current_decision": "build",
            "confidence_score": 7,
            "biggest_uncertainty": "who approves when tenants carry disruption",
            "next_test": "prototype owner onboarding",
        },
        "problem_after": "The immediate decision is to keep discovery focused on approval incentives before building financing workflow.",
        "stakeholders": ["landlord", "tenant", "contractor", "lender", "utility rebate administrator"],
        "price": 700,
        "final_decision_type": "continue_discovery",
        "final_decision": "Continue discovery on owner, tenant and lender approval incentives before building the workflow.",
        "predictive": "Owners may delay if tenant disruption and rebate timing are not handled before financing terms.",
        "risk": "The payer and disruption-bearer may remain misaligned.",
        "next_experiment": "Interview five landlords and five tenants with a rebate-timing storyboard.",
        "scores": [("baseline", 3), ("post", 4)],
        "feedback": {"would_pay": "maybe", "would_recommend": "yes", "note": "The process changed our build decision into a discovery decision."},
        "comments": [],
    },
]


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def demo_email(case: dict) -> str:
    return str(case["email"])


def placeholders(items: list[object]) -> str:
    return ",".join("?" for _ in items)


def get_team_id_for_email(email: str) -> int | None:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT team_id FROM team_members WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return int(row["team_id"]) if row else None


def ensure_team(team_name: str, member_name: str, email: str, role: str, challenge: str) -> int:
    existing = get_team_id_for_email(email)
    if existing is not None:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT team_name FROM teams WHERE id = ?", (existing,))
        row = cursor.fetchone()
        conn.close()
        if not row or not str(row["team_name"]).startswith(DEMO_MARKER):
            raise RuntimeError(f"Refusing to reuse non-demo team for {email}")
        return existing

    success, message, team_id = database.create_team(
        team_name,
        DEMO_PASSWORD,
        [{"name": member_name, "email": email, "role": role}],
        challenge,
        None,
    )
    if not success or team_id is None:
        raise RuntimeError(message)
    return int(team_id)


def get_demo_cohort_id() -> str | None:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cohort_id FROM cohorts WHERE cohort_name = ? AND institution_name = ?",
        (DEMO_COHORT_NAME, DEMO_INSTITUTION_NAME),
    )
    row = cursor.fetchone()
    conn.close()
    return str(row["cohort_id"]) if row else None


def assert_demo_team_ids(team_ids: list[int]) -> None:
    if not team_ids:
        return
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT teams.id, teams.team_name, team_members.email
        FROM teams
        LEFT JOIN team_members ON team_members.team_id = teams.id
        WHERE teams.id IN ({placeholders(team_ids)})
        """,
        team_ids,
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in rows:
        if not str(row.get("team_name") or "").startswith(DEMO_MARKER):
            raise RuntimeError(f"Refusing reset: team {row.get('id')} is not demo-marked")
        if not str(row.get("email") or "").endswith(f"@{DEMO_DOMAIN}"):
            raise RuntimeError(f"Refusing reset: member email {row.get('email')} is not in the demo domain")


def demo_team_ids() -> list[int]:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT teams.id
        FROM teams
        JOIN team_members ON team_members.team_id = teams.id
        WHERE teams.team_name LIKE ? AND team_members.email LIKE ?
        """,
        (f"{DEMO_MARKER}%", f"%@{DEMO_DOMAIN}"),
    )
    ids = [int(row["id"]) for row in cursor.fetchall()]
    conn.close()
    assert_demo_team_ids(ids)
    return ids


def demo_run_ids(cohort_id: str | None, team_ids: list[int]) -> list[str]:
    if not cohort_id or not team_ids:
        return []
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT run_id
        FROM runs
        WHERE cohort_id = ? AND team_id IN ({placeholders(team_ids)}) AND run_id LIKE 'run_demo_%'
        """,
        [cohort_id, *team_ids],
    )
    run_ids = [str(row["run_id"]) for row in cursor.fetchall()]
    conn.close()
    for run_id in run_ids:
        if not run_id.startswith("run_demo_"):
            raise RuntimeError(f"Refusing reset: run {run_id} is not demo-marked")
    return run_ids


def delete_artifact_dirs(run_ids: list[str]) -> int:
    removed = 0
    runtime_root = artifacts.RUNTIME_DIR.resolve()
    for run_id in run_ids:
        if not run_id.startswith("run_demo_"):
            raise RuntimeError(f"Refusing artifact delete for non-demo run {run_id}")
        target = artifacts.run_dir(run_id).resolve()
        if runtime_root not in target.parents:
            raise RuntimeError(f"Refusing artifact delete outside runtime dir: {target}")
        if target.exists():
            shutil.rmtree(target)
            removed += 1
    return removed


def reset_demo_data() -> dict:
    cohort_id = get_demo_cohort_id()
    team_ids = demo_team_ids()
    run_ids = demo_run_ids(cohort_id, team_ids)
    removed_dirs = delete_artifact_dirs(run_ids)
    counts = {"artifact_dirs": removed_dirs, "runs": len(run_ids), "teams": len(team_ids), "cohorts": 1 if cohort_id else 0}

    conn = database.get_db_connection()
    cursor = conn.cursor()
    if run_ids:
        params = run_ids
        run_clause = placeholders(run_ids)
        for table in ["decision_quality_scores", "case_comments", "run_artifacts", "ai_usage", "events", "decision_baselines"]:
            cursor.execute(f"DELETE FROM {table} WHERE run_id IN ({run_clause})", params)
        cursor.execute(f"DELETE FROM runs WHERE run_id IN ({run_clause})", params)
    if cohort_id:
        cursor.execute("DELETE FROM cohort_memberships WHERE cohort_id = ?", (cohort_id,))
        cursor.execute("DELETE FROM cohorts WHERE cohort_id = ? AND cohort_name = ? AND institution_name = ?", (cohort_id, DEMO_COHORT_NAME, DEMO_INSTITUTION_NAME))
    if team_ids:
        team_clause = placeholders(team_ids)
        cursor.execute(f"DELETE FROM ai_usage WHERE team_id IN ({team_clause})", team_ids)
        cursor.execute(f"DELETE FROM events WHERE team_id IN ({team_clause})", team_ids)
        cursor.execute(f"DELETE FROM team_members WHERE team_id IN ({team_clause}) AND email LIKE ?", [*team_ids, f"%@{DEMO_DOMAIN}"])
        cursor.execute(f"DELETE FROM teams WHERE id IN ({team_clause}) AND team_name LIKE ?", [*team_ids, f"{DEMO_MARKER}%"])
    conn.commit()
    conn.close()
    return counts


def create_demo_cohort(owner_team_id: int) -> dict:
    cohort = database.create_cohort(
        {
            "cohort_name": DEMO_COHORT_NAME,
            "institution_name": DEMO_INSTITUTION_NAME,
            "start_date": "2026-09-14",
            "end_date": "2026-10-23",
            "status": "active",
        },
        owner_team_id,
        FACILITATOR_EMAIL,
    )
    database.add_cohort_member(cohort["cohort_id"], owner_team_id)
    return cohort


def update_common_artifact(artifact: dict, run_id: str, project: dict, case: dict, artifact_type: str) -> dict:
    safe_run = run_id.replace("-", "_")
    now = "2026-09-15T09:00:00Z"
    artifact = copy.deepcopy(artifact)
    artifact["artifact_id"] = f"{artifact_type}_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["created_at"] = now
    artifact["updated_at"] = now
    artifact["status"] = "approved"
    artifact["provenance"]["source_kind"] = "synthetic_fixture"
    artifact["provenance"]["source_label"] = f"VERTEX institutional demo - {case['title']}"
    artifact["provenance"]["notes"] = "Synthetic demo data for institutional walkthrough only."
    if "human_approval" in artifact:
        artifact["human_approval"]["state"] = "approved"
        artifact["human_approval"]["approved_by_role"] = "facilitator"
        artifact["human_approval"]["approved_at"] = now
        artifact["human_approval"]["notes"] = "Approved for demo traceability."
    return artifact


def build_problem_frame(run_id: str, project: dict, case: dict) -> dict:
    artifact = update_common_artifact(load_fixture("problem-frame"), run_id, project, case, "problem_frame")
    artifact["preceding_artifacts"]["project_record_id"] = project["artifact_id"]
    artifact["original_challenge"] = case["challenge"]
    artifact["reframed_problem"]["statement"] = case["problem_after"]
    artifact["affected_users"][0]["label"] = case["baseline"]["initial_user"]
    artifact["affected_users"][1]["label"] = case["baseline"]["initial_customer"]
    return artifact


def build_system_map(run_id: str, project: dict, problem: dict, case: dict) -> dict:
    artifact = update_common_artifact(load_fixture("system-map"), run_id, project, case, "system_map")
    artifact["preceding_artifacts"]["project_record_id"] = project["artifact_id"]
    artifact["preceding_artifacts"]["problem_frame_id"] = problem["artifact_id"]
    for item, label in zip(artifact["stakeholders"], case["stakeholders"]):
        item["label"] = label
    for item in artifact["approved_assumptions"]:
        item["source_artifact_id"] = problem["artifact_id"]
    return artifact


def build_predictive_hypothesis(run_id: str, project: dict, problem: dict, system: dict, case: dict) -> dict:
    artifact = update_common_artifact(load_fixture("predictive-hypothesis"), run_id, project, case, "predictive_hypothesis")
    artifact["preceding_artifacts"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
    }
    artifact["approved_input_references"]["system_map_id"] = system["artifact_id"]
    artifact["scenario_question"] = f"What support or resistance could affect {case['title']}?"
    artifact["simulated_stakeholder_responses"][0]["simulated_response"] = case["predictive"]
    for item in artifact["assumptions_used"]:
        item["source_artifact_id"] = system["artifact_id"]
    artifact["run_metadata"]["run_id"] = run_id
    artifact["run_metadata"]["is_fixture"] = False
    return artifact


def build_financial_scenario(run_id: str, project: dict, problem: dict, system: dict, case: dict) -> dict:
    artifact = update_common_artifact(load_fixture("financial-scenario"), run_id, project, case, "financial_scenario")
    artifact["preceding_artifacts"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
    }
    artifact["currency"] = case["baseline"]["intuition_price_currency"]
    artifact["scenario_name"] = f"{case['title']} bounded pilot"
    artifact["pricing_assumptions"][0]["value"] = case["price"]
    artifact["pricing_assumptions"][0]["unit"] = f"{artifact['currency']} pilot price"
    artifact["revenue_projection"]["unit"] = artifact["currency"]
    artifact["cost_projection"]["unit"] = artifact["currency"]
    artifact["cash_requirement"]["unit"] = artifact["currency"]
    return artifact


def build_decision_record(run_id: str, project: dict, problem: dict, system: dict, predictive: dict, financial: dict, case: dict) -> dict:
    artifact = update_common_artifact(load_fixture("decision-record"), run_id, project, case, "decision_record")
    artifact["linked_upstream_artifact_ids"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
        "predictive_hypothesis_id": predictive["artifact_id"],
        "financial_scenario_id": financial["artifact_id"],
    }
    artifact["decision_question"] = f"What should {case['team_name'].replace(DEMO_MARKER, '').strip()} do next?"
    artifact["selected_decision"]["decision_id"] = f"dec_{case['key']}"
    artifact["selected_decision"]["statement"] = case["final_decision"]
    artifact["selected_decision"]["decision_type"] = case["final_decision_type"]
    artifact["rationale"] = f"The final decision follows the reframed problem, stakeholder system and financial scenario for {case['title']}."
    artifact["evidence_summary"][0]["source_artifact_id"] = problem["artifact_id"]
    artifact["evidence_summary"][0]["summary"] = f"Problem framing narrowed the decision for {case['title']}."
    artifact["evidence_summary"][1]["source_artifact_id"] = system["artifact_id"]
    artifact["evidence_summary"][1]["summary"] = "Stakeholder mapping surfaced approval, blocker and operating roles."
    artifact["predictive_hypotheses"][0]["hypothesis_id"] = predictive["artifact_id"]
    artifact["predictive_hypotheses"][0]["summary"] = case["predictive"]
    artifact["financial_scenarios"][0]["financial_scenario_id"] = financial["artifact_id"]
    artifact["financial_scenarios"][0]["summary"] = f"Financial scenario changed or confirmed the price at {financial['currency']} {case['price']}."
    artifact["risks"][0]["statement"] = case["risk"]
    artifact["risks"][0]["source_refs"] = [predictive["artifact_id"]]
    artifact["next_experiment"]["statement"] = case["next_experiment"]
    artifact["facilitator_approval"]["state"] = "approved"
    artifact["facilitator_approval"]["approved_by_role"] = "facilitator"
    artifact["facilitator_approval"]["approved_at"] = "2026-09-15T10:00:00Z"
    artifact["facilitator_approval"]["notes"] = "Approved for institutional demo."
    artifact["audit_trail"][0]["artifact_refs"] = [project["artifact_id"], problem["artifact_id"], system["artifact_id"], predictive["artifact_id"], financial["artifact_id"]]
    artifact["audit_trail"][1]["artifact_refs"] = [artifact["artifact_id"]]
    return artifact


def validate_and_save(run_id: str, artifact_type: str, artifact: dict) -> None:
    errors = contracts_runtime.validate_artifact(artifact_type, artifact, artifacts.load_upstream(run_id, artifact_type))
    if errors:
        raise RuntimeError(f"{artifact_type} validation failed for {run_id}: {errors}")
    path = artifacts.save_artifact(run_id, artifact_type, artifact)
    database.upsert_run_artifact(run_id, artifact_type, artifact["artifact_id"], str(path), artifact.get("status", "approved"))


def create_run_for_case(case: dict, team_id: int, cohort_id: str) -> str:
    run_id = f"run_demo_{case['key']}"
    run = database.create_run(run_id, team_id, case["title"], mode="cohort", cohort_id=cohort_id)
    project = artifacts.build_project_record(
        run_id,
        {"team_name": case["team_name"], "challenge_desc": case["challenge"]},
        case["title"],
        {"challenge_statement": case["challenge"], "is_synthetic": True, "approved_for_predictive_processing": True},
    )
    validate_and_save(run_id, "project_record", project)

    if case.get("baseline"):
        baseline = database.lock_decision_baseline(run_id, team_id, case["baseline"])
        database.record_event(team_id, "metric_baseline_captured", baseline, run_id)
        database.record_event(team_id, "baseline_locked", {"locked_at": baseline["locked_at"]}, run_id)
    elif case.get("legacy_event"):
        database.record_event(team_id, "metric_baseline_captured", case["legacy_event"], run_id)

    if "problem_frame" in case.get("partial_artifacts", ARTIFACT_TYPES) or case.get("final_decision"):
        problem = build_problem_frame(run_id, project, case)
        validate_and_save(run_id, "problem_frame", problem)
    else:
        problem = None
    if problem and ("system_map" in case.get("partial_artifacts", ARTIFACT_TYPES) or case.get("final_decision")):
        system = build_system_map(run_id, project, problem, case)
        validate_and_save(run_id, "system_map", system)
    else:
        system = None
    if case.get("final_decision") and system:
        predictive = build_predictive_hypothesis(run_id, project, problem, system, case)
        validate_and_save(run_id, "predictive_hypothesis", predictive)
        financial = build_financial_scenario(run_id, project, problem, system, case)
        validate_and_save(run_id, "financial_scenario", financial)
        decision = build_decision_record(run_id, project, problem, system, predictive, financial, case)
        validate_and_save(run_id, "decision_record", decision)
        database.mark_run_completed(run_id)

    for stage, base in case.get("scores", []):
        database.add_decision_quality_score(
            run_id,
            FACILITATOR_EMAIL,
            stage,
            {
                "framing": base,
                "system_awareness": base,
                "evidence_quality": base,
                "behavioral_logic": base,
                "economic_coherence": base,
                "decision_action": base,
            },
            f"Demo {stage} rubric score for {case['title']}.",
        )
    for comment in case.get("comments", []):
        saved = database.add_case_comment(run_id, team_id, FACILITATOR_EMAIL, "facilitator", comment.get("artifact_type"), comment["text"])
        if comment.get("resolved"):
            database.resolve_case_comment(run_id, saved["id"])
    if case.get("feedback"):
        database.record_event(team_id, "pilot_feedback_captured", {**case["feedback"], "respondent_role": "founder"}, run_id)
    database.record_ai_usage(team_id, "demo_seed", 1200, run_id)
    database.record_event(team_id, "demo_case_seeded", {"demo": True, "case_key": case["key"], "cohort_id": cohort_id}, run_id)
    return run["run_id"]


def seed_demo_cohort(reset_existing: bool = True) -> dict:
    if reset_existing:
        existing = get_demo_cohort_id()
        existing_teams = demo_team_ids()
        if existing or existing_teams:
            counts = reset_demo_data()
            print(f"Existing demo data removed before reseed: {counts}")

    facilitator_team_id = ensure_team(FACILITATOR_TEAM, "Renee Alvarez", FACILITATOR_EMAIL, "facilitator", "Northstar demo facilitator workspace")
    cohort = create_demo_cohort(facilitator_team_id)
    run_ids = []
    founders = []
    for case in DEMO_CASES:
        team_id = ensure_team(case["team_name"], case["founder_name"], demo_email(case), "founder", case["challenge"])
        database.add_cohort_member(cohort["cohort_id"], team_id)
        run_ids.append(create_run_for_case(case, team_id, cohort["cohort_id"]))
        founders.append({"team": case["team_name"], "email": demo_email(case), "password": DEMO_PASSWORD})

    result = {
        "cohort_id": cohort["cohort_id"],
        "cohort_name": DEMO_COHORT_NAME,
        "institution_name": DEMO_INSTITUTION_NAME,
        "facilitator": {"email": FACILITATOR_EMAIL, "password": DEMO_PASSWORD},
        "founders": founders,
        "run_ids": run_ids,
        "urls": {
            "facilitator_dashboard": f"{BASE_URL}/dashboard/facilitator",
            "cohort": f"{BASE_URL}/dashboard/facilitator/cohorts/{cohort['cohort_id']}",
            "outcome_report": f"{BASE_URL}/dashboard/facilitator/cohorts/{cohort['cohort_id']}/outcome-report",
            "decision_memo_complete": f"{BASE_URL}/dashboard/lab/decision-memo?run_id=run_demo_complete",
            "decision_memo_economics": f"{BASE_URL}/dashboard/lab/decision-memo?run_id=run_demo_economics_changed",
        },
    }
    return result


def print_handoff(result: dict) -> None:
    print("VERTEX institutional demo cohort seeded.")
    print(f"Cohort: {result['cohort_name']} ({result['cohort_id']})")
    print(f"Institution: {result['institution_name']}")
    print(f"Facilitator login: {result['facilitator']['email']} / {result['facilitator']['password']}")
    print("Founder logins:")
    for founder in result["founders"]:
        print(f"  - {founder['team']}: {founder['email']} / {founder['password']}")
    print("Run IDs:")
    for run_id in result["run_ids"]:
        print(f"  - {run_id}")
    print("Key URLs:")
    for label, url in result["urls"].items():
        print(f"  - {label}: {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed or reset the VERTEX institutional demo cohort.")
    parser.add_argument("--reset-demo", action="store_true", help="Delete only demo-marked cohort data and exit.")
    parser.add_argument("--json", action="store_true", help="Print a JSON summary after seeding.")
    args = parser.parse_args()

    if args.reset_demo:
        counts = reset_demo_data()
        print(f"Demo reset complete: {counts}")
        return

    result = seed_demo_cohort(reset_existing=True)
    print_handoff(result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
