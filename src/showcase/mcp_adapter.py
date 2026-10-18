"""MCP-style adapter for approved handoff records.

MCP is modeled here as a transport envelope around the same Stage 5-approved
payload. The point is that MCP does not replace the workflow gates; it becomes
one possible execution surface after the record is approved.
"""

from __future__ import annotations

from typing import Any

from .crm_handoff import build_stage5_crm_payload


def build_mcp_tool_call(
    record: dict[str, Any],
    *,
    server: str,
    tool: str,
) -> dict[str, Any]:
    """Build a public-safe MCP tool call envelope from an approved record."""
    payload = build_stage5_crm_payload(record)
    return {
        "transport": "mcp",
        "server": server,
        "tool": tool,
        "arguments": payload,
        "approval_gate": {
            "stage": record.get("stage"),
            "draft_status": record.get("draft_status"),
            "crm_sync_status": record.get("crm_sync_status"),
            "reviewed_by": record.get("draft_reviewed_by"),
            "content_fingerprint": record.get("draft_approval_fingerprint"),
        },
        "mode": "preview",
    }

