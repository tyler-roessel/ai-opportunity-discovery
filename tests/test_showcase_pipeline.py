from src.showcase.crm_handoff import build_stage5_crm_payload, is_stage5_crm_ready
from src.showcase.filters import evaluate_stage1_record
from src.showcase.pipeline import run_demo
from src.showcase.states import CRM_NOT_READY, DRAFT_APPROVED, STAGE_DRAFT_READY


def test_stage1_passes_plausible_source_aware_ai_record():
    record = {
        "company_name": "Northstar Agents",
        "website": "https://example-northstar-agents.test",
        "vertical": "AI",
        "role_title": "Platform Engineer",
        "posting_context": "Hiring for agent runtime infrastructure",
    }

    decision = evaluate_stage1_record(record)

    assert decision.passed is True
    assert decision.category == "passed"


def test_stage1_rejects_staffing_artifact():
    record = {
        "company_name": "Demo Staffing Group",
        "website": "https://example-staffing.test",
        "vertical": "SaaS",
        "description": "Recruitment agency for software teams",
    }

    decision = evaluate_stage1_record(record)

    assert decision.passed is False
    assert decision.category == "hard_reject"


def test_stage5_payload_requires_approval_gate():
    record = {
        "company_name": "WorkflowHarbor",
        "website": "https://example-workflowharbor.test",
        "stage": STAGE_DRAFT_READY,
        "draft_status": DRAFT_APPROVED,
        "crm_sync_status": CRM_NOT_READY,
        "company_summary": "Demo summary",
        "icp_status": "target",
        "priority_score": 82,
        "subject_line_1": "WorkflowHarbor hiring",
        "email_draft": "Public-safe demo draft",
        "source_urls_used": "https://example-workflowharbor.test",
    }

    assert is_stage5_crm_ready(record) is True
    payload = build_stage5_crm_payload(record)
    assert payload["name"] == "WorkflowHarbor"
    assert "crm_sync_status" not in payload


def test_demo_runs_all_five_stages():
    result = run_demo()

    assert result["mode"] == "dry_run"
    assert [summary["stage"] for summary in result["stage_summaries"]] == [
        "Stage 1",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "Stage 5",
    ]

