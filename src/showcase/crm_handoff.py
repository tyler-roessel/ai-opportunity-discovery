"""Sanitized Stage 5 CRM handoff gate."""

from __future__ import annotations

from typing import Any

from .states import (
    CRM_NOT_READY,
    CRM_PAYLOAD_FIELD_MAP,
    DRAFT_APPROVED,
    STAGE_DRAFT_READY,
)


REQUIRED_STAGE5_FIELDS = {
    "company_name",
    "website",
    "company_summary",
    "icp_status",
    "priority_score",
    "subject_line_1",
    "email_draft",
    "source_urls_used",
}


def is_stage5_crm_ready(record: dict[str, Any]) -> bool:
    if record.get("stage") != STAGE_DRAFT_READY:
        return False
    if record.get("draft_status") != DRAFT_APPROVED:
        return False
    if record.get("crm_sync_status") != CRM_NOT_READY:
        return False
    return all(str(record.get(field) or "").strip() for field in REQUIRED_STAGE5_FIELDS)


def build_stage5_crm_payload(record: dict[str, Any]) -> dict[str, Any]:
    if not is_stage5_crm_ready(record):
        raise ValueError("record does not satisfy Stage 5 CRM handoff gate")

    payload: dict[str, Any] = {}
    for source_field, crm_field in CRM_PAYLOAD_FIELD_MAP.items():
        value = record.get(source_field)
        if value in (None, ""):
            continue
        payload[crm_field] = value
    return payload

