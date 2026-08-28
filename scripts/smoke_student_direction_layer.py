"""Smoke test the student-facing direction layer across Quest modules."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]

ROUTES = [
    ("/dashboard/vertex/spark", "Locked Baseline + ProjectRecord", "Create a Spark case"),
    ("/dashboard/vertex/riddle", "ProblemFrame", "Save a ProblemFrame"),
    ("/dashboard/vertex/tangle", "SystemMap", "Save a SystemMap"),
    ("/dashboard/vertex/gatekeeper", "Approved assumption register", "Approve only assumptions"),
    ("/dashboard/vertex/ripple", "PredictiveHypothesis + QBI lite reading", "Create a PredictiveHypothesis"),
    ("/dashboard/vertex/ledger", "FinancialScenario", "Create a FinancialScenario"),
    ("/dashboard/vertex/stamp", "Stamp / DecisionRecord", "Create and save a Stamp"),
    ("/dashboard/lab/start-golden-path", "Locked Baseline + ProjectRecord", "Create a Spark case"),
    ("/dashboard/lab/assumption-approval", "Approved assumption register", "Approve only assumptions"),
    ("/dashboard/lab/decision-record", "Stamp / DecisionRecord", "Create and save a Stamp"),
]

LAB_TOOL_ROUTES = [
    ("/dashboard/lab", "Srsly Labs Lab", "VERTEX 4D Quest is separate"),
    ("/dashboard/lab/d-predict", "D-Predict / MiroFish", "Scenario Stress Test"),
    ("/dashboard/orbit", "The Orbit", "Evidence Orbit"),
    ("/dashboard/lab/finops", "FinOps Central", "coming soon"),
]

FUNCTIONAL_LAB_ROUTES = [
    (
        "/dashboard/lab/alex",
        ["Alex", "/api/alex/chat", "download-pdf-btn", "Socratic chat"],
    ),
    (
        "/dashboard/lab/synapmap",
        ["SynapMap", "d3.forceSimulation", "/api/process-file", "RACI Matrix", "system-map-svg"],
    ),
]


def assert_200(response, label: str) -> str:
    assert response.status_code == 200, f"{label} failed: {response.status_code} {response.text[:500]}"
    return response.text


def assert_contains(text: str, needle: str, label: str) -> None:
    assert needle.lower() in text.lower(), f"{label} missing expected text: {needle}"


def assert_not_contains(text: str, needle: str, label: str) -> None:
    assert needle.lower() not in text.lower(), f"{label} should not contain: {needle}"


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

        for route, name, status in LAB_TOOL_ROUTES:
            text = assert_200(client.get(route), route)
            assert_contains(text, name, route)
            assert_contains(text, "Srsly Labs Lab", route)
            assert_contains(text, status, route)

        for route, markers in FUNCTIONAL_LAB_ROUTES:
            text = assert_200(client.get(route), route)
            for marker in markers:
                assert_contains(text, marker, route)

        alex_lab = assert_200(client.get("/dashboard/lab/alex"), "lab alex")
        for forbidden in ["Riddle | VERTEX 4D", "Configure Riddle", "Next action", "Student direction and deliverable", "_path_bar", "_direction_strip"]:
            assert_not_contains(alex_lab, forbidden, "lab alex")

        synapmap_lab = assert_200(client.get("/dashboard/lab/synapmap"), "lab synapmap")
        for forbidden in ["Tangle", "Gatekeeper", "Student direction and deliverable", "Next action", "_path_bar", "_direction_strip"]:
            assert_not_contains(synapmap_lab, forbidden, "lab synapmap")

        tangle_vertex = assert_200(client.get("/dashboard/vertex/tangle"), "vertex tangle")
        for marker in ["Tangle", "SystemMap", "Student direction and deliverable", "Next action", "Gatekeeper", "artifacts/system_map/save"]:
            assert_contains(tangle_vertex, marker, "vertex tangle")

        billie_lab = assert_200(client.get("/dashboard/lab/billie"), "lab billie")
        for marker in ["Billie Storyteller", "Srsly Labs Lab", "Positioning Statement", "Safe Claims"]:
            assert_contains(billie_lab, marker, "lab billie")
        for forbidden in ["FinancialScenario", "pricing calculator"]:
            assert_not_contains(billie_lab, forbidden, "lab billie")

        dpredict_lab = assert_200(client.get("/dashboard/lab/d-predict"), "lab d-predict")
        for marker in ["D-Predict / MiroFish", "Scenario Stress Test", "quantum-like behavioral simulation", "localStorage only", "Readings, not forecasts"]:
            assert_contains(dpredict_lab, marker, "lab d-predict")
        for forbidden in ["PredictiveHypothesis", "Student direction and deliverable", "Next action", "_path_bar", "_direction_strip"]:
            assert_not_contains(dpredict_lab, forbidden, "lab d-predict")

        orbit_lab = assert_200(client.get("/dashboard/orbit"), "lab orbit")
        for marker in ["The Orbit", "Srsly Labs Lab", "Evidence Orbit", "Signal", "Confidence", "Shared Evidence", "local draft", "orbit_evidence_current"]:
            assert_contains(orbit_lab, marker, "lab orbit")
        for forbidden in ["automatic matching", "real-time monitoring", "external signal feed", "Student direction and deliverable", "Gatekeeper"]:
            assert_not_contains(orbit_lab, forbidden, "lab orbit")

        ripple_vertex = assert_200(client.get("/dashboard/vertex/ripple"), "vertex ripple")
        for marker in ["Ripple", "PredictiveHypothesis", "QBI lite", "Student direction and deliverable"]:
            assert_contains(ripple_vertex, marker, "vertex ripple")

        ledger_vertex = assert_200(client.get("/dashboard/vertex/ledger"), "vertex ledger")
        assert_contains(ledger_vertex, "Ledger", "vertex ledger")
        assert_contains(ledger_vertex, "FinancialScenario", "vertex ledger")

        doc_path = REPO_DIR / "docs" / "VERTEX_ACCELERATOR_EDUCATIONAL_DEMO.md"
        doc = doc_path.read_text(encoding="utf-8")
        assert_contains(doc, "Where Students Work", str(doc_path))
        assert_contains(doc, "Module And Deliverable Map", str(doc_path))
        assert_contains(doc, "Ready for guided accelerator demo", str(doc_path))

        print(
            "STUDENT DIRECTION SMOKE PASS: "
            f"{len(ROUTES)} Quest routes render direction layer; "
            f"{len(LAB_TOOL_ROUTES)} Lab status routes render honestly; "
            f"{len(FUNCTIONAL_LAB_ROUTES)} Lab tools keep functional markers"
        )


if __name__ == "__main__":
    main()
