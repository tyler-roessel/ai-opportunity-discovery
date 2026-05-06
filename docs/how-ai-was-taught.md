# How The AI Was Taught

This system was taught through operational feedback rather than model fine-tuning. Human review cycles became prompts, schemas, rubrics, validation checks, and workflow gates.

## Teaching Loop

```text
Sandbox run
  -> human review
  -> failure pattern
  -> rule or rubric
  -> prompt/schema/validation update
  -> safer automation
```

## What The Review Cycles Taught

### Source Quality

Early source tests showed that not every scrapeable source should be treated equally. The AI needed to preserve where a record came from and whether the source itself implied a useful signal.

Encoded as:

- discovery source fields
- source type fields
- posting URL preservation
- source-specific parsers
- source-aware vertical wrappers

### Identity Quality

Human review found ambiguous records, job-board artifacts, agencies, public-sector rows, nonprofits, and scaled companies that were technically valid but operationally wrong.

Encoded as:

- Stage 2 identity states
- domain-first dedupe
- rejection categories
- reviewer notes
- confidence and ambiguity markers

### Fit And Scoring

Review cycles showed that a company could be in the right vertical but still not worth pursuing. The AI needed to separate vertical relevance from target fit.

Encoded as:

- Stage 1 relevance checks
- Stage 3 ICP status
- priority score
- priority tier
- signal reasoning
- target-fit defer category

### Evidence Discipline

Draft review showed that AI drafts degrade when they rely on loose summaries instead of exact evidence.

Encoded as:

- evidence contract
- claim sets
- source URLs used
- draftable claims
- draft risks
- no-invention rule

### Automation Boundary

The system became safer when automation was tied to explicit states rather than "record has an email draft."

Encoded as:

- `draft_ready` stage
- approved draft status
- CRM sync status
- minimal CRM payload builder
- retryable sync errors

## Final Lesson

The AI became useful when human judgment became structured input. The private workflow taught the AI what a good opportunity looked like, what a bad match looked like, what evidence mattered, and when the system should stop for review.

