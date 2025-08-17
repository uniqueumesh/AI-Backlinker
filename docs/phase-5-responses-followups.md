## Phase 5 — Responses & Follow-ups (backend-first)

### Goal
- Detect replies and support polite follow-ups without manual tracking.

### Approach
1) Backend IMAP checker (configured via `.env`) periodically fetches unseen messages; associates by `to_email` or subject hash; stores lightweight status.
2) Expose minimal endpoints:
   - `GET /inbox/status` (counts, last-checked timestamp)
   - `POST /followups/start` (accepts rows; dry-run initially)
3) UI (later): read-only indicators per campaign and a one-click "Schedule follow-up" respecting opt-outs.

### Acceptance (backend-first)
- IMAP checker surfaces counts via API.
- Follow-up job accepts rows and records outcomes (dry-run in development).


