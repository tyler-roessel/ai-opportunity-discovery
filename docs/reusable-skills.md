# Reusable Skills

The private workflow was not just one automation. It was a set of reusable skills connected by state, evidence, and review gates. This public version documents those skills without exposing private prompts, live credentials, or record data.

## Skill Map

| Skill | Input | Output | Why it mattered |
|---|---|---|---|
| Context intake | Raw company names, job postings, source URLs, notes, or scraped snippets. | A normalized review record with source context and ambiguity preserved. | It turned messy context into something a human and later AI stages could evaluate. |
| Source scraping | Public job boards, company pages, portfolio boards, and search-derived sources. | Structured source evidence: company identity, posting URL, active roles, source name, source type. | It made discovery repeatable and traceable instead of relying on manual browsing. |
| Identity review assist | A discovered record plus source evidence. | `identity_confirmed`, `needs_review`, or `rejected`, with confidence and reasoning. | It kept bad identities from contaminating enrichment and drafting. |
| Enrichment | Confirmed company identity, website, posting evidence, and vertical context. | Summary, what-they-do field, ICP status, priority score, signal reasoning, claims, and source URLs used. | It taught the AI to produce structured judgment rather than loose prose. |
| Draft preparation | Enriched record, claims, source URLs, and vertical-specific context. | Subject lines, draft email body, claims used, source URLs used, and draft risk markers. | It made email work evidence-grounded and reviewable. |
| Handoff validation | Approved draft-ready record. | Minimal CRM payload and sync status update. | It separated review-state data from downstream relationship data. |

## Context Intake

The context-intake skill handled imperfect inputs: partial company names, job links, source names, profile pages, and rough notes. The important behavior was to preserve uncertainty instead of hiding it.

Public-safe output shape:

```json
{
  "company_name": "Northstar Agents",
  "website": "https://example-northstar-agents.test",
  "source_name": "portfolio_job_board",
  "posting_url": "https://jobs.example.test/northstar-agents/platform-engineer",
  "identity_risks": ["new company", "limited public context"],
  "needs_human_review": true
}
```

## Scraping And Source Discovery

The scraping skill collected source evidence and kept provenance attached to the record. It was useful for both the original job-search flow and the reversed client-discovery flow.

Public-safe output shape:

```json
{
  "discovery_source": "curated_job_source",
  "discovery_source_type": "startup_job_board",
  "source_query_context": "AI platform roles",
  "active_job_postings": [
    {
      "title": "Platform Engineer",
      "department": "Engineering",
      "source_url": "https://jobs.example.test/northstar-agents/platform-engineer",
      "posting_context": "agent runtime infrastructure"
    }
  ]
}
```

## Enrichment

The enrichment skill ran after identity review. That sequencing mattered because enrichment can make bad data look more convincing if it runs too early.

Public-safe output shape:

```json
{
  "company_summary": "Northstar Agents builds infrastructure for AI agent workflows.",
  "icp_status": "target",
  "priority_score": 78,
  "priority_tier": "Warm",
  "signal_reasoning": "Hiring signal suggests infrastructure and product expansion.",
  "claims_used": "Role evidence and public product context.",
  "source_urls_used": "https://example-northstar-agents.test/careers"
}
```

## Email Draft Preparation

The email skill was a draft-preparation skill, not a send engine. It produced subject lines and draft copy from evidence that had already been reviewed and enriched.

The boundary was intentional:

- do not draft from unconfirmed identities
- do not invent urgency
- do not overwrite approved drafts
- preserve claims used and source URLs
- require human approval before downstream handoff or sending

Public-safe output shape:

```json
{
  "subject_line_1": "Northstar Agents platform hiring",
  "subject_line_2": "Agent infrastructure team growth",
  "email_draft": "Hi team,\n\nNoticed the public hiring signal around agent runtime infrastructure...",
  "claims_used": "Hiring for platform engineering; public product context references agent workflows.",
  "draft_status": "Draft Ready"
}
```

## Handoff Validation

The handoff skill converted approved records into a minimal CRM payload. It did not send every enriched record downstream.

Required gate:

```text
Stage = draft_ready
Draft Status = Approved
CRM Sync Status = Not Ready
Email Draft is present
Source URLs Used is present
```

This made the workflow partially automated and fully governed: repeatable work could run automatically, while risky movement between systems stayed tied to explicit state.

