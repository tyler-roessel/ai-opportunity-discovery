# AI Opportunity Discovery System - Public Showcase

This repo is a sanitized public mirror of a private AI workflow. It preserves the real architecture, stage progression, orchestration patterns, and implementation lessons while replacing private business data, credentials, schemas, customer/prospect details, raw prompts, and live integration identifiers with safe examples.

The important story is not "AI found some leads." The system started as sandboxed AI experiments, moved through human-reviewed stages, converted review feedback into rubrics and guardrails, and then moved into full AI automation once the five-stage workflow was reliable.

## What This Demonstrates

- A five-stage AI workflow for discovery, review, enrichment, drafting, and CRM handoff.
- A practical human-in-the-loop path from sandbox scripts to repeatable automation.
- Source-aware discovery with provenance carried into later stages.
- Review gates that prevent weak records or speculative drafts from moving downstream.
- CRM handoff logic that syncs only approved, traceable records.
- Sanitized implementation patterns from the private operating repo.

## The Five-Stage Workflow

| Stage | Purpose | Review/automation role |
|---|---|---|
| Stage 1: Discovery and intake | Source-aware vertical discovery finds plausible companies, dedupes by domain/name, filters obvious bad fits, and writes `discovered` records. | Began as dry-run source testing. Later became repeatable vertical runs with deterministic filters and inserted/updated/error summaries. |
| Stage 2: Human identity review | A reviewer confirms whether the company is real, correctly identified, and worth deeper enrichment. | Human review taught the AI what bad matches, ambiguous identities, and source artifacts looked like. |
| Stage 3: Verification, enrichment, and scoring | AI enriches approved records with website/context evidence, ICP status, priority score, signal reasoning, and source URLs used. | Human feedback became scoring rubrics, evidence contracts, and confidence markers. |
| Stage 4: Drafting, recommendation, and review | AI drafts evidence-grounded outbound notes and records the claims used. | Draft review taught the AI to avoid invented urgency, weak personalization, and unsupported claims. |
| Stage 5: CRM handoff and automation-ready execution | Only approved draft-ready records become CRM handoff payloads. Failed syncs stay retryable. | Full automation happens after the gate is stable: approved records can be routed downstream without exposing unreviewed records. |

Full automation is the maturity state of the five stages, not a sixth stage. The workflow moved toward automation after the human-reviewed process proved stable enough to encode.

## How The AI Was Taught

The private system improved through a simple loop:

1. Run the AI in a sandbox or dry-run mode.
2. Review the results by hand.
3. Identify failure patterns: duplicates, source artifacts, wrong company identity, weak ICP fit, thin evidence, speculative drafts.
4. Convert review decisions into rules: rejection categories, required fields, scoring thresholds, evidence contracts, prompt constraints, and sync gates.
5. Run the next stage with tighter structure.
6. Automate the stage only after its inputs, outputs, and failure modes became predictable.

This is why the repo emphasizes workflow states, evidence preservation, dry-run/live boundaries, and Stage 5 gating. The goal was not to let AI guess. The goal was to teach AI a real operating workflow through repeated review, then automate the workflow once reliable.

## From Sandbox To Full Automation

The original operating pattern was intentionally conservative:

- Stage 1 supported `--dry-run` previews before live writes.
- Stage 2 stayed human-led while identity quality was still the biggest risk.
- Stage 3 and Stage 4 accepted small `--limit` runs and targeted reruns by company or record ID.
- Stage 4 skipped already-approved drafts and preserved `Needs Review` status on reruns.
- Stage 5 required explicit approval before CRM sync.

As the system matured, these manual checks became encoded gates. The public version keeps those gates because they are the proof of engineering judgment.

This system started before direct MCP-style CRM access was installed in my local workflow. I manually coded the review-to-CRM handoff first, then used that implementation as the contract for later AI-assisted automation.

## From Job Search Tooling To Client Discovery

One important implementation path came from forking a job-search workflow, reversing its purpose, and adding business-development automation on top. The original scanner looked for companies hiring for roles I might personally apply to. I realized the same signal had a second commercial use: companies hiring for those roles were also potential clients for my current recruiting contract work.

That changed the system design. Instead of treating hiring data only as a personal application pipeline, I reused the source registry, filtering, dedupe/history, and manual-review patterns as a client-discovery engine. The workflow was not "fully automated" in the sense of blindly acting on every result. It was operator-governed automation: the system could discover, enrich, score, draft, and prepare CRM handoff at scale, while review gates controlled which records moved forward.

The later business workflow took the useful parts of the forked job-search scanner and reversed the objective: instead of asking "should I apply to this company?" it asked "does this company have a live hiring signal that makes it a potential client?" From there, I added enrichment, scoring, drafting, review gates, and CRM handoff automation.

## Architecture And Data Flow

```text
Vertical sources
    |
    v
Stage 1 discovery scripts
    |
    v
Review/state table
    |
    v
Stage 2 identity review
    |
    v
Stage 3 enrichment + scoring
    |
    v
Stage 4 evidence-grounded drafting
    |
    v
Stage 5 approval gate
    |
    v
CRM handoff payload
```

The private workflow used Airtable as the review/state layer, Attio as the downstream CRM layer, n8n-style workflow orchestration for handoff automation, and Python orchestration scripts for discovery, enrichment, scoring, drafting, and sync payload shaping. This public mirror preserves that architecture with fake schemas and placeholder integration values.

## Real Artifacts Preserved

- Five-stage workflow shape and stage names.
- Dry-run/live operator boundary.
- Domain-first dedupe principle with name fallback.
- Stage 1 rejection taxonomy.
- Evidence contract across stages.
- Draft quality rubric and no-invention constraint.
- Stage 5 CRM handoff gate.
- Result summary patterns: fetched, skipped, enriched/drafted, failures, and errors.
- Representative CLI and orchestration code.

## What Was Sanitized

- Real company/prospect/customer data.
- Live Airtable base/table/field IDs.
- Live Attio object/list/field IDs.
- Webhook URLs, API keys, tokens, and credentials.
- Private-company-specific prompts, operating language, and strategy docs.
- Raw generated outputs, logs, and transcript dumps.
- Private commit details and internal file paths.

## How A CTO/Engineer Should Review This Sample

Review this as a public-safe architecture and implementation sample, not a plug-and-play product. The useful questions are:

- Does the workflow preserve state and provenance across stages?
- Are risky transitions gated by review or validation?
- Are dry-run/live boundaries explicit?
- Are generated drafts traceable to evidence?
- Is the CRM handoff minimal and approval-driven?
- Is the sanitized repo honest about what was preserved and what was removed?

The strongest signal is the progression: human judgment became rubrics and contracts, then those contracts became automation.

## Repository Map

- `docs/build-progression.md` - how the five-stage workflow moved from sandbox to full automation.
- `docs/how-ai-was-taught.md` - the feedback loop that turned review decisions into AI behavior.
- `docs/architecture.md` - system architecture and ownership boundaries.
- `docs/implementation-evidence.md` - source-derived implementation evidence preserved in public-safe form.
- `docs/sanitization-notes.md` - what was preserved, generalized, or removed.
- `examples/` - fake schemas, sample records, and before/after stage outputs.
- `workflows/` - sanitized workflow export showing Stage 5 handoff shape.
- `src/showcase/` - representative sanitized Python implementation patterns.

## Safe Local Run

This showcase has no live integrations. It runs only against fake local examples.

```bash
python3 -m pytest
python3 -m src.showcase.pipeline --dry-run
```
