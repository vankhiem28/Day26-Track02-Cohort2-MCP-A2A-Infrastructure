# Plan: Hoàn thành Day 26 Capstone + các bài tập notebook

## Goal
1. Hệ 4-agent (orchestrator + 3 specialist A2A + MCP) chạy ổn định với governance.
2. Chạy hết `day26_mcp_a2a_lab.ipynb` từng cell.
3. Hoàn thành **mọi bài tập** trong notebook (1.1, 1.2, 2.1, 3.1, 5.1, 5.2) + **5 prompt W1–W5** trong ADK Web.
4. Điền bảng kết quả `adk_web_results` ở cell [032].
5. Verify checklist capstone ở cell [045].

## Context
- Repo: `Day26-Track02-Cohort2-MCP-A2A-Infrastructure`
- Stack: Google ADK 2.3.0 + MCP (stdio) + A2A (HTTP agent card) + Gemini 2.5 Flash
- Đã có sẵn:
  - **Miniconda** ở `/opt/homebrew/Caskroom/miniconda/base`
  - **conda env `pii-env`** (Python 3.12) đã cài `requirements.txt` — `import google.adk; from mcp.server import Server` OK
  - **`.env`** đã có `GOOGLE_API_KEY` hợp lệ
  - **Thư mục `venv/`** (Homebrew Python 3.14 + `google-adk`) — **KHÔNG DÙNG**, chỉ pii-env theo README
  - Script `_lab_env.sh` ưu tiên `${CONDA_PREFIX}/bin/python` nếu conda env đang active, nếu không rơi về `python3` → vì thế phải `conda activate pii-env` trước khi chạy `start_*.sh`.

## Kiến trúc mục tiêu

| Port | Service | Source |
|------|---------|--------|
| — | MCP stdio (subprocess orchestrator) | `mcp_server/research_tools_server.py` |
| 8001 | A2A search_agent | `agents/search_agent/agent.py:a2a_app` |
| 8002 | A2A database_agent | `agents/database_agent/agent.py:a2a_app` |
| 8003 | A2A synthesis_agent | `agents/synthesis_agent/agent.py:a2a_app` |
| 8000 | ADK Web UI (orchestrator) | `agents/orchestrator/agent.py:root_agent` |

## Notebook inventory (cell index tham chiếu)

| Cell | Nội dung |
|------|----------|
| 001–007 | Module 0 — env setup, import |
| 008–012 | Module 1 — MCP server, `McpToolset`, bài tập 1.1 + **1.2** (thêm `count_words`) |
| 013–018 | Module 2 — A2A spec + agent card check + bài tập **2.1** (so sánh table) |
| 019–025 | Module 3 — SemanticRouter + AgentRegistry + bài tập **3.1** (Fallback chain) |
| 026–033 | Module 4 — `run_full_flow` + Capstone **W1–W5** trong ADK Web + điền `adk_web_results` |
| 034–045 | Module 5 — State, Governance `policy.json`, bài tập **5.1** (thiết kế capability matrix) + **5.2** (mở rộng policy) + capstone checklist |

## Tasks

### Phase A — Khởi động hệ thống

1. **Activate conda env + kiểm tra**
   ```bash
   eval "$(conda shell.zsh hook)"
   conda activate pii-env
   which python          # phải ra .../envs/pii-env/bin/python
   python -c "import google.adk; from mcp.server import Server; print('ok')"
   ```

2. **Khởi động A2A servers** (3 server nền, chạy từ `pii-env`):
   ```bash
   cd /Users/vankhiem/workspace/vin/Day26/Day26-Track02-Cohort2-MCP-A2A-Infrastructure
   bash scripts/start_a2a_servers.sh
   ```
   - Phải thấy `→ Python: .../envs/pii-env/bin/python` (không phải `venv/bin/python`).
   - Cuối script: 3 dòng `(search OK)` `(database OK)` `(synthesis OK)`.

3. **Khởi động ADK Web** (terminal riêng, vẫn trong `pii-env`):
   ```bash
   export PYTHONPATH="$PWD"
   adk web agents/orchestrator --port 8000
   # Mở http://localhost:8000/dev-ui/
   ```
   Hoặc gộp: `bash scripts/start_capstone.sh` (gộp cả 4 process trong 1 terminal, Ctrl+C dừng tất cả).

### Phase B — Chạy notebook Module 0 → 3, làm bài tập tương ứng

Chạy jupyter **trong cùng `pii-env`** để kernel có `google-adk` + `mcp`:
```bash
jupyter notebook day26_mcp_a2a_lab.ipynb
```
Chọn kernel `pii-env` (hoặc `Python 3 (ipykernel)` sau khi register).

4. **Cell [008] Module 1 — Bài tập 1.1**: đọc `mcp_server/research_tools_server.py`, trả lời 3 câu hỏi ngay trong cell markdown: 3 tool nào, `_sql_query` enforce governance thế nào, vì sao stdio khi dev local.
5. **Cell [012] Bài tập 1.2 — thêm tool `count_words`**:
   - Sửa `mcp_server/research_tools_server.py:60` (block `list_tools`) thêm entry mới.
   - Thêm handler trong `call_tool()` (cùng file, khoảng dòng 125).
   - Cập nhật `tool_filter` trong `agents/orchestrator/agent.py:99` nếu muốn orchestrator thấy tool này.
   - Restart `start_a2a_servers.sh` + `adk web` để nạp code mới.
   - Test: gõ "Đếm số từ trong câu: ..." → tool xuất hiện trong Trace.
6. **Cell [013–015] Module 2**: chạy cell kiểm tra agent card (chỉ chạy để xác nhận :8001/:8002 còn sống).
7. **Cell [018] Bài tập 2.1**: điền bảng so sánh A2A vs Sub-Agent Local (4 tiêu chí: Triển khai, Hiệu năng, Cô lập state, Phù hợp khi) + đoạn thảo luận.
8. **Cell [023] Bài tập 3.1 — Fallback chain**: thêm method `route_with_chain(self, request: str, chain: list[str]) -> str` trong `lab_utils/semantic_router.py`. Test với `chain=["search_agent", "database_agent", "orchestrator"]`.

### Phase C — Module 4 + W1–W5 trong ADK Web

9. **Cell [028] Ví dụ 1 + [028–029] Ví dụ 2**: chạy `run_full_flow` (nếu Gemini không trả 503). Nếu 503, ghi nhận trong notebook là "Gemini unavailable", vẫn qua Capstone.
10. **Cell [030] Cell kiểm tra trước capstone** (chạy nếu cần), rồi thực hiện **W1–W5** trong ADK Web UI:
    - Mở `http://localhost:8000`, **tạo session mới** (+), chọn `orchestrator`.
    - Gõ từng prompt copy y nguyên từ cell [032] (W1–W5).
    - Mở **Trace** (panel phải) để xem `transfer_to_agent`, MCP calls, A2A events.
    - Terminal thứ 3: `tail -f logs/governance_audit.jsonl | python3 -m json.tool --json-lines`.
11. **Cell [032] điền `adk_web_results`**: thay placeholder bằng quan sát thực tế. Đặc biệt:
    - **W1**: `agents_involved = ["orchestrator", "search_agent"]`, outcome ĐẠT nếu có text từ search_agent.
    - **W2**: protocol `MCP (search_documents, sql_query)` — đã dùng MCP local.
    - **W3**: `["orchestrator", "synthesis_agent"]` — A2A.
    - **W4**: protocol `suggest_routing` — `recommended_agent` phải khớp dự đoán.
    - **W5**: protocol `MCP sql_query — governance deny` — outcome ĐẠT nếu response có `blocked/deny`.

### Phase D — Module 5 + bài tập governance

12. **Cell [037] cell governance**: chạy, xác nhận output:
    - DROP TABLE → `block`
    - SELECT hợp lệ → `allow`
    - A2A đến `search_agent` → `allow`; đến `email_agent` → `block`
    - PII email → `hitl_required`
13. **Cell [039] Bài tập 5.2 — mở rộng policy**:
    - Sửa `lab_utils/governance/policy.json:36-39` — thêm `synthesis_agent` vào `allowed_targets` của orchestrator.
    - Thêm rule chặn từ khóa `password` trong `search_documents` (cần sửa `lab_utils/governance/guard.py`).
    - Restart hệ thống, chạy lại cell governance, xác nhận audit ghi đủ.
14. **Cell [042] Bài tập 5.1 — thiết kế capability matrix**: viết 4 yêu cầu (tool/agent, hành động HITL, rate limit, giới hạn tool calls) — ghi vào cell markdown.
15. **Cell [044–045] capstone checklist**: tick từng dòng theo thực tế.

### Phase E — Đóng

16. **Screenshot/đối chiếu**: chụp ADK Web cho W1, W2 (theo yêu cầu nộp bài của notebook).
17. **Dừng hệ thống**:
    ```bash
    bash scripts/stop_a2a_servers.sh
    # Ctrl+C terminal ADK Web
    # Hoặc: lsof -ti :8000 -i :8001 -i :8002 -i :8003 | xargs -r kill -9
    ```

## Validation
- [ ] `conda activate pii-env` → `which python` ra `.../envs/pii-env/bin/python`.
- [ ] `bash scripts/start_a2a_servers.sh` thấy `→ Python: .../envs/pii-env/bin/python` (không phải `venv/bin/python`).
- [ ] `curl :8001/, :8002/, :8003/` agent-card trả 200.
- [ ] `adb web` lên, `/list-apps` có `["orchestrator"]`.
- [ ] Notebook chạy hết 19 code cell không lỗi kernel.
- [ ] Tool `count_words` (bài 1.2) xuất hiện trong ADK Web Trace khi gõ prompt liên quan.
- [ ] W1–W5 đều được nhập vào ADK Web, từng turn có entry mới trong `logs/governance_audit.jsonl` (kiểm `connection_type ∈ {a2a, mcp}` và `actor=orchestrator`).
- [ ] W5 (DROP TABLE) có verdict `block` trong audit.
- [ ] Bài 5.2 sửa `policy.json` xong, cell governance chạy lại cho kết quả mới (nhưng không phá vỡ các test cũ).
- [ ] Capstone checklist cell [045] tick đủ 10 dòng.

## Risks & Caveats
- **Env trộn**: nếu `which python` ra `venv/bin/python` thay vì `pii-env`, tức conda chưa active trong shell đó. Luôn `eval "$(conda shell.zsh hook)" && conda activate pii-env` ở đầu mỗi terminal mới.
- **Gemini 503**: lab trước từng thấy `503 UNAVAILABLE`. Chỉ retry — không phải lỗi hệ thống.
- **`start_a2a_servers.sh` chạy 2 lần liên tiếp** sẽ **tự kill server cũ** để nạp code mới (`lsof -ti :port | xargs kill` trong script dòng 14–17). Hành vi này bình thường, không phải lỗi — nhưng nếu muốn giữ state thì restart riêng từng agent.
- **Bài 1.2 / 5.2 sửa code → phải restart** cả 3 A2A + ADK Web để MCP/A2A nạp policy mới. Plan task 5 và 13 đã ghi rõ.
- **Audit log chung**: `logs/governance_audit.jsonl` ghi từ cả notebook (nếu có chạy cell governance) + ADK Web. Không vấn đề nhưng khó tách nếu muốn phân tích từng nguồn.
- **Notebook kernel**: Jupyter mặc định đăng ký kernel theo env hiện tại. Nếu mở notebook lần đầu trong `pii-env` thì kernel `Python 3 (ipykernel)` đã có; không cần cài thêm.

## Out of scope
- Production hardening, TLS, multi-tenant, replace demo data.
- Chạy W1–W5 tự động (notebook/UI là manual).
- Triển khai transport SSE cho MCP (thử thách mở rộng — bỏ).
