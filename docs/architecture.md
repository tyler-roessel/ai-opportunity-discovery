# Architecture

This public architecture is generalized from the private implementation. It keeps the real system shape while replacing private tools, identifiers, and data with safe labels.

## System Ownership

| Layer | Public-safe name | Responsibility |
|---|---|---|
| Discovery sources | Vertical sources | Startup/job/source inputs that introduce possible companies. |
| Review/state layer | Review table | Human review, workflow state, draft status, and sync status. |
| AI orchestration | Stage pipelines | Enrichment, scoring, drafting, evidence preservation, and result summaries. |
| Workflow automation | Automation workflow | CRM handoff after approval. |
| CRM | CRM system | Downstream relationship record and operating queue. |

## Data Flow

```text
Terminal run parameters
  -> source-provider request
  -> source results
Stage 1: source-aware discovery
  -> Review table: discovered
Stage 2: identity review
  -> Review table: identity_confirmed / needs_review / rejected
Stage 3: enrichment and scoring
  -> Review table: enriched
Stage 4: drafting
  -> Review table: Draft Ready / Needs Review / Approved
Stage 5: approval and CRM handoff
  -> CRM: synced_to_crm
```

## Code Review Path

The public code is intentionally small enough to inspect quickly:

- `src/showcase/integration_flow.py`
  Maps terminal-style run parameters into a source request, then maps Firecrawl/search/job-source style results into review-table records.
- `src/showcase/pipeline.py`
  Moves fake records through the five-stage state machine.
- `src/showcase/crm_handoff.py`
  Enforces the Stage 5 approval gate before a payload can be built.
- `src/showcase/crm_adapters.py`
  Converts the same approved record into Attio, Salesforce, or HubSpot-style payloads.

This is the core interface design. The public repo does not need live provider credentials to show whether the architecture makes sense.

## Key Design Decisions

### Review Table Owns Workflow State

The review table owns state because it is where humans inspect records, make decisions, and correct the AI. This kept early automation from hiding bad inputs downstream.

### CRM Owns Relationship State

The CRM receives only approved records. It does not own discovery noise, rejected records, or draft experiments.

### AI Pipelines Own Repeatable Judgment

AI handles repeatable work after the workflow defines the input and output contract. That includes enrichment, scoring, evidence extraction, drafting, and payload preparation.

### Automation Owns Handoff

The automation layer moves records only after Stage 5 gates pass. This avoids syncing half-reviewed records just because a draft field exists.

## Failure Handling Patterns

- Dry-run before live writes.
- Limit live runs during first execution.
- Target reruns by company or record ID.
- Skip already-approved drafts.
- Preserve review-needed status during draft reruns.
- Separate scrape, LLM, write, and sync failure counts.
- Keep failed syncs retryable in the review/state layer.

## Evidence Contract

Every stage should emit:

1. the decision it made
2. the evidence used
3. confidence or ambiguity markers
4. enough structured output for the next stage

This is the central architecture lesson. The AI became reliable when each stage stopped forcing the next stage to infer from thin prose.
