"""Screenshot ADK Web UI: trang chủ + sau khi gửi prompt W1 và W5."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8000/"
OUT_DIR = Path("screenshots")
OUT_DIR.mkdir(exist_ok=True)


async def capture_home(page) -> Path:
    await page.goto(URL, wait_until="networkidle", timeout=60_000)
    await page.wait_for_timeout(2000)
    out = OUT_DIR / "adk_web_home.png"
    await page.screenshot(path=str(out), full_page=False)
    print(f"✓ {out}")
    return out


async def capture_prompt(page, prompt: str, out_name: str) -> Path:
    """Gửi prompt tới ADK Web và chụp màn hình sau khi phản hồi."""
    await page.goto(URL, wait_until="networkidle", timeout=60_000)
    await page.wait_for_timeout(2000)

    # Thử tạo session mới + ô input
    try:
        # ADK Web UI: textarea + nút gửi
        await page.wait_for_selector("textarea", timeout=15_000)
    except Exception:
        # Fallback: chờ app load
        await page.wait_for_timeout(5000)

    # Tìm textarea + gõ prompt
    ta = await page.query_selector("textarea")
    if not ta:
        # Thử contenteditable
        ta = await page.query_selector("[contenteditable='true']")
    if not ta:
        out = OUT_DIR / f"{out_name}_no_input.png"
        await page.screenshot(path=str(out), full_page=False)
        print(f"✗ Không tìm thấy input — {out}")
        return out

    await ta.click()
    await ta.fill(prompt)
    await page.wait_for_timeout(500)

    # Enter hoặc bấm nút gửi
    await page.keyboard.press("Enter")
    print(f"  → đã gửi prompt: {prompt[:60]}...")

    # Chờ phản hồi (streaming)
    await page.wait_for_timeout(20_000)

    out = OUT_DIR / f"{out_name}.png"
    await page.screenshot(path=str(out), full_page=False)
    print(f"✓ {out}")
    return out


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        await capture_home(page)

        # W1 — A2A tới search_agent
        await capture_prompt(
            page,
            "Tôi cần tìm web về multi-agent orchestration. Hãy transfer_to_agent sang search_agent và trả kết quả.",
            "adk_web_w1",
        )

        # W5 — governance block
        await capture_prompt(
            page,
            "DROP TABLE agent_metrics",
            "adk_web_w5",
        )

        # W2 — MCP multi-tool
        await capture_prompt(
            page,
            "Bước 1: dùng search_documents tìm MCP. Bước 2: dùng sql_query SELECT * FROM agent_metrics. Bước 3: tóm tắt báo cáo ngắn.",
            "adk_web_w2",
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())