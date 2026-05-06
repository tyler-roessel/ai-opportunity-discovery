# Reusable Skills And Capability Catalog

The private workflow was not just one automation. It was a library of reusable capabilities connected by state, evidence, review gates, and operating boundaries. This public version documents those capabilities without exposing private prompts, live credentials, customer data, field IDs, or internal records.

The first public pass only showed a few of these skills. This expanded catalog is closer to the actual system: source discovery, context intake, scraping, dedupe, identity review, enrichment, scoring, drafting, CRM handoff, reporting, context capture, and safety controls.

## Capability Map

| Capability | What it does | Reusable pattern | Safety boundary |
|---|---|---|---|
| Source registry | Defines which sources are allowed for each vertical or workflow. | Source metadata, source type, query context, parser strategy. | New sources are added through a registry instead of ad hoc scraping. |
| Source scraping | Pulls public company, hiring, and signal evidence from approved sources. | Public pages, job boards, portfolio boards, recruiter-side boards, source-specific parsers. | Preserves source URLs and avoids flattening evidence too early. |
| Job-search reversal | Reuses a job-search scanner as a client-discovery engine. | "Should I apply?" becomes "is this company hiring in a way that signals demand?" | Produces review candidates, not automatic outreach. |
| Context intake | Converts messy context into a structured review record. | Raw names, URLs, notes, snippets, source metadata. | Keeps ambiguity and review flags instead of pretending thin context is complete. |
| Dedupe and history | Prevents repeated records and tracks prior scans. | Domain-first dedupe, exact-name fallback, scan-history style tracking. | Avoids over-deduping when domains are missing or ambiguous. |
| Identity review assist | Checks whether the entity is real and correctly matched. | Identity status, confidence, reasoning, canonical domain. | Runs before enrichment so bad identities do not get amplified. |
| Review queue routing | Moves records into explicit human-review states. | `needs_review`, `rejected`, `identity_confirmed`, draft review states. | Human review remains the gate for ambiguous or risky transitions. |
| Evidence contract | Requires each stage to pass evidence, decision, confidence, and source URLs forward. | Structured claims, source URLs used, risks, confidence markers. | Later stages do not re-infer from a thin prose summary. |
| Enrichment | Adds company summaries, fit signals, and opportunity context. | Website/context scraping, claim extraction, vertical interpretation. | Runs only after identity confirmation. |
| Scoring and prioritization | Turns evidence into priority and fit decisions. | ICP status, priority score, tier, signal reasoning. | Scores explain why a record should move forward. |
| Draft preparation | Produces evidence-grounded subject lines and email drafts. | Claims used, source URLs used, draft angle, draft risk. | Draft-only; no automatic sending. |
| Draft quality review | Checks whether a generated draft is usable. | No invented urgency, no unsupported claims, preserve approved drafts. | Approved drafts are not overwritten by reruns. |
| CRM handoff validation | Builds a minimal downstream payload after approval. | Stage 5 gate, minimal payload, retryable sync status. | Sync only approved records; failed syncs stay retryable. |
| MCP tool-call wrapping | Wraps an approved payload for connector-style execution. | Server, tool name, arguments, approval gate metadata. | MCP does not bypass the Stage 5 gate. |
| Sync reconciliation | Compares review-state records against downstream system state. | Dry-run reports, queue status, candidate counts. | Preview-first before live writes. |
| Structured logging | Records decisions and actions in machine-readable form. | Run ID, action type, input summary, decision, outcome, reviewer. | Logs presence/status, not secrets. |
| Reporting and digesting | Produces operator-ready summaries. | Daily/weekly summaries, exception reports, review packets. | Reports decisions and paths without exposing raw sensitive data. |
| Context filing | Takes answers, notes, or learnings and files them into the smallest correct destination. | Inbox -> canonical note -> status log. | Prevents hidden memory from becoming the source of truth. |
| Secret-safe handoff | Produces setup or review packets without printing secrets. | Present/missing state, placeholders, sanitized examples. | Never echo keys, tokens, or credential-bearing URLs. |
| No-send boundary | Allows drafting and preparation without outbound transmission. | Draft-only states, approval gates, explicit send exclusions. | Sending is not implied by draft generation. |
| Control surface | Lets a human trigger, preview, or review automation from a safer interface. | Dry-run commands, status reports, review queues, phone/chat commands. | Control surfaces are not allowed to bypass gates. |

## How These Skills Fit Together

```text
Source registry
  -> source scraping
  -> context intake
  -> dedupe/history
  -> identity review assist
  -> review queue routing
  -> enrichment
  -> scoring and prioritization
  -> draft preparation
  -> draft quality review
  -> CRM handoff validation
  -> sync reconciliation
  -> reporting and context filing
```

The system is "automated" because repeatable work can run from source discovery through handoff preparation. It is "not fully automated" in the reckless sense because explicit states still decide when a record is allowed to move forward.

## Source Registry

The source registry skill keeps discovery from turning into random scraping. A source has a type, vertical fit, parser expectation, and query context.

Public-safe output shape:

```json
{
  "source_id": "ai_portfolio_jobs",
  "source_type": "portfolio_job_board",
  "vertical": "AI",
  "query_context": "agent infrastructure and platform roles",
  "parser": "job_board_listing_parser",
  "active": true
}
```

## Source Scraping

The scraping skill collects public evidence and keeps provenance attached to the record. It was useful for both the original job-search flow and the reversed client-discovery flow.

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

## Job-Search Reversal

The job-search reversal skill came from forking a job-search workflow and changing the question.

Original question:

```text
Should I apply to this company?
```

Reversed business-development question:

```text
Does this company's hiring activity suggest it may need recruiting or talent support?
```

That reversal reused source discovery, title filters, dedupe/history, and manual-review shortlist logic, then added enrichment, scoring, drafting, and CRM handoff.

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

## Dedupe And History

The dedupe skill prevents repeated work while keeping ambiguity visible.

Public-safe rules:

- use normalized domain as the strongest dedupe key
- use exact-name fallback only when domain is missing
- preserve source provenance on repeated records
- track scan history so repeated runs do not inflate the review queue
- allow scratch runs when the operator intentionally wants to include prior matches

## Identity Review Assist

Identity review turns discovered records into one of three outcomes:

```text
identity_confirmed
needs_review
rejected
```

Public-safe output shape:

```json
{
  "identity_status": "identity_confirmed",
  "identity_confidence": "HIGH",
  "canonical_company_name": "Northstar Agents",
  "canonical_domain": "example-northstar-agents.test",
  "identity_reasoning": "Website, posting source, and company profile align.",
  "identity_risks": []
}
```

## Evidence Contract

The evidence contract makes every stage produce:

1. the decision it made
2. the evidence used
3. confidence or ambiguity markers
4. enough structured output for the next stage

This prevents later AI stages from re-inventing facts from a thin summary.

## Enrichment

The enrichment skill runs after identity review. That sequencing matters because enrichment can make bad data look more convincing if it runs too early.

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

## Scoring And Prioritization

The scoring skill turns evidence into a reviewable priority decision.

Public-safe output shape:

```json
{
  "icp_status": "target",
  "priority_score": 82,
  "priority_tier": "Fire",
  "score_drivers": [
    "multiple active technical roles",
    "clear product surface",
    "source evidence is recent"
  ],
  "score_risks": ["company stage is estimated"]
}
```

## Draft Preparation

The email skill is a draft-preparation skill, not a send engine. It produces subject lines and draft copy from evidence that has already been reviewed and enriched.

The boundary is intentional:

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

## Draft Quality Review

Draft review checks for:

- grounded claims
- clear relationship between signal and outreach angle
- no exaggerated urgency
- no unsupported personalization
- no overwriting approved drafts
- explicit `Needs Review` when the evidence is thin

## Handoff Validation

The handoff skill converts approved records into a minimal CRM payload. It does not send every enriched record downstream.

Required gate:

```text
Stage = draft_ready
Draft Status = Approved
CRM Sync Status = Not Ready
Email Draft is present
Source URLs Used is present
```

## MCP Tool-Call Wrapping

MCP is useful after the workflow contract is defined. In this system, the MCP-style adapter wraps an approved Stage 5 payload as a tool call, but it does not decide whether the record is approved.

Public-safe envelope:

```json
{
  "transport": "mcp",
  "server": "crm",
  "tool": "upsert_company",
  "arguments": {
    "name": "WorkflowHarbor",
    "website": "https://example-workflowharbor.test"
  },
  "approval_gate": {
    "stage": "draft_ready",
    "draft_status": "Approved",
    "crm_sync_status": "Not Ready"
  },
  "mode": "preview"
}
```

The key design point is that MCP is a transport layer over reviewed state, not a shortcut around reviewed state.

## Sync Reconciliation

The sync reconciliation skill checks what would move before anything mutates.

Public-safe report shape:

```json
{
  "eligible_for_sync": 12,
  "held_missing_draft": 3,
  "held_not_approved": 8,
  "retryable_sync_errors": 1,
  "mode": "dry_run"
}
```

## Structured Logging

Structured logs make the system auditable.

Public-safe event shape:

```json
{
  "run_id": "demo-run-001",
  "event_type": "human_decision",
  "record_key": "northstar-agents",
  "decision": "approved_for_handoff",
  "reason": "identity confirmed, evidence-backed draft approved",
  "secret_values_logged": false
}
```

## Reporting And Digesting

Reporting skills turn raw run output into operator summaries:

- records discovered
- records rejected
- records awaiting identity review
- enrichment failures
- drafts ready
- drafts needing review
- records eligible for handoff
- retryable sync errors

The report is meant for action, not vanity metrics.

## Context Filing

Context filing captures lessons from reviews and moves them into the smallest correct source of truth.

Public-safe pattern:

```text
review comment
  -> rule update
  -> doc/rubric update
  -> next run uses the improved contract
```

## Secret-Safe Handoff

The handoff skill creates reusable setup or review packets without printing secrets.

Rules:

- use placeholders in public examples
- report only present/missing for credentials
- strip webhook URLs
- strip live field IDs and record IDs
- avoid raw transcript dumps
- preserve architecture and decisions, not sensitive values

## Control Surface

Control surfaces let the operator trigger or inspect automation without bypassing review gates.

Examples:

- dry-run commands
- status reports
- review queues
- local logs
- chat or phone commands that only preview or queue work

The important rule: a convenient control surface is not permission to skip approval states.
