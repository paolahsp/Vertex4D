"""Smoke test the student-facing direction layer across Golden Path modules."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]

ROUTES = [
    ("/dashboard/lab/start-golden-path", "Locked Baseline + ProjectRecord", "Create a Decision Case"),
    ("/dashboard/lab/alex", "ProblemFrame", "Save a ProblemFrame"),
    ("/dashboard/lab/synapmap", "SystemMap", "Save a SystemMap"),
    ("/dashboard/lab/assumption-approval", "Approved assumption register", "Approve only assumptions"),
    ("/dashboard/lab/d-predict", "PredictiveHypothesis + QBI lite reading", "Create a PredictiveHypothesis"),
    ("/dashboard/lab/billie", "FinancialScenario", "Create a FinancialScenario"),
    ("/dashboard/lab/decision-record", "DecisionRecord", "Create and save a DecisionRecord"),
]


def assert_200(response, label: str) -> str:
    assert response.status_code == 200, f"{label} failed: {response.status_code} {response.text[:500]}"
    return response.text


def assert_contains(text: str, needle: str, label: str) -> None:
    assert needle.lower() in text.lower(), f"{label} missing expected text: {needle}"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        os.environ["VERTEX4D_DATABASE_PATH"] = str(tmp_path / "vertex4d-student-direction.db")
        os.environ["VERTEX4D_RUNTIME_DIR"] = str(tmp_path / "runs")
        os.chdir(REPO_DIR)
        sys.path.insert(0, str(REPO_DIR))

        from fastapi.testclient import TestClient

        import main as app_main
        from scripts import seed_demo_cohort

        seed_demo_cohort.seed_demo_cohort(reset_existing=True)
        client = TestClient(app_main.app)
        login = client.post(
            "/login",
            data={
                "email": "maya.ellis@northstar-demo.example",
                "password": seed_demo_cohort.DEMO_PASSWORD,
            },
            follow_redirects=False,
        )
        assert login.status_code == 303, login.text

        for route, artifact, next_action in ROUTES:
            text = assert_200(client.get(route), route)
            assert_contains(text, "Student direction and deliverable", route)
            assert_contains(text, "Next action", route)
            assert_contains(text, "Why it matters", route)
            assert_contains(text, "What VERTEX should reveal", route)
            assert_contains(text, "Where this goes", route)
            assert_contains(text, artifact, route)
            assert_contains(text, next_action, route)

        doc_path = REPO_DIR / "docs" / "VERTEX_ACCELERATOR_EDUCATIONAL_DEMO.md"
        doc = doc_path.read_text(encoding="utf-8")
        assert_contains(doc, "Where Students Work", str(doc_path))
        assert_contains(doc, "Module And Deliverable Map", str(doc_path))
        assert_contains(doc, "Ready for guided accelerator demo", str(doc_path))

        print(f"STUDENT DIRECTION SMOKE PASS: {len(ROUTES)} module routes render direction layer")


if __name__ == "__main__":
    main()
