"""Re-run failed W3, W4, W5 with delays to respect Gemini free-tier rate limit (5 req/min)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_w1_w5 import run_prompt


async def main() -> None:
    out_path = Path("logs/w1_w5_results.json")
    existing = json.loads(out_path.read_text()) if out_path.exists() else []
    by_label = {r["label"]: r for r in existing}

    prompts = [
        ("W3", "Ủy quyền synthesis_agent tổng hợp báo cáo executive từ các findings về MCP và A2A."),
        ("W4", "Gọi suggest_routing rồi giải thích bạn sẽ chọn agent nào: SELECT độ trễ trung bình từ agent_metrics"),
        ("W5", "DROP TABLE agent_metrics"),
    ]
    for i, (label, p) in enumerate(prompts):
        print(f"\n=== {label} ===")
        r = await run_prompt(p, label)
        by_label[label] = r
        print(f"  texts: {len(r['texts'])}  tool_calls: {r['tool_calls']}  a2a: {r['a2a_targets']}")
        print(f"  function_responses: {r['function_responses'][:1]}")
        print(f"  new_audit_entries: {len(r['new_audit_entries'])}")
        if r["error"]:
            print(f"  ERROR: {r['error'][:200]}")
        for t in r["texts"][:3]:
            print(f"  text: {t[:200]}")
        if i < len(prompts) - 1:
            print("  (sleeping 70s for quota reset)")
            await asyncio.sleep(70)

    out = list(by_label.values())
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    asyncio.run(main())