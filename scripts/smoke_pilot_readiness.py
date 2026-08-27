"""Smoke test print/export routes and pilot readiness documents."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
DOCS = [
    "docs/PILOT_OPERATOR_CHECKLIST.md",
    "docs/PRIVACY_DATA_HANDLING.md",
    "docs/PAID_PILOT_PROPOSAL_ONE_PAGER.md",
    "docs/BUYER_FOLLOW_UP_EMAIL.md",
    "docs/FOUNDER_ONBOARDING_SCRIPT.md",
    "docs/FACILITATOR_RUN_OF_SHOW.md",
    "docs/VERTEX_ACCELERATOR_EDUCATIONAL_DEMO.md",
]


def assert_200(response, label: str) -> str:
    assert response.status_code == 200, f"{label} failed: {response.status_code} {response.text}"
    return response.text


def assert_contains(text: str, needle: str, label: str) -> None:
    assert needle.lower() in text.lower(), f"{label} missing expected text: {needle}"


def assert_not_contains(text: str, needle: str, label: str) -> None:
    assert needle.lower() not in text.lower(), f"{label} should not contain: {needle}"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        os.environ["VERTEX4D_DATABASE_PATH"] = str(tmp_path / "vertex4d-pilot-readiness.db")
        os.environ["VERTEX4D_RUNTIME_DIR"] = str(tmp_path / "runs")
        os.chdir(REPO_DIR)
        sys.path.insert(0, str(REPO_DIR))

        from fastapi.testclient import TestClient

        import database
        import main as app_main
        from scripts import seed_demo_cohort

        seeded = seed_demo_cohort.seed_demo_cohort(reset_existing=True)
        facilitator = database.verify_login(seed_demo_cohort.FACILITATOR_EMAIL, seed_demo_cohort.DEMO_PASSWORD)[2]
        founder = database.verify_login("maya.ellis@northstar-demo.example", seed_demo_cohort.DEMO_PASSWORD)[2]
        assert facilitator and facilitator["role"] == "facilitator", facilitator
        assert founder and founder["role"] == "founder", founder

        client = TestClient(app_main.app)

        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: facilitator
        facilitator_login = client.post(
            "/login",
            data={
                "email": seed_demo_cohort.FACILITATOR_EMAIL,
                "password": seed_demo_cohort.DEMO_PASSWORD,
            },
            follow_redirects=False,
        )
        assert facilitator_login.status_code == 303, facilitator_login.text
        assert client.get("/dashboard/facilitator").status_code == 200, "facilitator dashboard should still render"
        assert client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/outcome-report").status_code == 200, "report should still render"

        demo_entry = client.get("/dashboard/facilitator/accelerator-demo", follow_redirects=False)
        assert demo_entry.status_code == 303, demo_entry.text
        assert seeded["cohort_id"] in demo_entry.headers.get("location", ""), demo_entry.headers
        demo_page = assert_200(
            client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/accelerator-demo"),
            "accelerator demo mode",
        )
        assert_contains(demo_page, "Accelerator Demo Mode", "accelerator demo mode")
        assert_contains(demo_page, "Intervention Radar", "accelerator demo mode")
        assert_contains(demo_page, "run_demo_economics_changed", "accelerator demo mode")
        assert_contains(demo_page, "run_demo_decision_changed", "accelerator demo mode")
        assert_contains(demo_page, "Brief", "accelerator demo mode")
        assert_contains(demo_page, "Outcome Report", "accelerator demo mode")

        route_checks = [
            ("/dashboard/vertex/spark", "Spark"),
            ("/dashboard/vertex/riddle", "Riddle"),
            ("/dashboard/vertex/tangle", "Tangle"),
            ("/dashboard/vertex/gatekeeper", "Gatekeeper"),
            ("/dashboard/vertex/ripple", "Ripple"),
            ("/dashboard/vertex/ledger", "Ledger"),
            ("/dashboard/vertex/stamp", "Stamp"),
            ("/dashboard/vertex/brief?run_id=run_demo_complete", "Brief"),
            ("/dashboard/vertex/brief/print?run_id=run_demo_complete", "Brief"),
            ("/dashboard/vertex/quest", "Quest"),
            ("/dashboard/lab", "Srsly Labs Lab"),
            ("/dashboard/lab/alex", "Alex"),
            ("/dashboard/lab/synapmap", "SynapMap"),
            ("/dashboard/lab/d-predict", "D-Predict / MiroFish"),
            ("/dashboard/lab/billie", "Billie"),
            ("/dashboard/lab/finops", "FinOps Central"),
            ("/dashboard/orbit", "The Orbit"),
            ("/dashboard/lab/start-golden-path", "Spark"),
            ("/dashboard/lab/assumption-approval", "Gatekeeper"),
            ("/dashboard/lab/decision-record", "Stamp"),
            ("/dashboard/lab/decision-memo?run_id=run_demo_complete", "Brief"),
            ("/dashboard/lab/decision-memo/print?run_id=run_demo_complete", "Brief"),
            ("/dashboard/lab/golden-path", "Quest"),
        ]
        for path, expected in route_checks:
            assert_contains(assert_200(client.get(path), path), expected, path)

        alex_lab = assert_200(client.get("/dashboard/lab/alex"), "lab alex")
        assert_contains(alex_lab, "/api/alex/chat", "lab alex")
        assert_contains(alex_lab, "download-pdf-btn", "lab alex")
        assert_contains(alex_lab, "Socratic chat", "lab alex")

        synapmap_lab = assert_200(client.get("/dashboard/lab/synapmap"), "lab synapmap")
        assert_contains(synapmap_lab, "d3.forceSimulation", "lab synapmap")
        assert_contains(synapmap_lab, "/api/process-file", "lab synapmap")
        assert_contains(synapmap_lab, "RACI Matrix", "lab synapmap")
        assert_contains(synapmap_lab, "system-map-svg", "lab synapmap")
        for forbidden in ["Tangle", "Gatekeeper", "Student direction and deliverable", "Next action"]:
            assert_not_contains(synapmap_lab, forbidden, "lab synapmap")

        tangle_vertex = assert_200(client.get("/dashboard/vertex/tangle"), "vertex tangle")
        assert_contains(tangle_vertex, "Tangle", "vertex tangle")
        assert_contains(tangle_vertex, "SystemMap", "vertex tangle")
        assert_contains(tangle_vertex, "Student direction and deliverable", "vertex tangle")
        assert_contains(tangle_vertex, "artifacts/system_map/save", "vertex tangle")

        billie_lab = assert_200(client.get("/dashboard/lab/billie"), "lab billie")
        assert_contains(billie_lab, "Billie Storyteller", "lab billie")
        assert_contains(billie_lab, "Positioning Statement", "lab billie")
        assert_contains(billie_lab, "Safe Claims", "lab billie")
        assert_not_contains(billie_lab, "FinancialScenario", "lab billie")
        assert_not_contains(billie_lab, "pricing calculator", "lab billie")

        dpredict_lab = assert_200(client.get("/dashboard/lab/d-predict"), "lab d-predict")
        assert_contains(dpredict_lab, "D-Predict / MiroFish", "lab d-predict")
        assert_contains(dpredict_lab, "Scenario Stress Test", "lab d-predict")
        assert_contains(dpredict_lab, "Readings, not forecasts", "lab d-predict")
        assert_contains(dpredict_lab, "not a factual prediction", "lab d-predict")
        assert_not_contains(dpredict_lab, "PredictiveHypothesis", "lab d-predict")
        assert_not_contains(dpredict_lab, "Student direction and deliverable", "lab d-predict")

        ledger_vertex = assert_200(client.get("/dashboard/vertex/ledger"), "vertex ledger")
        assert_contains(ledger_vertex, "Ledger", "vertex ledger")
        assert_contains(ledger_vertex, "FinancialScenario", "vertex ledger")

        orbit_lab = assert_200(client.get("/dashboard/orbit"), "lab orbit")
        for marker in ["The Orbit", "Evidence Orbit", "Signal", "Confidence", "Shared Evidence", "local draft", "orbit_evidence_current"]:
            assert_contains(orbit_lab, marker, "lab orbit")
        for forbidden in ["automatic matching", "real-time monitoring", "external signal feed"]:
            assert_not_contains(orbit_lab, forbidden, "lab orbit")

        memo_print = assert_200(
            client.get("/dashboard/lab/decision-memo/print?run_id=run_demo_complete"),
            "decision memo print",
        )
        assert_contains(memo_print, "does not predict startup success", "decision memo print")
        assert_contains(memo_print, "run_demo_complete", "decision memo print")
        assert_contains(memo_print, "project_record_run_demo_complete", "decision memo print")

        report_print = assert_200(
            client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/outcome-report/print"),
            "cohort report print",
        )
        assert_contains(report_print, "does not predict startup success", "cohort report print")
        assert_contains(report_print, seeded["cohort_id"], "cohort report print")
        assert_contains(report_print, "run_demo_baseline_risk", "cohort report print")
        assert_contains(report_print, "missing", "cohort report print")
        assert_contains(report_print, "review needed", "cohort report print")

        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: founder
        client.cookies.clear()
        founder_login = client.post(
            "/login",
            data={
                "email": "maya.ellis@northstar-demo.example",
                "password": seed_demo_cohort.DEMO_PASSWORD,
            },
            follow_redirects=False,
        )
        assert founder_login.status_code == 303, founder_login.text
        founder_memo = assert_200(
            client.get("/dashboard/lab/decision-memo/print?run_id=run_demo_complete"),
            "founder decision memo print",
        )
        assert_contains(founder_memo, "run_demo_complete", "founder decision memo print")
        founder_report = client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/outcome-report/print")
        assert founder_report.status_code == 403, founder_report.text
        founder_demo = client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/accelerator-demo")
        assert founder_demo.status_code == 403, founder_demo.text

        for doc in DOCS:
            path = REPO_DIR / doc
            assert path.exists(), f"{doc} missing"
            text = path.read_text(encoding="utf-8")
            assert len(text.strip()) > 500, f"{doc} unexpectedly short"
            assert "does not predict startup success" in text.lower() or "not predict startup success" in text.lower(), f"{doc} missing no-overclaim language"

        print(
            "PILOT READINESS SMOKE PASS: "
            f"print routes render for {seeded['cohort_id']}; "
            f"{len(DOCS)} docs checked; founder report access refused"
        )


if __name__ == "__main__":
    main()
