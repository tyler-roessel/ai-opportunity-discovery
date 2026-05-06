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

from .crm_handoff import build_stage5_crm_payload, is_stage5_crm_ready
from .filters import evaluate_stage1_record
from .states import (
    CRM_NOT_READY,
    DRAFT_APPROVED,
    DRAFT_READY,
    STAGE_DISCOVERED,
    STAGE_DRAFT_READY,
    STAGE_ENRICHED,
    STAGE_IDENTITY_CONFIRMED,
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
        try:
            decision = evaluate_stage1_record(record)
            record["stage1_filter_decision"] = "passed" if decision.passed else "rejected"
            record["stage1_filter_reason"] = decision.reason
            if decision.passed:
                record["stage"] = STAGE_DISCOVERED
                results["passed"] += 1
            else:
                results["rejected"] += 1
        except Exception as exc:
            results["errors"].append({"company": record.get("company_name", "?"), "error": str(exc)})
    return results


def run_stage2(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {"stage": "Stage 2", "reviewed": 0, "identity_confirmed": 0, "needs_review": 0}
    for record in records:
        if record.get("stage") != STAGE_DISCOVERED:
            continue
        results["reviewed"] += 1
        if record.get("website"):
            record["stage"] = STAGE_IDENTITY_CONFIRMED
            record["identity_confidence"] = "HIGH"
            record["identity_reasoning"] = "Demo rule: website and source context are present."
            results["identity_confirmed"] += 1
        else:
            record["stage"] = "needs_review"
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
        record.update(
            {
                "stage": STAGE_ENRICHED,
                "company_summary": f"{record['company_name']} is a demo {record.get('vertical', 'technology')} company.",
                "what_they_do": "Public-safe placeholder description generated from fake source evidence.",
                "icp_status": "target",
                "priority_score": 78,
                "priority_tier": "Warm",
                "signal_reasoning": "Fake role and source evidence indicate a plausible hiring or growth signal.",
                "claims_used": "Fake source evidence only.",
                "source_urls_used": record.get("posting_url") or record.get("website"),
            }
        )
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
        record.update(
            {
                "subject_line_1": f"{record['company_name']} hiring signal",
                "subject_line_2": "Quick note on technical hiring",
                "email_draft": (
                    f"Hi team,\n\nNoticed {record['company_name']} has public signals that suggest "
                    "growth in a technical function. Open to a short note on where specialized "
                    "recruiting support could help?\n\nBest,"
                ),
                "draft_status": DRAFT_READY,
            }
        )
        results["drafted"] += 1
    return results


def run_stage5(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = {"stage": "Stage 5", "ready": 0, "payloads_built": 0, "held": 0, "errors": []}
    for record in records:
        if record.get("stage") == STAGE_ENRICHED and record.get("draft_status") == DRAFT_READY:
            record["stage"] = STAGE_DRAFT_READY
            record["draft_status"] = DRAFT_APPROVED
            record["crm_sync_status"] = CRM_NOT_READY
        if is_stage5_crm_ready(record):
            results["ready"] += 1
            build_stage5_crm_payload(record)
            results["payloads_built"] += 1
        else:
            results["held"] += 1
    return results


def run_demo() -> dict[str, Any]:
    records = load_sample_records()
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
        "stage_summaries": summaries,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Public-safe five-stage pipeline demo")
    parser.add_argument("--dry-run", action="store_true", required=True, help="Required; no live integrations exist")
    args = parser.parse_args()
    if not args.dry_run:
        raise SystemExit("Only --dry-run is supported in the public showcase.")
    print(json.dumps(run_demo(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

