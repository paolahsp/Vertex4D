"""End-to-end smoke test for the reduced VERTEX Golden Path.

Creates an isolated temporary database/runtime, builds the active artifact chain,
verifies a founder cannot sign the final DecisionRecord, then verifies a
facilitator created through the real team-member role mechanism can validate
and save it.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_DIR / "fixtures" / "golden-case" / "v1"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def assert_ok(response, label: str) -> dict:
    assert response.status_code == 200, f"{label} failed: {response.status_code} {response.text}"
    return response.json()


def save_artifact(client, run_id: str, artifact_type: str, artifact: dict) -> dict:
    return assert_ok(
        client.post(f"/api/vertex/runs/{run_id}/artifacts/{artifact_type}/save", json=artifact),
        f"save {artifact_type}",
    )


def build_problem_frame(run_id: str, project: dict) -> dict:
    safe_run = run_id.replace("-", "_")
    artifact = load_fixture("problem-frame")
    artifact["artifact_id"] = f"problem_frame_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["preceding_artifacts"]["project_record_id"] = project["artifact_id"]
    artifact["created_at"] = "2026-08-19T00:00:00Z"
    artifact["updated_at"] = "2026-08-19T00:00:00Z"
    return artifact


def build_system_map(run_id: str, project: dict, problem: dict) -> dict:
    safe_run = run_id.replace("-", "_")
    artifact = load_fixture("system-map")
    artifact["artifact_id"] = f"system_map_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["preceding_artifacts"]["project_record_id"] = project["artifact_id"]
    artifact["preceding_artifacts"]["problem_frame_id"] = problem["artifact_id"]
    artifact["created_at"] = "2026-08-19T00:00:00Z"
    artifact["updated_at"] = "2026-08-19T00:00:00Z"
    for item in artifact["approved_assumptions"]:
        item["source_artifact_id"] = problem["artifact_id"]
    return artifact


def build_predictive_hypothesis(run_id: str, project: dict, problem: dict, system: dict) -> dict:
    safe_run = run_id.replace("-", "_")
    artifact = load_fixture("predictive-hypothesis")
    artifact["artifact_id"] = f"predictive_hypothesis_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["status"] = "pending_review"
    artifact["created_at"] = "2026-08-19T00:00:00Z"
    artifact["updated_at"] = "2026-08-19T00:00:00Z"
    artifact["provenance"]["source_kind"] = "system_generated"
    artifact["provenance"]["source_label"] = "D-Predict reduced deterministic smoke"
    artifact["provenance"]["notes"] = "Smoke artifact generated without external API calls."
    artifact["human_approval"] = {
        "required": True,
        "state": "pending",
        "approved_by_role": "founder",
        "approved_at": "2026-08-19T00:00:00Z",
        "notes": "Pending facilitator review.",
    }
    artifact["preceding_artifacts"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
    }
    artifact["approved_input_references"]["system_map_id"] = system["artifact_id"]
    for item in artifact["assumptions_used"]:
        item["source_artifact_id"] = system["artifact_id"]
    artifact["run_metadata"] = {
        "run_id": run_id,
        "engine_name": "d_predict_reduced_deterministic",
        "engine_version": "0.1.0",
        "is_fixture": False,
        "external_api_calls_made": False,
        "scenario_count": 1,
        "time_horizon": "next pilot decision window",
    }
    return artifact


def build_financial_scenario(run_id: str, project: dict, problem: dict, system: dict) -> dict:
    safe_run = run_id.replace("-", "_")
    artifact = load_fixture("financial-scenario")
    artifact["artifact_id"] = f"financial_scenario_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["status"] = "pending_review"
    artifact["created_at"] = "2026-08-19T00:00:00Z"
    artifact["updated_at"] = "2026-08-19T00:00:00Z"
    artifact["human_approval"] = {
        "required": True,
        "state": "pending",
        "approved_by_role": "founder",
        "approved_at": "2026-08-19T00:00:00Z",
        "notes": "Pending financial review.",
    }
    artifact["preceding_artifacts"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
    }
    return artifact


def build_decision_record(run_id: str, project: dict, problem: dict, system: dict, predictive: dict, financial: dict) -> dict:
    safe_run = run_id.replace("-", "_")
    artifact = load_fixture("decision-record")
    artifact["artifact_id"] = f"decision_record_{safe_run}"
    artifact["project_id"] = project["project_id"]
    artifact["created_at"] = "2026-08-19T00:00:00Z"
    artifact["updated_at"] = "2026-08-19T00:00:00Z"
    artifact["linked_upstream_artifact_ids"] = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
        "predictive_hypothesis_id": predictive["artifact_id"],
        "financial_scenario_id": financial["artifact_id"],
    }
    artifact["predictive_hypotheses"][0]["hypothesis_id"] = predictive["artifact_id"]
    artifact["financial_scenarios"][0]["financial_scenario_id"] = financial["artifact_id"]
    artifact["risks"][0]["source_refs"] = [predictive["artifact_id"]]
    artifact["audit_trail"][0]["artifact_refs"] = [
        project["artifact_id"],
        problem["artifact_id"],
        system["artifact_id"],
        predictive["artifact_id"],
        financial["artifact_id"],
    ]
    artifact["audit_trail"][1]["artifact_refs"] = [artifact["artifact_id"]]
    artifact["human_approval"] = {
        "required": True,
        "state": "approved",
        "approved_by_role": "facilitator",
        "approved_at": "2026-08-19T00:00:00Z",
        "notes": "Smoke final approval.",
    }
    artifact["facilitator_approval"] = {
        "state": "approved",
        "approved_by_role": "facilitator",
        "approved_at": "2026-08-19T00:00:00Z",
        "notes": "Smoke final approval.",
    }
    return artifact


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        os.environ["VERTEX4D_DATABASE_PATH"] = str(tmp_path / "vertex4d-smoke.db")
        os.environ["VERTEX4D_RUNTIME_DIR"] = str(tmp_path / "runs")
        os.chdir(REPO_DIR)
        sys.path.insert(0, str(REPO_DIR))

        from fastapi.testclient import TestClient
        import main as app_main

        client = TestClient(app_main.app)
        team_name = "Smoke Team Golden Path"
        founder_email = "founder-smoke@example.com"
        facilitator_email = "facilitator-smoke@example.com"
        password = "smoke-password"

        # The facilitator role must survive the real program-authorization gate,
        # not be handed to the test directly. An unauthorized request is refused.
        requested_members = [
            {"name": "Founder Smoke", "email": founder_email, "role": "founder"},
            {"name": "Facilitator Smoke", "email": facilitator_email, "role": "facilitator"},
        ]
        os.environ.pop("VERTEX4D_FACILITATOR_EMAILS", None)
        os.environ.pop("VERTEX4D_FACILITATOR_INVITE_CODE", None)
        unauthorized, unauthorized_error = app_main.authorize_member_roles(requested_members, "")
        assert not unauthorized and unauthorized_error, "facilitator must be refused with no program control configured"
        print(f"OK    facilitator refused without program control: {unauthorized_error}")

        os.environ["VERTEX4D_FACILITATOR_EMAILS"] = facilitator_email
        impostor, impostor_error = app_main.authorize_member_roles(
            [{"name": "Impostor", "email": "impostor-smoke@example.com", "role": "facilitator"}], ""
        )
        assert not impostor and impostor_error, "off-allowlist email must be refused the facilitator role"
        print(f"OK    off-allowlist facilitator refused: {impostor_error}")

        members, role_error = app_main.authorize_member_roles(requested_members, "")
        assert role_error is None, role_error
        assert [item["role"] for item in members] == ["founder", "facilitator"], members

        success, message, team_id = app_main.database.create_team(
            team_name,
            password,
            members,
            "Smoke final decision venture",
            None,
        )
        assert success, message
        founder_user = app_main.database.verify_login(founder_email, password)[2]
        facilitator_user = app_main.database.verify_login(facilitator_email, password)[2]
        assert founder_user["role"] == "founder", founder_user
        assert facilitator_user["role"] == "facilitator", facilitator_user
        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: founder_user

        created = assert_ok(
            client.post(
                "/api/vertex/runs",
                json={
                    "title": "Golden Path smoke",
                    "challenge_statement": "A pilot needs a traceable final decision.",
                    "is_synthetic": True,
                },
            ),
            "create run",
        )
        run_id = created["run"]["run_id"]
        project = assert_ok(client.get(f"/api/vertex/runs/{run_id}/artifacts/project_record"), "load project")["artifact"]

        problem = build_problem_frame(run_id, project)
        save_artifact(client, run_id, "problem_frame", problem)
        system = build_system_map(run_id, project, problem)
        save_artifact(client, run_id, "system_map", system)
        predictive = build_predictive_hypothesis(run_id, project, problem, system)
        save_artifact(client, run_id, "predictive_hypothesis", predictive)
        financial = build_financial_scenario(run_id, project, problem, system)
        save_artifact(client, run_id, "financial_scenario", financial)
        decision = build_decision_record(run_id, project, problem, system, predictive, financial)

        founder_validation = assert_ok(
            client.post(f"/api/vertex/runs/{run_id}/artifacts/decision_record/validate", json=decision),
            "founder decision validation",
        )
        assert founder_validation["valid"] is False, "founder unexpectedly validated final DecisionRecord"
        assert any("facilitator approval" in err["message"] for err in founder_validation["errors"]), founder_validation

        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: facilitator_user
        facilitator_validation = assert_ok(
            client.post(f"/api/vertex/runs/{run_id}/artifacts/decision_record/validate", json=decision),
            "facilitator decision validation",
        )
        assert facilitator_validation["valid"] is True, facilitator_validation
        save_artifact(client, run_id, "decision_record", decision)
        loaded = assert_ok(client.get(f"/api/vertex/runs/{run_id}/artifacts/decision_record"), "load decision")["artifact"]
        assert loaded["facilitator_approval"]["approved_by_role"] == "facilitator"
        assert loaded["predictive_hypotheses"][0]["not_evidence"] is True
        print(f"GOLDEN PATH SMOKE PASS: {run_id} -> {loaded['artifact_id']} ({loaded['selected_decision']['decision_type']})")


if __name__ == "__main__":
    main()
