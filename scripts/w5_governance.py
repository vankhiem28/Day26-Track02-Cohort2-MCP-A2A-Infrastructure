"""W5 governance deny test — không qua LLM, gọi thẳng guard.

Mục đích: xác nhận policy.json block DROP TABLE ngay cả khi LLM quota exhausted.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab_utils.governance import AuditLogger, get_guard


def main() -> None:
    guard = get_guard()
    audit = AuditLogger()
    AUDIT_PATH = Path("logs/governance_audit.jsonl")
    before = sum(1 for _ in AUDIT_PATH.open()) if AUDIT_PATH.exists() else 0

    bad_sql = guard.authorize_mcp_tool(
        "orchestrator", "sql_query", {"sql": "DROP TABLE agent_metrics"}
    )
    print(f"DROP TABLE → {bad_sql.verdict.value}: {bad_sql.reason}")

    pii_sql = guard.authorize_mcp_tool(
        "orchestrator",
        "sql_query",
        {"sql": "SELECT * FROM agent_metrics WHERE email='user@vinuni.edu.vn'"},
    )
    print(f"PII email → {pii_sql.verdict.value}: {pii_sql.reason}")

    good_sql = guard.authorize_mcp_tool(
        "orchestrator", "sql_query", {"sql": "SELECT * FROM agent_metrics"}
    )
    print(f"SELECT hợp lệ → {good_sql.verdict.value}")

    ssn_sql = guard.authorize_mcp_tool(
        "orchestrator",
        "sql_query",
        {"sql": "SELECT * FROM agent_metrics WHERE ssn='123-45-6789'"},
    )
    print(f"PII SSN → {ssn_sql.verdict.value}: {ssn_sql.reason}")

    after = sum(1 for _ in AUDIT_PATH.open())
    new_entries = after - before
    print(f"\nAudit entries mới: {new_entries}")
    print("Summary:", audit.summary())


if __name__ == "__main__":
    main()