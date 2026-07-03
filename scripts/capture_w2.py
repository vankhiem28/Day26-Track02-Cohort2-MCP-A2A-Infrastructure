"""Capture riêng W2 — chờ 35s cho chuỗi 3 MCP tool hoàn tất."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8000/"
OUT_DIR = Path("screenshots")
OUT_DIR.mkdir(exist_ok=True)

PROMPT = (
    "Bước 1: dùng search_documents tìm MCP. "
    "Bước 2: dùng sql_query SELECT * FROM agent_metrics. "
    "Bước 3: tóm tắt báo cáo ngắn."
)


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)
        await page.wait_for_selector("textarea", timeout=15_000)

        ta = await page.query_selector("textarea")
        await ta.click()
        await ta.fill(PROMPT)
        await page.keyboard.press("Enter")
        print("→ đã gửi W2, chờ 40s cho 3 MCP tool hoàn tất...")

        await page.wait_for_timeout(90_000)
        out = OUT_DIR / "adk_web_w2.png"
        await page.screenshot(path=str(out), full_page=False)
        print(f"✓ {out}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())