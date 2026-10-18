from copy import deepcopy

import pytest

from src.showcase.crm_handoff import approve_draft, is_stage5_crm_ready
from src.showcase.pipeline import run_demo, run_stage1, run_stage2, run_stage3, run_stage4, run_stage5
from src.showcase.identity_review import approve_identity


def draft():
    record = {
        "company_name": "Example", "website": "https://example.test",
        "stage": "draft_ready", "draft_status": "Draft Ready", "crm_sync_status": "Not Ready",
        "company_summary": "Source describes workflow tooling.", "icp_status": "candidate",
        "priority_score": 70, "subject_line_1": "Example source",
        "email_draft": "Source-grounded draft.", "source_urls_used": "https://example.test/careers",
    }
    approve_identity(record, reviewer="fixture-reviewer")
    return record


def test_stage5_does_not_approve_or_mutate_unreviewed_drafts():
    record = draft()
    before = deepcopy(record)
    result = run_stage5([record])
    assert result["payloads_built"] == 0
    assert record == before


def test_explicit_review_allows_handoff_and_failed_sync_remains_retryable():
    record = draft()
    approve_draft(record, reviewer="fixture-reviewer")
    assert run_stage5([record])["payloads_built"] == 1
    record["crm_sync_status"] = "Synced Error"
    assert is_stage5_crm_ready(record)
    record["crm_sync_status"] = "Synced"
    assert not is_stage5_crm_ready(record)


@pytest.mark.parametrize("field,value", [
    ("email_draft", "Changed draft"), ("company_summary", "Changed evidence"),
    ("source_urls_used", "https://other.test"), ("priority_score", 99),
])
def test_approval_is_invalidated_when_reviewed_content_changes(field, value):
    record = draft()
    approve_draft(record, reviewer="fixture-reviewer")
    record[field] = value
    assert not is_stage5_crm_ready(record)


@pytest.mark.parametrize("field,value", [
    ("priority_score", True), ("priority_score", float("nan")),
    ("priority_score", -1), ("priority_score", "high"),
    ("source_urls_used", []), ("website", "file:///tmp/example"),
    ("website", "https://[invalid"),
    ("company_summary", ""), ("icp_status", "needs_review"),
])
def test_invalid_context_cannot_be_approved(field, value):
    record = draft()
    record[field] = value
    with pytest.raises(ValueError, match="incomplete or invalid"):
        approve_draft(record, reviewer="fixture-reviewer")


def test_identity_requires_an_explicit_review_and_can_resume_from_hold():
    record = {"company_name": "Example", "website": "https://example.test", "stage": "discovered"}
    run_stage2([record])
    assert record["stage"] == "needs_review"
    approve_identity(record, reviewer="fixture-reviewer")
    run_stage2([record])
    assert record["stage"] == "identity_confirmed"


def test_invalid_identity_url_stays_in_review():
    record = {
        "stage": "discovered", "website": "https://[invalid",
        "identity_review_status": "Approved", "identity_reviewed_by": "fixture-reviewer",
    }
    run_stage2([record])
    assert record["stage"] == "needs_review"


def test_rejected_discovery_does_not_proceed():
    record = {
        "company_name": "Staffing Agency", "website": "https://example.test",
        "description": "Recruitment agency", "stage": "discovered",
    }
    run_stage1([record])
    run_stage2([record])
    assert record["stage"] == "rejected"


def test_scoring_uses_available_evidence_and_thin_records_do_not_get_drafts():
    thin = {"company_name": "Thin", "website": "https://thin.test", "stage": "identity_confirmed"}
    rich = {
        "company_name": "Rich", "website": "https://rich.test", "stage": "identity_confirmed",
        "posting_url": "https://rich.test/jobs", "discovery_source": "fixture",
        "description": "Builds workflow software.",
        "active_job_postings": [{"title": "Engineer"}],
    }
    approve_identity(thin, reviewer="fixture-reviewer")
    approve_identity(rich, reviewer="fixture-reviewer")
    run_stage3([thin, rich])
    assert thin["priority_score"] < rich["priority_score"]
    assert rich["priority_score"] == sum(rich["score_components"].values())
    assert rich["company_summary"] == rich["description"]
    run_stage4([thin, rich])
    assert "email_draft" not in thin
    assert rich["draft_status"] == "Draft Ready"
    assert not is_stage5_crm_ready(rich)


@pytest.mark.parametrize("status", ["Approved", "Needs Review", "Rejected"])
def test_drafting_reruns_preserve_review_decisions(status):
    record = draft()
    record.update(stage="enriched", draft_status=status, email_draft="Keep reviewer work")
    run_stage4([record])
    assert record["email_draft"] == "Keep reviewer work"
    assert record["draft_status"] == status


def test_end_to_end_run_preserves_existing_approved_state_on_rerun():
    first = run_demo()
    second = run_demo(deepcopy(first["records"]))
    assert first["records"] == second["records"]
    assert first["model_inference"] is False
    assert first["stage_summaries"][-1]["payloads_built"] == 1


def test_complete_source_to_review_to_handoff_flow():
    record = {
        "company_name": "Example", "website": "https://example.test", "vertical": "AI",
        "description": "Builds agent software.", "posting_url": "https://example.test/jobs",
        "identity_review_status": "Approved", "identity_reviewed_by": "fixture-reviewer",
        "active_job_postings": [{"title": "Engineer"}], "discovery_source": "fixture",
    }
    approve_identity(record, reviewer="fixture-reviewer")
    run_stage1([record])
    run_stage2([record])
    run_stage3([record])
    run_stage4([record])
    assert run_stage5([record])["held"] == 1
    approve_draft(record, reviewer="fixture-reviewer")
    assert run_stage5([record])["payloads_built"] == 1


def test_filter_errors_do_not_inherit_identity_approval():
    record = {
        "company_name": "Example", "website": "https://example.test", "stage": "discovered",
        "active_job_postings": 42, "identity_review_status": "Approved",
        "identity_reviewed_by": "fixture-reviewer",
    }
    assert run_stage1([record])["errors"]
    run_stage2([record])
    assert record["stage"] == "needs_review"


def test_persisted_confirmed_state_without_review_is_held():
    record = {"company_name": "Example", "website": "https://example.test", "stage": "identity_confirmed"}
    assert run_stage3([record])["validation_failures"] == 1
    assert record["stage"] == "needs_review"


def test_changed_identity_invalidates_the_review():
    record = draft()
    record.update(stage="discovered", website="https://changed.test")
    run_stage2([record])
    assert record["stage"] == "needs_review"


def test_per_posting_evidence_retains_its_source_and_uses_neutral_subjects():
    record = {
        "company_name": "Example", "website": "https://example.test", "stage": "identity_confirmed",
        "discovery_source": "fixture", "active_job_postings": [
            {"title": "Engineer", "posting_context": "Build agent software.", "source_url": "https://jobs.test/one"},
        ],
    }
    approve_identity(record, reviewer="fixture-reviewer")
    run_stage3([record])
    assert "https://jobs.test/one" in record["source_urls_used"]
    run_stage4([record])
    assert "hiring signal" not in record["subject_line_1"]


def test_malformed_postings_are_held_without_aborting_other_records():
    bad = {"company_name": "Bad", "website": "https://bad.test", "stage": "identity_confirmed", "active_job_postings": 42}
    good = {"company_name": "Good", "website": "https://good.test", "stage": "identity_confirmed"}
    for record in (bad, good):
        approve_identity(record, reviewer="fixture-reviewer")
    summary = run_stage3([bad, good])
    assert summary["validation_failures"] == 1
    assert summary["enriched"] == 1
