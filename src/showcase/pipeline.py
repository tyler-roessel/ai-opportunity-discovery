"""Small local-only demo of the five-stage state machine.

This file is intentionally not connected to live Airtable, Attio, n8n, Firecrawl,
or LLM APIs. It preserves the orchestration shape and failure accounting from
the private system with fake records only.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .crm_handoff import build_stage5_crm_payload, is_stage5_crm_ready
from .filters import evaluate_stage1_record
from .states import (
    CRM_NOT_READY,
    DRAFT_APPROVED,
    DRAFT_READY,
    DRAFT_NEEDS_REVIEW,
    DRAFT_REJECTED,
    STAGE_DISCOVERED,
    STAGE_DRAFT_READY,
    STAGE_ENRICHED,
    STAGE_IDENTITY_CONFIRMED,
    STAGE_NEEDS_REVIEW,
    STAGE_REJECTED,
)


def load_sample_records() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[2] / "examples" / "sample-records.json"
    return json.loads(path.read_text())


def run_stage1(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {
        "stage": "Stage 1",
        "fetched": len(records),
        "passed": 0,
        "rejected": 0,
        "errors": [],
    }
    for record in records:
        if record.get("stage") not in {None, STAGE_DISCOVERED}:
            continue
        try:
            decision = evaluate_stage1_record(record)
            record["stage1_filter_decision"] = "passed" if decision.passed else "rejected"
            record["stage1_filter_reason"] = decision.reason
            if decision.passed:
                record["stage"] = STAGE_DISCOVERED
                results["passed"] += 1
            else:
                record["stage"] = STAGE_REJECTED
                results["rejected"] += 1
        except Exception as exc:
            record["stage"] = STAGE_NEEDS_REVIEW
            record["identity_review_status"] = "Needs Review"
            results["errors"].append({"company": record.get("company_name", "?"), "error": str(exc)})
    return results


def run_stage2(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {"stage": "Stage 2", "reviewed": 0, "identity_confirmed": 0, "needs_review": 0}
    for record in records:
        if record.get("stage") not in {STAGE_DISCOVERED, STAGE_NEEDS_REVIEW}:
            continue
        results["reviewed"] += 1
        try:
            website = urlparse(str(record.get("website") or ""))
            valid_website = website.scheme in {"http", "https"} and bool(website.hostname)
        except ValueError:
            valid_website = False
        if (
            valid_website
            and record.get("identity_review_status") == "Approved"
            and isinstance(record.get("identity_reviewed_by"), str)
            and record["identity_reviewed_by"].strip()
        ):
            record["stage"] = STAGE_IDENTITY_CONFIRMED
            record["identity_confidence"] = "HIGH"
            record["identity_reasoning"] = "Explicit identity review supplied with the input record."
            record["needs_human_review"] = False
            results["identity_confirmed"] += 1
        else:
            record["stage"] = STAGE_NEEDS_REVIEW
            record["needs_human_review"] = True
            results["needs_review"] += 1
    return results


def run_stage3(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {
        "stage": "Stage 3",
        "fetched": 0,
        "enriched": 0,
        "scrape_failures": 0,
        "llm_failures": 0,
        "write_failures": 0,
        "errors": [],
    }
    for record in records:
        if record.get("stage") != STAGE_IDENTITY_CONFIRMED:
            continue
        results["fetched"] += 1
        postings = [item for item in (record.get("active_job_postings") or []) if isinstance(item, dict)]
        titles = [str(item["title"]) for item in postings if item.get("title")]
        context = str(record.get("description") or record.get("posting_context") or "").strip()
        if not context:
            context = "; ".join(str(item["posting_context"]) for item in postings if item.get("posting_context"))
        urls = [str(record[field]) for field in ("posting_url", "website") if record.get(field)]
        components = {
            "source_context": 30 if context else 0,
            "observed_roles": 30 if titles else 0,
            "posting_source": 20 if record.get("posting_url") else 0,
            "source_attribution": 15 if record.get("discovery_source") else 0,
            "website": 5 if record.get("website") else 0,
        }
        score = sum(components.values())
        summary = context or ("Observed roles: " + ", ".join(titles) if titles else "Insufficient source context.")
        record.update({
            "stage": STAGE_ENRICHED,
            "company_summary": summary,
            "what_they_do": str(record.get("description") or "Not established by supplied evidence."),
            "icp_status": "candidate" if context and score >= 40 else "needs_review",
            "priority_score": score,
            "priority_tier": "High" if score >= 80 else "Medium" if score >= 40 else "Low",
            "score_components": components,
            "scoring_method": "evidence_completeness_v1",
            "signal_reasoning": "Priority reflects supplied evidence completeness, not buying intent.",
            "claims_used": summary,
            "source_urls_used": "\n".join(dict.fromkeys(urls)),
        })
        results["enriched"] += 1
    return results


def run_stage4(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {"stage": "Stage 4", "fetched": 0, "drafted": 0, "skipped_approved": 0, "errors": []}
    for record in records:
        if record.get("stage") != STAGE_ENRICHED:
            continue
        results["fetched"] += 1
        if record.get("draft_status") == DRAFT_APPROVED:
            results["skipped_approved"] += 1
            continue
        if record.get("draft_status") in {DRAFT_NEEDS_REVIEW, DRAFT_REJECTED}:
            continue
        if record.get("icp_status") != "candidate":
            continue
        record.update(
            {
                "subject_line_1": f"{record['company_name']} hiring signal",
                "subject_line_2": "Quick note on technical hiring",
                "email_draft": (
                    f"Hi team,\n\nI found this source context for {record['company_name']}: "
                    f"{record['claims_used']}\n\n"
                    "Is recruiting support relevant to your current plans?\n\nBest,"
                ),
                "draft_status": DRAFT_READY,
                "stage": STAGE_DRAFT_READY,
                "crm_sync_status": CRM_NOT_READY,
                "draft_method": "evidence_template",
            }
        )
        results["drafted"] += 1
    return results


def run_stage5(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {"stage": "Stage 5", "ready": 0, "payloads_built": 0, "held": 0, "errors": []}
    for record in records:
        if is_stage5_crm_ready(record):
            results["ready"] += 1
            build_stage5_crm_payload(record)
            results["payloads_built"] += 1
        else:
            results["held"] += 1
    return results


def run_demo(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    records = load_sample_records() if records is None else records
    summaries = [
        run_stage1(records),
        run_stage2(records),
        run_stage3(records),
        run_stage4(records),
        run_stage5(records),
    ]
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run",
        "implementation": "offline_rules_and_templates",
        "model_inference": False,
        "stage_summaries": summaries,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Public-safe five-stage pipeline demo")
    parser.add_argument("--dry-run", action="store_true", required=True, help="Required; no live integrations exist")
    parser.add_argument("--input", type=Path, help="Optional local review-state JSON; defaults to synthetic examples.")
    args = parser.parse_args()
    if not args.dry_run:
        raise SystemExit("Only --dry-run is supported in the public showcase.")
    records = json.loads(args.input.read_text()) if args.input else None
    if records is not None and (not isinstance(records, list) or any(not isinstance(item, dict) for item in records)):
        parser.error("input must be a list of record objects")
    print(json.dumps(run_demo(records), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

