## Loaders, Progress Bars, and Live Status Messages

### Purpose
Give end users immediate, clear feedback while background jobs run. Show a visual progress bar, short human‑readable messages (e.g., "Searching (3/8)…"), and small counters (searched, scraped, emails found, sent_ok, etc.). This is additive only and does not change core logic or outputs.

### Goals
- Show a visible loader and percentage for each phase (Research, Drafts, Send)
- Display friendly status messages and basic counters
- Keep API backward compatible (existing clients keep working)
- Keep changes minimal, safe, and testable in small steps

### Non‑Goals (for this iteration)
- No cancel/retry buttons
- No streaming logs or websockets (keep polling)
- No database changes; continue writing CSV files

---

## Architecture Overview

Current jobs already run in the background and expose status via:
- `GET /research/status/{job_id}`
- `GET /emails/generate/status/{job_id}`
- `GET /send/status/{job_id}`

We will extend each status response with optional fields:
- `message?: string` — short user‑friendly text
- `stats?: object` — numeric counters only (e.g., `{ searched, scraped, emails_found }`)

The new fields are optional so older frontends ignore them safely.

---

## Backend Changes (additive and safe)

Files to touch:
- `backend/app/models.py`
- `backend/app/routers/research.py`
- `backend/app/routers/emails.py`
- `backend/app/routers/send.py`

### 1) Models: add optional fields
Add to all three status models:
- `message: Optional[str] = None`
- `stats: Optional[Dict[str, int]] = None`

Backward compatible: existing fields unchanged.

### 2) Research job status updates (`backend/app/routers/research.py`)
- At start: `progress=0.05`, `message="Preparing queries…"`, `stats={"searched":0,"scraped":0,"emails_found":0}`
- During search loop (per query `i/N`): update message `"Searching Google (i/N)…"`; increment `stats["searched"]` as results processed
- During scraping (per URL `k/M`): update message `"Scraping pages (k/M)…"`; increment `stats["scraped"]`; after email extraction, add to `stats["emails_found"]`
- Before save: `progress≈0.95`, `message="Saving results…"`
- Done: `progress=1.0`, `message="Done. X rows"`

Throttling: call `job_store.update` at most ~4 times/second.

### 3) Email generation status updates (`backend/app/routers/emails.py`)
- Start: `stats={"selected":T,"generated":0,"fallback":0}`, `message="Generating drafts (0/T)…"`
- Per draft: increment `generated` (and `fallback` if placeholder); set `progress = 0.2 + 0.75*(generated/T)`; update message `"Generating drafts (generated/T)…"`
- Done: `message="Done. generated drafts"`

### 4) Sending status updates (`backend/app/routers/send.py`)
- Start: detect total rows `T`; `stats={"processed":0,"sent_ok":0,"error":0,"skipped":0}`, `message="Sending emails…"`
- Per row: update counters; set `progress = 0.2 + 0.75*(processed/T)`; `message="Sending (processed/T)… ok:sent_ok error:error"`
- Done: `message="Done. sent:sent_ok error:error skipped:skipped"`

### 5) Errors
On exceptions, set `status="error"`, keep partial `stats`, and a clear `message` like `"Job failed — see error"`.

---

## Frontend Changes (UI only)

Files to touch:
- `frontend/src/services/api.ts` (type updates)
- `frontend/src/pages/ResearchPage.tsx` (render progress, message, counters)

### 1) API types
For all three status types, add optional:
- `message?: string`
- `stats?: Record<string, number>`

### 2) Research UI
- Replace generic text with:
  - Linear progress bar bound to `status.progress`
  - Caption from `status.message || 'Working…'`
  - Counters when present: e.g., `searched 3 · scraped 2 · emails 4`

### 3) Drafts UI
- Show progress bar and `egStatus.message` like `"Generating drafts (4/7)…"`
- Counters: `generated`, `fallback`

### 4) Send UI
- Show progress bar and `sendStatus.message` like `"Sending (12/50)… ok:11 error:1"`
- Counters: `processed`, `sent_ok`, `error`, `skipped`

### 5) UX guidelines
- Always show progress bars once a job starts; hide on done/error
- Keep messages short; truncate if long
- If `message` is missing, fall back to phase‑specific generic text

---

## Polling Strategy
Keep the existing 1.5s polling cadence. Consider a faster first poll (500–800 ms) for snappier feedback after starting a job.

---

## Backward Compatibility
- All new fields are optional
- No request payload changes
- CSV outputs are unchanged

---

## Acceptance Criteria

Research
- Progress bar appears within 1.5s of starting
- While running, message and counters update (searched/scraped/emails_found)
- On completion, progress shows 100% with final message (e.g., "Done. 14 rows")

Drafts
- Shows `"Generating drafts (i/T)…"` with progress and counters

Send
- Shows `"Sending (i/T)… ok:X error:Y"` with progress and counters
- On error, user sees a clear failure message

Accessibility
- Progress has textual alternative (percent or message visible)
- No disruptive layout shift

---

## Rollout Plan (small, safe steps)

Step 1: UI loaders (no backend change)
- Use existing `status.progress` to show a linear loader and a generic message

Step 2: Backend messages/stats for Research
- Add `message`/`stats` updates in `research.py`; extend the status model

Step 3: Frontend reads messages/stats (Research)
- Render `message` and counters if present

Step 4: Repeat for Drafts and Send
- Add events in `emails.py` and `send.py`; render on the frontend

---

## Example Status Payloads

Research mid‑run:
```
{
  "job_id": "abc",
  "status": "running",
  "progress": 0.42,
  "message": "Scraping pages (6/14)…",
  "stats": { "searched": 8, "scraped": 6, "emails_found": 9 }
}
```

Drafts final:
```
{
  "job_id": "def",
  "status": "done",
  "progress": 1.0,
  "message": "Done. 7 drafts",
  "stats": { "selected": 7, "generated": 7, "fallback": 2 }
}
```

Send mid‑run:
```
{
  "job_id": "ghi",
  "status": "running",
  "progress": 0.55,
  "message": "Sending (28/50)… ok:26 error:2",
  "stats": { "processed": 28, "sent_ok": 26, "error": 2, "skipped": 0 }
}
```

---

## Testing Checklist
- Start research with and without API keys; observe live message + counters
- Generate drafts; verify counts increment and progress advances smoothly
- Send with dry_run; verify processed/ok/error counters
- Simulate an error; ensure error status and message are visible
- Cross‑browser sanity (Chrome, Edge, Safari)
- Performance: UI feels responsive; updates no more than ~4/second

---

## Risks and Mitigations
- Too many updates → throttle `job_store.update`
- Long messages → truncate to ~80 chars
- Missing keys → show friendly hint (e.g., "Using placeholder drafts; no LLM key set")

---

## Implementation Map

Backend
- `backend/app/models.py`: add `message` and `stats` to status responses
- `backend/app/routers/research.py`: emit progress + message + counters during loops
- `backend/app/routers/emails.py`: emit per‑row generation updates
- `backend/app/routers/send.py`: emit per‑row sending updates

Frontend
- `frontend/src/services/api.ts`: extend status types with `message?` and `stats?`
- `frontend/src/pages/ResearchPage.tsx`: render progress bar, live message, counters for Research, Drafts, Send


