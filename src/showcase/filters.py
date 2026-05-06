"""Representative Stage 1 filtering patterns from the private workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


REASON_HARD_REJECT = "hard_reject"
REASON_SOURCE_ARTIFACT = "source_artifact"
REASON_VERTICAL_RELEVANCE_MISS = "vertical_relevance_miss"
REASON_TARGET_FIT_DEFER = "target_fit_defer"

NON_CANONICAL_DOMAINS = {
    "greenhouse.io",
    "jobs.lever.co",
    "ashbyhq.com",
    "workdayjobs.com",
}

AGENCY_KEYWORDS = {
    "staffing",
    "recruitment agency",
    "recruiting firm",
    "headhunter",
    "outsourcing",
}

PUBLIC_SECTOR_KEYWORDS = {
    "city of ",
    "state of ",
    "county of ",
    "department of ",
    "university",
    "school district",
    "nonprofit",
    "foundation",
}

VERTICAL_SIGNALS = {
    "AI": {"agent", "model", "inference", "ai platform", "machine learning", "copilot"},
    "FinTech": {"payments", "ledger", "risk", "compliance", "banking", "card issuing"},
    "SaaS": {"workflow", "crm", "customer onboarding", "product analytics", "automation"},
    "Blockchain": {"wallet", "protocol", "onchain", "smart contract", "defi", "crypto"},
}


@dataclass(frozen=True)
class Stage1Decision:
    passed: bool
    category: str
    reason: str


def normalize_domain(url_or_domain: str) -> str:
    if not url_or_domain:
        return ""
    cleaned = str(url_or_domain).strip().lower()
    parsed = urlparse(cleaned if "://" in cleaned else f"https://{cleaned}")
    return (parsed.netloc or parsed.path).removeprefix("www.").rstrip("/")


def build_searchable_text(record: dict[str, Any]) -> str:
    parts = [
        record.get("company_name"),
        record.get("description"),
        record.get("role_title"),
        record.get("posting_context"),
        record.get("discovery_source"),
    ]
    postings = record.get("active_job_postings") or []
    for posting in postings:
        if isinstance(posting, dict):
            parts.extend([posting.get("title"), posting.get("department"), posting.get("posting_context")])
    return " ".join(str(part).lower() for part in parts if part)


def evaluate_stage1_record(record: dict[str, Any]) -> Stage1Decision:
    name = str(record.get("company_name") or "").strip()
    website = str(record.get("website") or "").strip()
    posting_url = str(record.get("posting_url") or "").strip()
    vertical = str(record.get("vertical") or "").strip()
    searchable = build_searchable_text(record)
    domain = normalize_domain(website)
    posting_domain = normalize_domain(posting_url)

    if not name:
        return Stage1Decision(False, REASON_HARD_REJECT, "missing company name")
    if len(name) <= 2:
        return Stage1Decision(False, REASON_HARD_REJECT, "ambiguous short name")
    if domain in NON_CANONICAL_DOMAINS and not posting_domain:
        return Stage1Decision(False, REASON_SOURCE_ARTIFACT, "job-board domain is not a canonical company website")
    if any(keyword in searchable for keyword in AGENCY_KEYWORDS):
        return Stage1Decision(False, REASON_HARD_REJECT, "agency or staffing artifact")
    if any(keyword in searchable for keyword in PUBLIC_SECTOR_KEYWORDS):
        return Stage1Decision(False, REASON_HARD_REJECT, "public-sector, education, or nonprofit artifact")

    signals = VERTICAL_SIGNALS.get(vertical, set())
    if signals and any(signal in searchable for signal in signals):
        return Stage1Decision(True, "passed", f"{vertical} relevance signal found")

    return Stage1Decision(
        False,
        REASON_VERTICAL_RELEVANCE_MISS,
        f"no {vertical or 'target'} relevance signal found",
    )

