"""Public-safe workflow state constants.

These mirror the private system's state model with CRM-specific labels
generalized for public review.
"""

STAGE_DISCOVERED = "discovered"
STAGE_IDENTITY_CONFIRMED = "identity_confirmed"
STAGE_NEEDS_REVIEW = "needs_review"
STAGE_REJECTED = "rejected"
STAGE_ENRICHED = "enriched"
STAGE_DRAFT_READY = "draft_ready"
STAGE_SYNCED_TO_CRM = "synced_to_crm"

DRAFT_NOT_STARTED = "Not Started"
DRAFT_READY = "Draft Ready"
DRAFT_NEEDS_REVIEW = "Needs Review"
DRAFT_REJECTED = "Rejected"
DRAFT_APPROVED = "Approved"

CRM_NOT_READY = "Not Ready"
CRM_SYNCED = "Synced"
CRM_SYNCED_ERROR = "Synced Error"

VALID_STAGE_VALUES = {
    STAGE_DISCOVERED,
    STAGE_IDENTITY_CONFIRMED,
    STAGE_NEEDS_REVIEW,
    STAGE_REJECTED,
    STAGE_ENRICHED,
    STAGE_DRAFT_READY,
    STAGE_SYNCED_TO_CRM,
}

VALID_DRAFT_STATUS_VALUES = {
    DRAFT_NOT_STARTED,
    DRAFT_READY,
    DRAFT_NEEDS_REVIEW,
    DRAFT_REJECTED,
    DRAFT_APPROVED,
}

VALID_CRM_SYNC_VALUES = {
    CRM_NOT_READY,
    CRM_SYNCED,
    CRM_SYNCED_ERROR,
}

CRM_PAYLOAD_FIELD_MAP = {
    "company_name": "name",
    "website": "website",
    "vertical": "vertical",
    "posting_url": "posting_url",
    "linkedin_company_url": "linkedin_company_url",
    "what_they_do": "what_they_do",
    "company_summary": "company_summary",
    "priority_score": "priority_score",
    "priority_tier": "priority_tier",
    "icp_status": "icp_status",
    "signal_reasoning": "signal_reasoning",
    "subject_line_1": "subject_line_1",
    "subject_line_2": "subject_line_2",
    "email_draft": "email_draft",
    "claims_used": "claims_used",
    "source_urls_used": "source_urls_used",
}

