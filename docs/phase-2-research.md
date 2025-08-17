## Phase 2 — Research (Finding backlink opportunities)

### Research input (signed-in only)

#### UI
- Single input: `keyword` (required, 2–80 chars).
- Optional: `max_results` (default 10; min 1, max 50). Not user-selectable for now (fixed at 10).
- Button: "Start Research".

#### Validation
- Keyword required; trim whitespace; disallow only punctuation/emoji.
- Disable button during in-flight request.

#### API contract
- Start: `POST /research/start`
  - Body: `{ "keyword": "ai writers", "max_results": 10 }`
  - Provider API keys are NOT sent from the UI; backend reads from `.env`.
- Poll: `GET /research/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

#### States
- Idle → Starting → Polling → Done/Error
- Error shows `error` string from response; re-enable inputs.

#### Edge cases
- Backend offline: show inline banner with retry + link to `/docs`.
- Backend missing provider keys: backend returns a clear error; UI shows guidance and disables Start until resolved.
- No results: render empty-state table.

---

### Results table (read-only)

#### Columns
- `url` (link), `domain`, `title`, `contact_email`, `contact_form_url`, `guidelines_url`, `context_source`, `page_excerpt` (truncated, tooltip on hover).

#### Table UX
- Sticky header, client-side pagination.
- Wrap long text; tooltips for long excerpts.
- Summary line: total rows, time completed.

#### Acceptance
- Renders all returned rows; links open in new tab.
- CSV download works when `saved_csv_path` is present.

---

### Technical details
- Frontend uses `VITE_API_BASE_URL` for API base.
- Poll interval: 1500ms; stop on `done` or `error`.
- Loading & errors use inline banners/toasts.


