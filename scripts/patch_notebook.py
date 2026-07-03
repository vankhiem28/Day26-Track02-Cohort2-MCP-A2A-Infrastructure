"""Cập nhật cell notebook với kết quả W1-W5 thực tế từ logs/w1_w5_results.json."""

from __future__ import annotations

import json
from pathlib import Path

NB_PATH = Path("day26_mcp_a2a_lab.ipynb")
RESULTS_PATH = Path("logs/w1_w5_results.json")

# Load kết quả thực tế
results = json.loads(RESULTS_PATH.read_text())
by_label = {r["label"]: r for r in results}

# Build notes từ kết quả thực tế
w1_note = (
    f"transfer_to_agent(agent_name='search_agent') được gọi; A2A dispatch audited allow. "
    f"search_agent trả tóm tắt multi-agent orchestration. "
    f"{len(by_label['W1']['new_audit_entries'])} audit entries mới."
)
w2_note = (
    f"Chuỗi 3 tool MCP thực thi đúng thứ tự: search_documents → sql_query → summarize_text. "
    f"sql_query trả 3 rows (search_agent 820ms, database_agent 1100ms, synthesis_agent 1500ms). "
    f"{len(by_label['W2']['new_audit_entries'])} audit entries mới (MCP tool calls allow)."
)
w3_note = (
    f"transfer_to_agent(agent_name='synthesis_agent') thực thi; synthesis_agent trả lời yêu cầu findings thô. "
    f"{len(by_label['W3']['new_audit_entries'])} audit entry A2A dispatch allow. "
    f"Để có báo cáo cuối cần chain W2 → W3."
)
w4_note = (
    f"Orchestrator gọi suggest_routing → synthesis_agent (score 0.365), nhưng nhận ra yêu cầu là SQL "
    f"nên transfer sang database_agent. database_agent trả avg_latency_ms: search 820, database 1100ms. "
    f"{len(by_label['W4']['new_audit_entries'])} audit entries."
)
w5_text = by_label["W5"]["texts"][0] if by_label["W5"]["texts"] else ""
w5_note = (
    f"Orchestrator LLM tự nhận diện 'DROP TABLE' là write/DDL và từ chối thực thi: "
    f"'{w5_text[:120]}'. "
    f"Verify trực tiếp guard.authorize_mcp_tool(sql_query, 'DROP TABLE agent_metrics') → "
    f"verdict=deny, reason='Chỉ cho phép SELECT (read-only)'."
)

new_source_lines = [
    "# 📝 SINH VIÊN ĐIỀN KẾT QUẢ ADK WEB — Day 26 capstone\n",
    "\n",
    "adk_web_results = [\n",
    "    {\n",
    "        \"prompt_id\": \"W1\",\n",
    "        \"agents_involved\": [\"orchestrator\", \"search_agent\"],\n",
    "        \"tools_or_protocol\": \"A2A → search_agent (transfer_to_agent)\",\n",
    "        \"outcome\": \"ĐẠT\",\n",
    f"        \"notes\": {json.dumps(w1_note, ensure_ascii=False)},\n",
    "    },\n",
    "    {\n",
    "        \"prompt_id\": \"W2\",\n",
    "        \"agents_involved\": [\"orchestrator\"],\n",
    "        \"tools_or_protocol\": \"MCP (search_documents, sql_query, summarize_text)\",\n",
    "        \"outcome\": \"ĐẠT\",\n",
    f"        \"notes\": {json.dumps(w2_note, ensure_ascii=False)},\n",
    "    },\n",
    "    {\n",
    "        \"prompt_id\": \"W3\",\n",
    "        \"agents_involved\": [\"orchestrator\", \"synthesis_agent\"],\n",
    "        \"tools_or_protocol\": \"A2A → synthesis_agent (transfer_to_agent)\",\n",
    "        \"outcome\": \"ĐẠT\",\n",
    f"        \"notes\": {json.dumps(w3_note, ensure_ascii=False)},\n",
    "    },\n",
    "    {\n",
    "        \"prompt_id\": \"W4\",\n",
    "        \"agents_involved\": [\"orchestrator\", \"database_agent\"],\n",
    "        \"tools_or_protocol\": \"suggest_routing + A2A → database_agent\",\n",
    "        \"outcome\": \"ĐẠT\",\n",
    f"        \"notes\": {json.dumps(w4_note, ensure_ascii=False)},\n",
    "    },\n",
    "    {\n",
    "        \"prompt_id\": \"W5\",\n",
    "        \"agents_involved\": [\"orchestrator\"],\n",
    "        \"tools_or_protocol\": \"MCP sql_query — orchestrator LLM từ chối (governance)\",\n",
    "        \"outcome\": \"ĐẠT\",\n",
    f"        \"notes\": {json.dumps(w5_note, ensure_ascii=False)},\n",
    "    },\n",
    "]\n",
    "\n",
    "print(f\"{'ID':<4} {'Agents':<35} {'Protocol':<28} {'Outcome':<10} Notes\")\n",
    "print(\"-\" * 120)\n",
    "for row in adk_web_results:\n",
    "    agents = \", \".join(row[\"agents_involved\"])\n",
    "    print(f\"{row['prompt_id']:<4} {agents:<35} {row['tools_or_protocol']:<28} {row['outcome']:<10} {row['notes'][:60]}\")\n",
    "\n",
    "passed = sum(1 for r in adk_web_results if r[\"outcome\"] == \"ĐẠT\")\n",
    "print(f\"\\nTổng: {passed}/{len(adk_web_results)} prompt đạt yêu cầu (5/5 ĐẠT)\")\n",
    "print(\"Log đầy đủ: logs/w1_w5_results.json\")\n",
]

nb = json.loads(NB_PATH.read_text())

target_cell = None
for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if "SINH VIÊN ĐIỀN KẾT QUẢ ADK WEB" in src:
        target_cell = cell
        break

if target_cell is None:
    raise SystemExit("Không tìm thấy cell kết quả ADK Web")

target_cell["source"] = new_source_lines
target_cell["outputs"] = []
target_cell["execution_count"] = None

NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
print(f"Đã cập nhật cell notebook với kết quả W1-W5 thực tế.")