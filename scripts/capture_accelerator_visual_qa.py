"""Capture accelerator-demo visual QA screenshots against a local VERTEX server."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.seed_demo_cohort import (
    DEMO_CASES,
    DEMO_PASSWORD,
    FACILITATOR_EMAIL,
    demo_email,
    get_demo_cohort_id,
)


BASE_URL = os.environ.get("VERTEX_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
COHORT_ID = os.environ.get("VERTEX_DEMO_COHORT_ID") or get_demo_cohort_id()
FOUNDER_EMAIL = os.environ.get(
    "VERTEX_DEMO_FOUNDER_EMAIL",
    demo_email(DEMO_CASES[0]),
)
OUT = Path("docs/accelerator_visual_qa_assets")


STUDENT_PAGES = [
    {
        "file": "01-student-spark-desktop.png",
        "title": "Student workspace: Spark",
        "url": "/dashboard/vertex/spark",
        "description": "Student enters Quest and sees the baseline job before any downstream artifact.",
        "expected": ["Open Spark", "Locked Baseline + ProjectRecord", "Next action"],
    },
    {
        "file": "02-student-riddle-desktop.png",
        "title": "Student workspace: Riddle",
        "url": "/dashboard/vertex/riddle",
        "description": "Student frames the problem and sees why the ProblemFrame matters downstream.",
        "expected": ["Riddle", "ProblemFrame", "Why it matters"],
    },
    {
        "file": "03-student-tangle-desktop.png",
        "title": "Student workspace: Tangle",
        "url": "/dashboard/vertex/tangle",
        "description": "Student maps users, payers, approvers, blockers and dependencies.",
        "expected": ["Tangle", "SystemMap", "payer"],
    },
    {
        "file": "04-student-gatekeeper-desktop.png",
        "title": "Student workspace: Gatekeeper",
        "url": "/dashboard/vertex/gatekeeper",
        "description": "Student/facilitator sees which assumptions can propagate into Ripple or Ledger.",
        "expected": ["Approved assumption register", "Hard gate", "downstream"],
    },
    {
        "file": "05-student-ripple-desktop.png",
        "title": "Student workspace: Ripple + QBI lite",
        "url": "/dashboard/vertex/ripple",
        "description": "Student creates a bounded behavior hypothesis and sees QBI lite as a reading, not a prediction.",
        "expected": ["Ripple", "PredictiveHypothesis", "QBI lite"],
    },
    {
        "file": "06-student-ledger-desktop.png",
        "title": "Student workspace: Ledger",
        "url": "/dashboard/vertex/ledger",
        "description": "Student tests economic assumptions and pricing coherence.",
        "expected": ["Ledger", "FinancialScenario", "price"],
    },
    {
        "file": "07-student-stamp-desktop.png",
        "title": "Student workspace: Stamp",
        "url": "/dashboard/vertex/stamp",
        "description": "Student converts the reviewed chain into a bounded next commitment.",
        "expected": ["Stamp", "final decision", "provenance"],
    },
]


FACILITATOR_PAGES = [
    {
        "file": "08-facilitator-dashboard-desktop.png",
        "title": "Facilitator dashboard",
        "url": "/dashboard/facilitator",
        "description": "Facilitator sees cohort-level work, readiness and entry points.",
        "expected": ["Facilitator", "cohort", "Decision"],
    },
    {
        "file": "08b-accelerator-demo-mode-desktop.png",
        "title": "Accelerator Demo Mode",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}/accelerator-demo",
        "description": "Buyer-facing presentation flow for the seeded accelerator demo cohort.",
        "expected": ["Accelerator Demo Mode", "run_demo_economics_changed", "run_demo_decision_changed", "Outcome Report"],
    },
    {
        "file": "09-cohort-case-room-desktop.png",
        "title": "Cohort case room",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}",
        "description": "Facilitator reviews intervention queue, cases, comments and rubric gaps.",
        "expected": ["Intervention", "Demo Cohort", "rubric"],
    },
    {
        "file": "10-outcome-report-desktop.png",
        "title": "Cohort Outcome Report",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report",
        "description": "Buyer-facing report summarizes before/after movement and missing data.",
        "expected": ["Outcome Report", "Stamp", "intervention"],
    },
    {
        "file": "11-student-brief-desktop.png",
        "title": "Student workspace: Brief",
        "url": "/dashboard/vertex/brief?run_id=run_demo_economics_changed",
        "description": "Student/buyer sees the case-level Brief that connects baseline, evidence and final decision.",
        "expected": ["Brief", "run_demo_economics_changed", "price"],
    },
]


MOBILE_PAGES = [
    {
        "file": "12-student-spark-mobile.png",
        "title": "Mobile student: Spark",
        "url": "/dashboard/vertex/spark",
        "description": "Checks the first student step at buyer/mobile width.",
        "expected": ["Spark", "Next action"],
    },
    {
        "file": "13-student-ripple-mobile.png",
        "title": "Mobile student: Ripple + QBI lite",
        "url": "/dashboard/vertex/ripple",
        "description": "Checks whether the densest behavior module stays readable on mobile.",
        "expected": ["QBI lite", "PredictiveHypothesis"],
    },
    {
        "file": "13b-accelerator-demo-mode-mobile.png",
        "title": "Mobile facilitator: Accelerator Demo Mode",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}/accelerator-demo",
        "description": "Checks buyer-facing demo mode on mobile.",
        "expected": ["Accelerator Demo Mode", "run_demo_economics_changed", "Outcome Report"],
    },
    {
        "file": "14-cohort-case-room-mobile.png",
        "title": "Mobile facilitator: Cohort case room",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}",
        "description": "Checks facilitator scanability on mobile.",
        "expected": ["Intervention", "rubric"],
    },
    {
        "file": "15-outcome-report-mobile.png",
        "title": "Mobile buyer: Outcome Report",
        "url": f"/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report",
        "description": "Checks buyer report readability on mobile.",
        "expected": ["Outcome Report", "Stamp"],
    },
]


def set_light_mode(page) -> None:
    page.evaluate(
        """
        () => {
            document.documentElement.dataset.theme = 'light';
            document.documentElement.dataset.motion = 'none';
            document.documentElement.dataset.focus = 'off';
            document.getAnimations().forEach((animation) => animation.finish());
        }
        """
    )


def login(page, email: str) -> None:
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    set_light_mode(page)
    page.fill("#email", email)
    page.fill("#password", DEMO_PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def layout_metrics(page) -> dict:
    return page.evaluate(
        """
        () => {
            const doc = document.documentElement;
            const body = document.body;
            const viewportWidth = doc.clientWidth;
            const scrollWidth = Math.max(doc.scrollWidth, body.scrollWidth);
            const direction = document.querySelector('.v4-direction');
            const clipped = [];
            for (const el of document.querySelectorAll('main *')) {
                const style = getComputedStyle(el);
                if (el.offsetParent === null || style.display === 'none') continue;
                const hasText = (el.innerText || '').trim().length > 0;
                const isClipped = el.scrollWidth > el.clientWidth + 3 && style.overflowX === 'visible';
                if (hasText && isClipped) {
                    clipped.push({
                        tag: el.tagName.toLowerCase(),
                        className: String(el.className || '').slice(0, 90),
                        text: (el.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120),
                        clientWidth: el.clientWidth,
                        scrollWidth: el.scrollWidth
                    });
                }
                if (clipped.length >= 12) break;
            }
            return {
                title: document.title,
                viewportWidth,
                viewportHeight: window.innerHeight,
                scrollWidth,
                scrollHeight: Math.max(doc.scrollHeight, body.scrollHeight),
                horizontalOverflowPx: Math.max(0, scrollWidth - viewportWidth),
                directionPresent: Boolean(direction),
                directionText: direction ? direction.innerText.trim().replace(/\\s+/g, ' ').slice(0, 420) : '',
                visibleHeadings: Array.from(document.querySelectorAll('h1,h2')).slice(0, 8).map((h) => h.innerText.trim()),
                clippedTextCandidates: clipped
            };
        }
        """
    )


def expected_checks(page, expected: list[str]) -> dict:
    content = page.locator("body").inner_text(timeout=3000)
    return {marker: marker.lower() in content.lower() for marker in expected}


def capture(page, item: dict, viewport: str, authenticated_as: str) -> dict:
    path = OUT / item["file"]
    page.goto(f"{BASE_URL}{item['url']}", wait_until="networkidle")
    set_light_mode(page)
    metrics = layout_metrics(page)
    checks = expected_checks(page, item["expected"])
    page.screenshot(path=str(path), full_page=True)
    return {
        "title": item["title"],
        "description": item["description"],
        "url": f"{BASE_URL}{item['url']}",
        "viewport": viewport,
        "authenticated_as": authenticated_as,
        "screenshot": str(path),
        "expected_checks": checks,
        "layout": metrics,
    }


def main() -> None:
    if not COHORT_ID:
        raise SystemExit("No demo cohort found. Run: python scripts\\seed_demo_cohort.py")

    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "cohort_id": COHORT_ID,
        "student_login": FOUNDER_EMAIL,
        "facilitator_login": FACILITATOR_EMAIL,
        "screens": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        student_context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        student_page = student_context.new_page()
        login(student_page, FOUNDER_EMAIL)
        for item in STUDENT_PAGES:
            manifest["screens"].append(capture(student_page, item, "desktop 1440x1100", FOUNDER_EMAIL))

        facilitator_context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        facilitator_page = facilitator_context.new_page()
        login(facilitator_page, FACILITATOR_EMAIL)
        for item in FACILITATOR_PAGES:
            manifest["screens"].append(capture(facilitator_page, item, "desktop 1440x1100", FACILITATOR_EMAIL))

        mobile_student = browser.new_context(viewport={"width": 390, "height": 900}, is_mobile=True)
        mobile_student_page = mobile_student.new_page()
        login(mobile_student_page, FOUNDER_EMAIL)
        for item in MOBILE_PAGES[:2]:
            manifest["screens"].append(capture(mobile_student_page, item, "mobile 390x900", FOUNDER_EMAIL))

        mobile_facilitator = browser.new_context(viewport={"width": 390, "height": 900}, is_mobile=True)
        mobile_facilitator_page = mobile_facilitator.new_page()
        login(mobile_facilitator_page, FACILITATOR_EMAIL)
        for item in MOBILE_PAGES[2:]:
            manifest["screens"].append(capture(mobile_facilitator_page, item, "mobile 390x900", FACILITATOR_EMAIL))

        browser.close()

    (OUT / "capture_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"screens": len(manifest["screens"]), "out": str(OUT), "cohort_id": COHORT_ID}, indent=2))


if __name__ == "__main__":
    main()
