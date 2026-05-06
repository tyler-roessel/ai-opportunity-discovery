# Build Progression: Sandbox To Full AI Automation

This document preserves the real progression of the private system without exposing private records, field IDs, credentials, prompts, or customer/prospect data.

## The Core Arc

The system was not designed as full automation on day one. It moved through five stages of increasing structure:

1. Sandbox discovery and source testing.
2. Human review of identity and fit.
3. AI-assisted enrichment and scoring.
4. AI-assisted drafting with review.
5. CRM handoff after approval.

After those five stages stabilized, the workflow could be automated end-to-end because the human review decisions had been converted into system logic.

## Origin: Reversing The Job Search Workflow

Before this became a client-discovery system, the underlying idea came from a forked job-search workflow. The earlier workflow scanned companies hiring for roles I might personally apply to and turned those listings into a manual-review shortlist.

The useful realization was that the same hiring signal had two sides:

- as a candidate, it surfaced companies worth applying to
- as a recruiting operator, it surfaced companies that might need hiring help

That reversed the original purpose of the scanner. Instead of only asking whether a company was worth applying to, the new workflow asked whether the company's hiring activity made it a potential client. The source registry, title filtering, dedupe/history, batch scanning, and manual-review shortlist became reusable architecture. The later workflow added enrichment, scoring, drafting, review gates, and CRM handoff on top of that reversed job-search foundation.

This is also why the automation style is intentionally governed. The system can automate the repeatable work, but it still preserves review states because the goal is not blind execution. The goal is to convert hiring signals into reviewed commercial opportunities.

## Stage 1: Discovery And Intake

Early versions tested whether AI and source-specific scrapers could find plausible companies at all. The useful lesson was that generic sourcing creates too much noise. The architecture moved toward source-aware vertical discovery:

- separate entrypoints for AI, FinTech, SaaS, and Blockchain
- startup-native and job-source inputs
- domain-first dedupe with name fallback
- deterministic rejection categories
- dry-run previews before live writes
- inserted, updated, skipped, rejected, and error summaries

Human realization: the AI needed clear intake boundaries. Stage 1 should answer, "Is this plausible enough to review?" not "Should this become an outbound target?"

## Stage 2: Human Identity Review

The first high-risk failure mode was identity quality. A company could look interesting but still be the wrong entity, a job-board artifact, an agency, a public-sector entity, a scaled company, or an ambiguous short-name match.

Stage 2 stayed human-led while those failure patterns were being learned. Review outcomes became structured states:

- `identity_confirmed`
- `needs_review`
- `rejected`

Human realization: identity confidence had to become an explicit field, not a hidden assumption. This is where the AI was taught what "real company, correct identity, worth enriching" meant.

## Stage 3: Verification, Enrichment, And Scoring

Once identity was confirmed, the AI could safely enrich and score the record. The private implementation used website/context scraping, evidence extraction, ICP interpretation, and score fields.

The important engineering shift was evidence preservation. Stage 3 was not allowed to collapse everything into one summary. It needed to emit:

- company summary
- what the company does
- ICP status
- priority score and priority tier
- signal reasoning
- claims used
- source URLs used
- confidence and ambiguity markers

Human realization: downstream drafting improves only when Stage 3 passes structured evidence, not just prose.

## Stage 4: Drafting, Recommendation, And Review

Stage 4 generated draft outreach, but the draft had to stay tied to evidence. Review feedback taught the AI to avoid:

- invented urgency
- unsupported claims
- over-polished outbound copy
- drafts that ignored the actual hiring or product signal
- rewriting already-approved drafts

The mature behavior kept approved drafts protected, preserved `Needs Review` status on reruns, and used a lightweight rubric before marking a draft ready.

Human realization: the draft is not the decision. The draft is an evidence-backed recommendation that must survive review before CRM handoff.

## Stage 5: CRM Handoff And Automation-Ready Execution

Stage 5 became the automation boundary. The handoff required:

- `Stage = draft_ready`
- `Draft Status = Approved`
- `CRM Sync Status = Not Ready`
- non-empty draft
- enough supporting identity, signal, and source fields to make the CRM record useful

Failed syncs stayed retryable instead of pretending the handoff succeeded.

Human realization: automation should happen at the handoff only after record quality, draft quality, and approval status are explicit.

## Full Automation After Stabilization

The final operating state was not "skip humans." It was "automate the repeatable work after human judgment has been encoded." The stable workflow could run the five-stage progression with AI handling discovery assistance, enrichment, scoring, drafting, routing, and CRM payload preparation while preserving approval gates for high-risk decisions.

That progression is the main public proof point: sandbox output became reviewed output, reviewed output became rubrics, rubrics became validation gates, and validation gates enabled full AI automation.
