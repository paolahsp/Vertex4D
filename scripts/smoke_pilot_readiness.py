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
        assert client.get("/dashboard/facilitator").status_code == 200, "facilitator dashboard should still render"
        assert client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/outcome-report").status_code == 200, "report should still render"

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
        founder_memo = assert_200(
            client.get("/dashboard/lab/decision-memo/print?run_id=run_demo_complete"),
            "founder decision memo print",
        )
        assert_contains(founder_memo, "run_demo_complete", "founder decision memo print")
        founder_report = client.get(f"/dashboard/facilitator/cohorts/{seeded['cohort_id']}/outcome-report/print")
        assert founder_report.status_code == 403, founder_report.text

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
