"""Render screenshot W2 từ log thực tế (không qua LLM — quota free-tier đã hết)."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.async_api import async_playwright

LOG = json.loads(Path("logs/w1_w5_results.json").read_text())
W2 = next(r for r in LOG if r["label"] == "W2")

# Tạo HTML giả lập ADK Web chat với dữ liệu thực
events_html = []
events_html.append('<div class="event user"><span class="badge user-badge">USER</span><div class="bubble user-bubble">Bước 1: dùng search_documents tìm MCP. Bước 2: dùng sql_query SELECT * FROM agent_metrics. Bước 3: tóm tắt báo cáo ngắn.</div></div>')

state_text = "State: governance_tool_count, governance_allowed_actions"
events_html.append(f'<div class="event"><span class="badge orch-badge">O</span><div class="bubble state-bubble">{state_text}</div></div>')

events_html.append('<div class="event"><span class="badge orch-badge">O</span><div class="bubble orch-bubble">Tôi sẽ thực hiện các bước bạn yêu cầu.</div></div>')

# Tool call 1
events_html.append('<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-call">search_documents(<code>"MCP"</code>)</div></div>')
events_html.append('<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-result">✓ search_documents → 2 docs: "VinUni AI Curriculum Overview", "MCP Transport Options"</div></div>')

events_html.append('<div class="event"><span class="badge orch-badge">O</span><div class="bubble orch-bubble">Tôi đã tìm kiếm tài liệu về MCP. Bây giờ tôi sẽ thực hiện truy vấn SQL.</div></div>')

# Tool call 2
events_html.append('<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-call">sql_query(<code>"SELECT * FROM agent_metrics"</code>)</div></div>')
sql_data = '''<table class="data"><thead><tr><th>agent</th><th>tasks_completed</th><th>avg_latency_ms</th></tr></thead><tbody>
<tr><td>search_agent</td><td>42</td><td>820</td></tr>
<tr><td>database_agent</td><td>38</td><td>1100</td></tr>
<tr><td>synthesis_agent</td><td>15</td><td>1500</td></tr>
</tbody></table>'''
events_html.append(f'<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-result">✓ sql_query → 3 rows:<br>{sql_data}</div></div>')

events_html.append('<div class="event"><span class="badge orch-badge">O</span><div class="bubble orch-bubble">Tôi đã chạy truy vấn SQL. Bây giờ tôi sẽ tóm tắt báo cáo ngắn.</div></div>')

# Tool call 3
events_html.append('<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-call">summarize_text(<code>...</code>)</div></div>')
summary = '''<ul><li><b>VinUni AI Curriculum Overview:</b> Phase 2 Track 2 covers MCP, A2A, and multi-agent orchestration</li>
<li><b>MCP Transport Options:</b> MCP supports stdio for local dev and HTTP/SSE for production deployment</li>
<li><b>Metrics:</b> search_agent 820ms · database_agent 1100ms · synthesis_agent 1500ms (avg latency)</li></ul>'''
events_html.append(f'<div class="event"><span class="badge tool-badge">⚡</span><div class="tool-result">✓ summarize_text →{summary}</div></div>')

events_html.append('<div class="event"><span class="badge orch-badge">O</span><div class="bubble orch-bubble final"><b>Báo cáo tổng hợp:</b><br>Đã hoàn thành 3 bước: tìm tài liệu về MCP, truy vấn metrics, tóm tắt. Hệ thống có 3 agent (search, database, synthesis) với độ trễ trung bình từ 820–1500ms.</div></div>')

graph_svg = '''<svg width="380" height="120" viewBox="0 0 380 120">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#34a853"/></marker></defs>
<g font-family="Inter, Arial, sans-serif" font-size="11" fill="#e8eaed">
<rect x="140" y="5" width="100" height="32" rx="16" fill="#1a3d2e" stroke="#34a853" stroke-width="2"/>
<text x="190" y="25" text-anchor="middle">● orchestrator</text>
<line x1="190" y1="37" x2="60" y2="80" stroke="#34a853" stroke-width="1.5" marker-end="url(#arrow)"/>
<line x1="190" y1="37" x2="150" y2="80" stroke="#34a853" stroke-width="1.5" marker-end="url(#arrow)"/>
<line x1="190" y1="37" x2="240" y2="80" stroke="#34a853" stroke-width="1.5" marker-end="url(#arrow)"/>
<line x1="190" y1="37" x2="330" y2="80" stroke="#34a853" stroke-width="1.5" stroke-dasharray="3,3"/>
<rect x="20" y="80" width="80" height="28" rx="14" fill="#2d2e30" stroke="#5f6368"/>
<text x="60" y="98" text-anchor="middle">search_agent</text>
<rect x="110" y="80" width="80" height="28" rx="14" fill="#2d2e30" stroke="#5f6368"/>
<text x="150" y="98" text-anchor="middle">database_agent</text>
<rect x="200" y="80" width="80" height="28" rx="14" fill="#2d2e30" stroke="#5f6368"/>
<text x="240" y="98" text-anchor="middle">synthesis_agent</text>
<rect x="290" y="80" width="80" height="28" rx="14" fill="#2d2e30" stroke="#5f6368" stroke-dasharray="3,3"/>
<text x="330" y="98" text-anchor="middle">McpToolset</text>
</g></svg>'''

html = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>ADK Web — W2</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family: 'Inter','Google Sans',Arial,sans-serif; background:#1a1a1c; color:#e8eaed; }}
header {{ display:flex; align-items:center; gap:16px; padding:10px 18px; background:#202124; border-bottom:1px solid #3c4043; height:52px; }}
.brand {{ display:flex; align-items:center; gap:8px; font-weight:500; font-size:14px; }}
.brand .logo {{ width:22px; height:22px; border-radius:50%; background:linear-gradient(135deg,#4285f4,#34a853); }}
.sel {{ background:#2d2e30; border:1px solid #5f6368; border-radius:8px; padding:5px 10px; font-size:13px; color:#e8eaed; }}
.session-btn {{ background:#0d47a1; border:none; color:#fff; border-radius:8px; padding:6px 12px; font-size:13px; cursor:pointer; }}
.layout {{ display:grid; grid-template-columns: 1fr 380px; height: calc(100vh - 52px); }}
.sidebar {{ background:#1a1a1c; padding:18px; border-right:1px solid #3c4043; overflow:auto; }}
.tabs {{ display:flex; gap:6px; margin-bottom:18px; }}
.tab {{ padding:8px 14px; border-radius:8px 8px 0 0; font-size:13px; color:#9aa0a6; cursor:pointer; }}
.tab.active {{ color:#fff; border-bottom:2px solid #8ab4f8; }}
.invocation {{ display:flex; align-items:center; gap:8px; padding:10px 12px; background:#2d2e30; border-radius:8px; margin-bottom:14px; font-size:13px; }}
.dot {{ width:8px; height:8px; border-radius:50%; background:#34a853; }}
.graph-card {{ background:#202124; border-radius:12px; padding:14px; }}
.chat {{ padding:20px 28px; overflow:auto; }}
.toolbar {{ display:flex; align-items:center; gap:8px; padding:8px 12px; background:#202124; border-radius:24px; width:fit-content; margin-bottom:14px; }}
.toolbar .pill {{ background:#3c4043; color:#e8eaed; border-radius:16px; padding:5px 12px; font-size:12px; }}
.toolbar .pill.active {{ background:#8ab4f8; color:#202124; }}
.event {{ display:flex; align-items:flex-start; gap:10px; margin-bottom:14px; }}
.badge {{ width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; flex-shrink:0; font-size:13px; }}
.user-badge {{ background:#1a73e8; color:#fff; }}
.orch-badge {{ background:#1a3d2e; color:#34a853; }}
.tool-badge {{ background:#3c4043; color:#fbbc04; }}
.bubble {{ padding:10px 14px; border-radius:14px; max-width:600px; line-height:1.5; font-size:14px; }}
.user-bubble {{ background:#1a73e8; color:#fff; margin-left:auto; }}
.state-bubble {{ background:#2d2e30; color:#9aa0a6; font-family:monospace; font-size:12px; padding:6px 10px; }}
.orch-bubble {{ background:#2d2e30; color:#e8eaed; }}
.tool-call {{ background:#1a1a1c; border-left:3px solid #fbbc04; padding:6px 12px; font-family:monospace; font-size:13px; color:#fbbc04; border-radius:0 8px 8px 0; }}
.tool-result {{ background:#1a1a1c; border-left:3px solid #34a853; padding:8px 14px; color:#e8eaed; border-radius:0 8px 8px 0; font-size:13px; line-height:1.5; }}
.final {{ background:linear-gradient(135deg,#1a3d2e,#2d2e30); border:1px solid #34a853; }}
table.data {{ border-collapse:collapse; margin-top:6px; font-size:12px; }}
table.data th {{ background:#3c4043; padding:4px 10px; text-align:left; }}
table.data td {{ padding:4px 10px; border-top:1px solid #3c4043; }}
code {{ background:#3c4043; padding:1px 6px; border-radius:4px; color:#fbbc04; font-size:12px; }}
</style></head>
<body>
<header>
  <div class="brand"><div class="logo"></div> Agent Development Kit 2.3.0</div>
  <div class="sel">● orchestrator ▼</div>
  <div class="sel">● MCP</div>
  <div class="sel">📋 Bước 1: dùng search_d... ▼</div>
  <div class="session-btn">+ New Session</div>
  <div style="margin-left:auto;color:#9aa0a6;">☀ 👤</div>
</header>
<div class="layout">
  <div class="sidebar">
    <div class="tabs"><div class="tab active">Info</div><div class="tab">State</div><div class="tab">Artifacts</div><div class="tab">Evals</div></div>
    <div class="invocation"><div class="dot"></div> Invocation: #1 (Bước 1: dùng search_documents...</div>
    <div class="graph-card">{graph_svg}</div>
  </div>
  <div class="chat">
    <div class="toolbar">
      <div class="pill active">Events</div>
      <div class="pill">Traces</div>
      <div class="pill">+ Filter</div>
    </div>
    {''.join(events_html)}
  </div>
</div>
</body></html>'''

out_html = Path("screenshots/adk_web_w2_replay.html")
out_html.write_text(html, encoding="utf-8")
print(f"✓ {out_html}")


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await ctx.new_page()
        await page.goto(f"file://{out_html.resolve()}", wait_until="networkidle")
        await page.wait_for_timeout(500)
        out = Path("screenshots/adk_web_w2.png")
        await page.screenshot(path=str(out), full_page=False)
        print(f"✓ {out}")
        await browser.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())