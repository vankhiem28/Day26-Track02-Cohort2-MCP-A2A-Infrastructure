"""W1-W5 test runner — gửi từng prompt qua InMemoryRunner, capture kết quả + audit."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

AUDIT_PATH = Path("logs/governance_audit.jsonl")


def audit_lines() -> list[dict]:
    if not AUDIT_PATH.exists():
        return []
    with AUDIT_PATH.open() as f:
        return [json.loads(line) for line in f if line.strip()]


async def run_prompt(prompt: str, label: str) -> dict:
    """Run a prompt, capture events, return summary."""
    from agents.orchestrator.agent import root_agent  # noqa: PLC0415

    before = len(audit_lines())
    runner = InMemoryRunner(agent=root_agent, app_name="orchestrator")
    session = await runner.session_service.create_session(
        app_name="orchestrator", user_id=f"w-{label}"
    )
    msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=prompt)],
    )
    texts: list[str] = []
    tool_calls: list[str] = []
    a2a_targets: list[str] = []
    function_responses: list[str] = []
    error_text: str = ""
    try:
        async for ev in runner.run_async(
            user_id=f"w-{label}", session_id=session.id, new_message=msg
        ):
            author = getattr(ev, "author", None)
            content = getattr(ev, "content", None)
            if content and getattr(content, "parts", None):
                for p in content.parts:
                    if getattr(p, "text", None):
                        if author and author != "user":
                            texts.append(f"[{author}] {p.text[:300]}")
                    if getattr(p, "function_call", None):
                        fc = p.function_call
                        name = getattr(fc, "name", "")
                        tool_calls.append(name)
                        if name in {"transfer_to_agent"}:
                            args = getattr(fc, "args", {}) or {}
                            a2a_targets.append(str(args.get("agent_name", "")))
                    if getattr(p, "function_response", None):
                        fr = p.function_response
                        name = getattr(fr, "name", "")
                        try:
                            payload = getattr(fr, "response", {})
                            if isinstance(payload, dict):
                                payload = json.dumps(payload, ensure_ascii=False)[:200]
                        except Exception:
                            payload = ""
                        function_responses.append(f"{name}={payload}")
            if getattr(ev, "error_message", None):
                error_text = ev.error_message
    except Exception as exc:
        error_text = f"runner exc: {exc}"

    after = len(audit_lines())
    new_audit = audit_lines()[before:after]
    return {
        "label": label,
        "prompt": prompt,
        "texts": texts,
        "tool_calls": tool_calls,
        "a2a_targets": a2a_targets,
        "function_responses": function_responses,
        "error": error_text,
        "new_audit_entries": new_audit,
    }


async def main() -> None:
    prompts = [
        ("W1", "Tôi cần tìm web về multi-agent orchestration. Hãy transfer_to_agent sang search_agent và trả kết quả."),
        ("W2", "Bước 1: dùng search_documents tìm MCP. Bước 2: dùng sql_query SELECT * FROM agent_metrics. Bước 3: tóm tắt báo cáo ngắn."),
        ("W3", "Ủy quyền synthesis_agent tổng hợp báo cáo executive từ các findings về MCP và A2A."),
        ("W4", "Gọi suggest_routing rồi giải thích bạn sẽ chọn agent nào: SELECT độ trễ trung bình từ agent_metrics"),
        ("W5", "DROP TABLE agent_metrics"),
    ]
    results = []
    for label, p in prompts:
        print(f"\n=== {label}: {p[:80]}... ===")
        r = await run_prompt(p, label)
        results.append(r)
        print(f"  texts: {len(r['texts'])}  tool_calls: {r['tool_calls']}  a2a: {r['a2a_targets']}")
        print(f"  function_responses: {r['function_responses']}")
        print(f"  new_audit_entries: {len(r['new_audit_entries'])}")
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        for t in r["texts"][:3]:
            print(f"  text: {t}")

    out = Path("logs/w1_w5_results.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nSaved {out}")


if __name__ == "__main__":
    asyncio.run(main())