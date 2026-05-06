# Implementation Evidence Preserved

This file records what came from the private implementation shape and how it was made public-safe.

## Source-Derived Architecture Evidence

The private repo contained a canonical source-aware workflow with:

- separate Stage 1 vertical discovery entrypoints
- a shared Stage 1 filter contract
- a review/state table as the workflow state layer
- Stage 3 enrichment and scoring
- Stage 4 draft generation
- Stage 5 CRM handoff documentation
- reusable agent-style context, scraping, enrichment, drafting, and handoff skills
- workflow constants for stage, draft status, and sync status
- tests around field transformation and Stage 5 readiness

This public mirror preserves those implementation ideas in generalized form.

## Source-Derived Operating Patterns

The public code and docs preserve these real patterns:

- forked and reversed job-search scanning patterns for client discovery
- source registry and title-filter concepts adapted from a manual-review job-search funnel
- `--dry-run` before live execution
- small live run limits before broad runs
- targeted reruns by company or record ID
- domain-first dedupe with exact-name fallback only when domain is missing
- rejection taxonomy for hard rejects, source artifacts, relevance misses, and target-fit defers
- separate failure counters for scrape, AI, write, and sync failures
- draft-only email preparation before approval
- protected approved drafts
- preserved review-needed status on draft reruns
- Stage 5 gate requiring approved status before CRM payload creation

## Generalized File/Module Shape

Private implementation pattern:

```text
repo-root stage entrypoints
src/orchestration/
src/verticals/
src/integrations/
src/models/
docs/
tests/
```

Public showcase pattern:

```text
README.md
docs/
examples/
workflows/
src/showcase/
tests/
```

The public version is intentionally smaller. It keeps the reviewable architecture and state-machine behavior without copying private prompts, field IDs, outputs, or live integration code.

## What Was Not Preserved

- raw private prompts
- live integration IDs
- real record data
- live workflow exports
- generated outputs and logs
- private commit history
- private company-specific operating docs

## Why This Is Still Authentic

The public mirror does not fake the architecture. It preserves the real lessons:

- job listings can be interpreted as both personal opportunity signals and client-demand signals
- a forked job-search funnel can become a business-development source engine when the objective is reversed and automation is added on top
- AI output needed staged review before automation.
- Human review taught the system which records to reject, hold, enrich, draft, and sync.
- Evidence had to survive from discovery into drafting.
- CRM handoff needed approval gates, not a loose "draft exists" trigger.
- Full automation became credible only after those gates stabilized.
