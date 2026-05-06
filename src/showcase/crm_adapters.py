"""Generic CRM payload adapters for public review.

The private workflow used a specific CRM. This module shows how the same Stage 5
approved record can map to Attio, Salesforce, or HubSpot-style payloads without
changing the upstream five-stage workflow.
"""

from __future__ import annotations

from typing import Any

from .crm_handoff import build_stage5_crm_payload


def build_crm_payload(record: dict[str, Any], *, crm: str) -> dict[str, Any]:
    """Build a public-safe CRM payload from an approved Stage 5 record."""
    base = build_stage5_crm_payload(record)
    normalized = crm.strip().lower()
    if normalized == "attio":
        return _attio_payload(base)
    if normalized == "salesforce":
        return _salesforce_payload(base)
    if normalized == "hubspot":
        return _hubspot_payload(base)
    raise ValueError(f"unsupported crm adapter: {crm}")


def _attio_payload(base: dict[str, Any]) -> dict[str, Any]:
    return {
        "crm": "attio",
        "object": "companies",
        "fields": {
            "name": base.get("name"),
            "website": base.get("website"),
            "vertical": base.get("vertical"),
            "priority_score": base.get("priority_score"),
            "priority_tier": base.get("priority_tier"),
            "approved_draft": base.get("email_draft"),
            "source_urls_used": base.get("source_urls_used"),
        },
    }


def _salesforce_payload(base: dict[str, Any]) -> dict[str, Any]:
    return {
        "crm": "salesforce",
        "object": "Account",
        "fields": {
            "Name": base.get("name"),
            "Website": base.get("website"),
            "Industry": base.get("vertical"),
            "Priority_Score__c": base.get("priority_score"),
            "Priority_Tier__c": base.get("priority_tier"),
            "Approved_Draft__c": base.get("email_draft"),
            "Source_URLs_Used__c": base.get("source_urls_used"),
        },
    }


def _hubspot_payload(base: dict[str, Any]) -> dict[str, Any]:
    return {
        "crm": "hubspot",
        "object": "companies",
        "properties": {
            "name": base.get("name"),
            "domain": base.get("website"),
            "vertical": base.get("vertical"),
            "priority_score": base.get("priority_score"),
            "priority_tier": base.get("priority_tier"),
            "approved_draft": base.get("email_draft"),
            "source_urls_used": base.get("source_urls_used"),
        },
    }

