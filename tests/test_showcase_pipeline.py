from src.showcase.crm_handoff import build_stage5_crm_payload, is_stage5_crm_ready
from src.showcase.filters import evaluate_stage1_record
from src.showcase.pipeline import run_demo
from src.showcase.states import CRM_NOT_READY, DRAFT_APPROVED, STAGE_DRAFT_READY


def test_terminal_parameters_map_to_source_client_request():
    from src.showcase.integration_flow import build_source_request

    request = build_source_request(
        vertical="AI",
        source_provider="firecrawl",
        query="agent infrastructure hiring",
        limit=25,
    )

    assert request == {
        "provider": "firecrawl",
        "vertical": "AI",
        "query": "agent infrastructure hiring",
        "limit": 25,
        "mode": "dry_run",
    }


def test_raw_source_result_maps_to_review_table_record():
    from src.showcase.integration_flow import map_source_result_to_review_record

    record = map_source_result_to_review_record(
        {
            "name": "Northstar Agents",
            "url": "https://example-northstar-agents.test",
            "source_url": "https://jobs.example.test/northstar-agents/platform-engineer",
            "job_title": "Platform Engineer",
            "snippet": "Hiring for agent runtime infrastructure",
        },
        vertical="AI",
        discovery_source="firecrawl_search",
    )

    assert record["company_name"] == "Northstar Agents"
    assert record["website"] == "https://example-northstar-agents.test"
    assert record["stage"] == "discovered"
    assert record["discovery_source"] == "firecrawl_search"
    assert record["active_job_postings"][0]["title"] == "Platform Engineer"
    assert record["needs_human_review"] is True


def test_approved_record_maps_to_generic_crm_payloads():
    from src.showcase.crm_adapters import build_crm_payload

    record = {
        "company_name": "WorkflowHarbor",
        "website": "https://example-workflowharbor.test",
        "stage": STAGE_DRAFT_READY,
        "draft_status": DRAFT_APPROVED,
        "crm_sync_status": CRM_NOT_READY,
        "vertical": "SaaS",
        "company_summary": "Workflow automation platform.",
        "icp_status": "target",
        "priority_score": 82,
        "priority_tier": "Fire",
        "subject_line_1": "WorkflowHarbor hiring",
        "email_draft": "Public-safe demo draft",
        "source_urls_used": "https://example-workflowharbor.test/careers",
    }

    attio = build_crm_payload(record, crm="attio")
    salesforce = build_crm_payload(record, crm="salesforce")
    hubspot = build_crm_payload(record, crm="hubspot")

    assert attio["object"] == "companies"
    assert attio["fields"]["name"] == "WorkflowHarbor"
    assert salesforce["object"] == "Account"
    assert salesforce["fields"]["Name"] == "WorkflowHarbor"
    assert hubspot["object"] == "companies"
    assert hubspot["properties"]["name"] == "WorkflowHarbor"


def test_approved_record_maps_to_mcp_tool_call():
    from src.showcase.mcp_adapter import build_mcp_tool_call

    record = {
        "company_name": "WorkflowHarbor",
        "website": "https://example-workflowharbor.test",
        "stage": STAGE_DRAFT_READY,
        "draft_status": DRAFT_APPROVED,
        "crm_sync_status": CRM_NOT_READY,
        "vertical": "SaaS",
        "company_summary": "Workflow automation platform.",
        "icp_status": "target",
        "priority_score": 82,
        "priority_tier": "Fire",
        "subject_line_1": "WorkflowHarbor hiring",
        "email_draft": "Public-safe demo draft",
        "source_urls_used": "https://example-workflowharbor.test/careers",
    }

    call = build_mcp_tool_call(record, server="crm", tool="upsert_company")

    assert call["transport"] == "mcp"
    assert call["server"] == "crm"
    assert call["tool"] == "upsert_company"
    assert call["arguments"]["name"] == "WorkflowHarbor"
    assert call["approval_gate"]["stage"] == STAGE_DRAFT_READY
    assert call["approval_gate"]["draft_status"] == DRAFT_APPROVED


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
