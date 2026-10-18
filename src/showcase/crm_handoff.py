"""Sanitized Stage 5 CRM handoff gate."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any
from urllib.parse import urlparse

from .states import (
    CRM_NOT_READY,
    CRM_SYNCED_ERROR,
    CRM_PAYLOAD_FIELD_MAP,
    DRAFT_APPROVED,
    DRAFT_READY,
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


def draft_fingerprint(record: dict[str, Any]) -> str:
    """Bind a review decision to its exact draft and supporting context."""
    fields = REQUIRED_STAGE5_FIELDS | set(CRM_PAYLOAD_FIELD_MAP)
    content = {field: record.get(field) for field in sorted(fields)}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode("utf-8")).hexdigest()


def approve_draft(record: dict[str, Any], *, reviewer: str) -> None:
    """Record an explicit local review decision. Never called by pipeline stages."""
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("reviewer is required")
    if record.get("stage") != STAGE_DRAFT_READY or record.get("draft_status") != DRAFT_READY:
        raise ValueError("only a draft-ready record can be approved")
    if not _has_valid_content(record):
        raise ValueError("draft context is incomplete or invalid")
    record["draft_status"] = DRAFT_APPROVED
    record["draft_reviewed_by"] = reviewer.strip()
    record["draft_approval_fingerprint"] = draft_fingerprint(record)


def _has_valid_content(record: dict[str, Any]) -> bool:
    for field in REQUIRED_STAGE5_FIELDS - {"priority_score"}:
        if not isinstance(record.get(field), str) or not record[field].strip():
            return False
    score = record.get("priority_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return False
    if not math.isfinite(score) or not 0 <= score <= 100:
        return False
    if record.get("icp_status") not in {"candidate", "target"}:
        return False
    try:
        for url in [record["website"], *record["source_urls_used"].splitlines()]:
            parsed = urlparse(url.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                return False
    except ValueError:
        return False
    return True


def is_stage5_crm_ready(record: dict[str, Any]) -> bool:
    if record.get("stage") != STAGE_DRAFT_READY:
        return False
    if record.get("draft_status") != DRAFT_APPROVED:
        return False
    if record.get("crm_sync_status") not in {CRM_NOT_READY, CRM_SYNCED_ERROR}:
        return False
    return (
        _has_valid_content(record)
        and isinstance(record.get("draft_reviewed_by"), str)
        and bool(record["draft_reviewed_by"].strip())
        and record.get("draft_approval_fingerprint") == draft_fingerprint(record)
    )


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

