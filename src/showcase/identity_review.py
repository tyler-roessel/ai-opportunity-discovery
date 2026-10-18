"""Explicit local identity-review assertions bound to company facts."""

import hashlib
import json
from urllib.parse import urlparse


def identity_fingerprint(record):
    content = {key: record.get(key) for key in ("company_name", "website")}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def valid_identity(record):
    if not isinstance(record.get("company_name"), str) or not record["company_name"].strip():
        return False
    if not isinstance(record.get("website"), str):
        return False
    try:
        url = urlparse(record["website"])
        return url.scheme in {"http", "https"} and bool(url.hostname)
    except ValueError:
        return False


def has_identity_review(record):
    return (
        valid_identity(record)
        and record.get("identity_review_status") == "Approved"
        and isinstance(record.get("identity_reviewed_by"), str)
        and bool(record["identity_reviewed_by"].strip())
        and record.get("identity_approval_fingerprint") == identity_fingerprint(record)
    )


def approve_identity(record, *, reviewer):
    if not isinstance(reviewer, str) or not reviewer.strip() or not valid_identity(record):
        raise ValueError("a valid identity and reviewer are required")
    record["identity_review_status"] = "Approved"
    record["identity_reviewed_by"] = reviewer.strip()
    record["identity_approval_fingerprint"] = identity_fingerprint(record)
