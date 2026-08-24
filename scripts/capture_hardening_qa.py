from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


BASE_URL = "http://127.0.0.1:8011"
COHORT_ID = "cohort_49b5190b81"
OUT = Path("docs/hardening_qa_assets")


async def set_light_mode(page) -> None:
    await page.evaluate(
        """
        () => {
            document.documentElement.dataset.theme = 'light';
            document.documentElement.dataset.motion = 'none';
            document.documentElement.dataset.focus = 'off';
            document.getAnimations().forEach((animation) => animation.finish());
        }
        """
    )


async def capture(page, name: str, url: str, full_page: bool = True) -> None:
    await page.goto(url, wait_until="networkidle")
    await set_light_mode(page)
    await page.screenshot(path=str(OUT / name), full_page=full_page)


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": 1440, "height": 1100})
        page = await context.new_page()
        await page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        await set_light_mode(page)
        await page.fill('input[name="email"]', "facilitator@northstar-demo.example")
        await page.fill('input[name="password"]', "vertex-demo-2026")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        await capture(page, "01-cohort-desktop.png", f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}", full_page=True)
        await capture(page, "02-memo-desktop.png", f"{BASE_URL}/dashboard/lab/decision-memo?run_id=run_demo_economics_changed", full_page=True)
        await capture(page, "03-outcome-desktop.png", f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report", full_page=True)
        await capture(page, "04-evidence-gate-desktop.png", f"{BASE_URL}/dashboard/lab/start-golden-path", full_page=False)

        mobile = await browser.new_context(viewport={"width": 390, "height": 900}, is_mobile=True)
        mpage = await mobile.new_page()
        await mpage.goto(f"{BASE_URL}/login", wait_until="networkidle")
        await set_light_mode(mpage)
        await mpage.fill('input[name="email"]', "facilitator@northstar-demo.example")
        await mpage.fill('input[name="password"]', "vertex-demo-2026")
        await mpage.click('button[type="submit"]')
        await mpage.wait_for_load_state("networkidle")
        await capture(mpage, "05-cohort-mobile.png", f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}", full_page=True)
        await capture(mpage, "06-memo-mobile.png", f"{BASE_URL}/dashboard/lab/decision-memo?run_id=run_demo_economics_changed", full_page=True)
        await capture(mpage, "07-outcome-mobile.png", f"{BASE_URL}/dashboard/facilitator/cohorts/{COHORT_ID}/outcome-report", full_page=True)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
