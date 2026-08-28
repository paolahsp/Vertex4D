"""Smoke test the VERTEX institutional demo cohort seed/reset workflow."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]


def assert_ok(response, label: str):
    assert response.status_code == 200, f"{label} failed: {response.status_code} {response.text}"
    return response.json() if "application/json" in response.headers.get("content-type", "") else response.text


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        os.environ["VERTEX4D_DATABASE_PATH"] = str(tmp_path / "vertex4d-demo-smoke.db")
        os.environ["VERTEX4D_RUNTIME_DIR"] = str(tmp_path / "runs")
        os.chdir(REPO_DIR)
        sys.path.insert(0, str(REPO_DIR))

        from fastapi.testclient import TestClient

        import database
        import main as app_main
        from scripts import seed_demo_cohort

        result = seed_demo_cohort.seed_demo_cohort(reset_existing=True)
        success, message, control_team_id = database.create_team(
            "Smoke Control Team",
            "keep-me",
            [{"name": "Control Founder", "email": "control-smoke@example.com", "role": "founder"}],
            "Non-demo row used to verify reset safety.",
            None,
        )
        assert success and control_team_id, message

        facilitator_user = database.verify_login(
            seed_demo_cohort.FACILITATOR_EMAIL,
            seed_demo_cohort.DEMO_PASSWORD,
        )[2]
        assert facilitator_user and facilitator_user["role"] == "facilitator", facilitator_user

        client = TestClient(app_main.app)
        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: facilitator_user

        assert client.get("/dashboard/facilitator").status_code == 200, "facilitator dashboard should render"
        assert client.get(f"/dashboard/facilitator/cohorts/{result['cohort_id']}").status_code == 200, "cohort page should render"
        assert client.get(f"/dashboard/facilitator/cohorts/{result['cohort_id']}/outcome-report").status_code == 200, "outcome report page should render"
        assert client.get("/dashboard/lab/decision-memo?run_id=run_demo_complete").status_code == 200, "decision memo should render"

        report = assert_ok(client.get(f"/api/vertex/cohorts/{result['cohort_id']}/outcome-report"), "outcome report")
        cases = report["cases"]
        assert len(cases) >= 5, report
        assert report["totals"]["cases"] >= 5, report["totals"]
        assert any(case["needs_intervention"] for case in cases), cases
        assert any(case["completed"] for case in cases), cases
        assert any(case["open_comments"] > 0 for case in cases), cases
        assert any(case["quality_scores"]["delta"] is not None for case in cases), cases
        assert any(case["run_id"] == "run_demo_economics_changed" and case["price_changed"] is True for case in cases), cases
        assert any(case["run_id"] == "run_demo_decision_changed" and case["decision_changed"] is True for case in cases), cases

        management = app_main.compose_cohort_management(result["cohort_id"], facilitator_user)
        intervention = next(case for case in management["cases"] if case["run_id"] == "run_demo_intervention")
        assert "open facilitator comments" in intervention["intervention_reasons"], intervention
        assert "post score missing" in intervention["intervention_reasons"], intervention
        baseline_risk = next(case for case in management["cases"] if case["run_id"] == "run_demo_baseline_risk")
        assert "baseline not locked" in baseline_risk["intervention_reasons"], baseline_risk

        memo = assert_ok(client.get("/api/vertex/runs/run_demo_economics_changed/decision-memo"), "economics memo")
        assert "49" in memo["pricing_financial_insight"] and "89" in memo["pricing_financial_insight"], memo

        reset_counts = seed_demo_cohort.reset_demo_data()
        assert reset_counts["runs"] == 5, reset_counts
        assert database.get_cohort(result["cohort_id"]) is None, "demo cohort should be removed"
        assert database.get_run_any("run_demo_complete") is None, "demo run should be removed"
        assert database.verify_login("control-smoke@example.com", "keep-me")[0] is True, "non-demo control team should remain"

        print(
            "DEMO COHORT SMOKE PASS: "
            f"{result['cohort_id']} seeded with {len(cases)} cases; "
            f"reset removed {reset_counts['runs']} demo runs and preserved control team {control_team_id}"
        )


if __name__ == "__main__":
    main()
