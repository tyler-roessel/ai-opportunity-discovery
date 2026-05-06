"""Public-safe integration mapping from terminal params to staged records.

This module shows the shape a CTO would look for:
terminal run parameters become a source-provider request, source results become
review-table records, and later stages decide whether CRM handoff is allowed.
No live provider calls happen here.
"""

from __future__ import annotations

from typing import Any

from .states import STAGE_DISCOVERED


def build_source_request(
    *,
    vertical: str,
    source_provider: str,
    query: str,
    limit: int,
    mode: str = "dry_run",
) -> dict[str, Any]:
    """Map CLI-style parameters into a source-client request."""
    if mode != "dry_run":
        raise ValueError("public showcase only supports dry_run mode")
    return {
        "provider": source_provider,
        "vertical": vertical,
        "query": query,
        "limit": limit,
        "mode": mode,
    }


def map_source_result_to_review_record(
    result: dict[str, Any],
    *,
    vertical: str,
    discovery_source: str,
) -> dict[str, Any]:
    """Map a Firecrawl/search/job-source result into the review-table shape."""
    title = result.get("job_title") or result.get("title") or "Unknown role"
    source_url = result.get("source_url") or result.get("url") or ""
    snippet = result.get("snippet") or result.get("description") or ""
    return {
        "company_name": result.get("name", ""),
        "website": result.get("url", ""),
        "vertical": vertical,
        "stage": STAGE_DISCOVERED,
        "discovery_source": discovery_source,
        "posting_url": source_url,
        "active_job_postings": [
            {
                "title": title,
                "department": result.get("department", ""),
                "source_url": source_url,
                "posting_context": snippet,
            }
        ],
        "source_urls_used": source_url,
        "needs_human_review": True,
    }


def run_source_to_review_table_demo(
    *,
    vertical: str,
    source_provider: str,
    query: str,
    limit: int,
    source_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Demonstrate terminal -> source provider -> review table mapping."""
    request = build_source_request(
        vertical=vertical,
        source_provider=source_provider,
        query=query,
        limit=limit,
    )
    records = [
        map_source_result_to_review_record(
            result,
            vertical=vertical,
            discovery_source=f"{source_provider}_search",
        )
        for result in source_results[:limit]
    ]
    return {
        "request": request,
        "review_table_records": records,
        "would_write_to_review_table": len(records),
        "mode": "dry_run",
    }

