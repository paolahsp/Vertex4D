"""Capture the VERTEX demo rehearsal screenshots against a local server."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8010"
COHORT_ID = "cohort_83a643a003"
OUT = Path("docs/demo_rehearsal_assets")
OUT.mkdir(parents=True, exist_ok=True)


STEPS = []


def capture(page, filename: str, title: str, description: str, result: str, full_page: bool = True) -> None:
    path = OUT / filename
    page.screenshot(path=str(path), full_page=full_page)
    STEPS.append({
        "title": title,
        "description": description,
        "result": result,
        "screenshot": str(path),
        "url": page.url,
    })


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 980}, device_scale_factor=1)
        page = context.new_page()

        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        capture(
            page,
            "01-login.png",
            "Login",
            "Open the live local app and prepare facilitator authentication.",
            "Login page loaded correctly.",
        )

        page.fill("#email", "facilitator@northstar-demo.example")
        page.fill("#password", "vertex-demo-2026")
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE_URL}/dashboard/facilitator", wait_until="networkidle")
        capture(
            page,
            "02-facilitator-dashboard.png",
            "Facilitator dashboard",
            "Open the program-level dashboard after facilitator login.",
            "Dashboard renders cohort metrics, Decision Case counts, locked snapshots and open comments.",
        )

        page.goto(f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}", wait_until="networkidle")
        capture(
            page,
            "03-cohort-case-room.png",
            "Cohort case room",
            "Open the seeded demo cohort case room.",
            "Cohort totals, add-case controls and intervention queue are visible.",
        )

        page.locator(".cm-panel").filter(has_text="Intervention queue").scroll_into_view_if_needed()
        capture(
            page,
            "04-intervention-queue.png",
            "Intervention queue",
            "Focus the cohort page on the intervention queue.",
            "SkillBridge and ClinicFlow appear as honest intervention needs with reasons.",
            full_page=False,
        )

        page.locator("#case-run_demo_intervention").scroll_into_view_if_needed()
        capture(
            page,
            "05-intervention-case-comments.png",
            "Case comments and rubric gap",
            "Open the case that needs facilitator intervention.",
            "Open comment and missing post score are visible on the case.",
            full_page=False,
        )

        page.goto(f"{BASE_URL}/dashboard/lab/decision-memo?run_id=run_demo_economics_changed", wait_until="networkidle")
        capture(
            page,
            "06-decision-memo.png",
            "Decision Memo",
            "Open the economics-changed Decision Memo.",
            "Memo shows initial decision context, final decision, pricing insight and artifact traceability.",
        )

        page.goto(f"{BASE_URL}/dashboard/lab/decision-memo/print?run_id=run_demo_economics_changed", wait_until="networkidle")
        capture(
            page,
            "07-decision-memo-print.png",
            "Decision Memo print view",
            "Open print-friendly Decision Memo artifact.",
            "White print view includes generated timestamp, run/team/cohort identifiers, traceability IDs and no-overclaim disclaimer.",
        )
        page.pdf(path=str(OUT / "decision-memo-run_demo_economics_changed.pdf"), format="Letter", print_background=True)

        page.goto(f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report", wait_until="networkidle")
        capture(
            page,
            "08-outcome-report.png",
            "Cohort Outcome Report",
            "Open the cohort-level institutional report.",
            "Report summarizes completion, baselines, DecisionRecords, stakeholder/price/decision changes and intervention needs.",
        )

        page.goto(f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report/print", wait_until="networkidle")
        capture(
            page,
            "09-outcome-report-print.png",
            "Outcome Report print view",
            "Open print-friendly Cohort Outcome Report artifact.",
            "White print view includes cohort identifiers, case table, missing data labels, methodology and no-overclaim disclaimer.",
        )
        page.pdf(path=str(OUT / "cohort-outcome-report-demo.pdf"), format="Letter", landscape=True, print_background=True)

        browser.close()

    (OUT / "capture_manifest.json").write_text(json.dumps(STEPS, indent=2), encoding="utf-8")
    print(json.dumps({"steps": len(STEPS), "out": str(OUT), "cohort_id": COHORT_ID}, indent=2))


if __name__ == "__main__":
    main()
