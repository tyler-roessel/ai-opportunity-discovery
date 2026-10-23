# Implementation status

The runnable sample is offline. Historical architecture documents describe the larger design and do not establish live inference, scraping, sync, or delivery in this public code.

- Discovery rejection is an explicit state. Reruns preserve later workflow states.
- Identity confirmation requires an explicit review decision bound to the company name and website. Persisted confirmed states must supply the same evidence.
- Priority reflects supplied context (30), observed roles (30), posting source (20), source attribution (15), and website (5). Missing context prevents drafting. Per-posting evidence retains its URLs. Subjects use neutral source language. This is evidence completeness, not verified fit or intent.
- Drafting preserves Needs Review and Rejected decisions. Stage 5 cannot approve drafts.
- Approval records the reviewer and a SHA-256 digest of draft and CRM context. Changes invalidate readiness. This detects content changes; it does not establish reviewer identity.
- The Python validator checks field types, score bounds, source URLs, approval, and retry state. It has no external side effects.
- The workflow JSON is a historical diagram. It is not an importable n8n workflow and does not encode the full current validator. Use the tested Python gate rather than the diagram for approval behavior.

Outside scope: reviewer access control, persistent/concurrent state, model evaluation, vendor schema validation, connector execution, durable retries, and monitoring. No measured revenue impact is asserted.
