## Frontend Plan: Landing → Auth → Research (Phase 2)

This document specifies the exact UX, states, API calls, and acceptance criteria for the first three steps of the SaaS UI.

### Goals
- Gate research behind sign-in (Clerk Google/GitHub).
- Minimal flow: Get Started → Login → Enter Keyword → Start Research → Show Results Table.
- Keep the landing page strictly minimal: only the elements described below (no extra buttons/text).
- Reliable polling and clear feedback.
- Frontend never handles provider API keys. Backend reads all required keys from its own `.env`.

---

## 1) Landing (anonymous)

### UI
- One visible control: "Get Started" button.

### Behavior
- Clicking "Get Started":
  - If NOT signed in → open Clerk sign-in (Google/GitHub).
  - If signed in → scroll or navigate to Research panel.

### Acceptance
- "Get Started" opens Clerk modal when signed out.
- No keyword input shown while signed out.

---

## 2) Auth (Clerk)

### Requirements
- Providers enabled: Google and GitHub (set in Clerk dashboard).
- If only one provider is enabled in Clerk, only that provider will appear in the modal.
- Frontend env: `VITE_CLERK_PUBLISHABLE_KEY` set.
- Allowed origins/redirects include current dev URL.

### UI
- No extra login buttons on the landing page besides "Get Started".
- Clerk modal provides both Google and GitHub options (when enabled in Clerk).
- After sign-in, show a minimal sign-out control (e.g., a small "Sign out" link/button) without introducing extra navigation.

### Behavior
- On successful OAuth, page shows research input panel.
- On failure, surface Clerk’s error and remain on landing.
- On sign-out, return to landing state showing only "Get Started".

### Acceptance
- SignedOut → no research input visible.
- SignedIn → research input visible.
- Clerk sign-in modal displays both Google and GitHub.
- A sign-out control is visible after sign-in, and returns the UI to the signed-out landing state when used.

---

## 3) Research input (signed-in only)

### UI
- Single input: `keyword` (required, 2–80 chars).
- Optional: `max_results` (default 10; min 1, max 50). Not user-selectable for now (fixed at 10).
- Button: "Start Research".
- Note (non-visual requirement): Backend uses configured provider keys. No keys are entered in the UI.

### Validation
- Keyword required; trim whitespace; disallow only punctuation/emoji.
- Disable button during in-flight request.

### API contract
- Start: `POST /research/start`
  - Body (example): `{ "keyword": "ai writers", "max_results": 10 }` (fixed default for now)
  - Provider API keys are NOT sent from the UI; backend reads them from its `.env`.
- Poll: `GET /research/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

### States
- Idle: input enabled; no results.
- Starting: optimistic toast/inline banner "Starting research…".
- Polling: show progress bar or spinner; disable inputs.
- Done:
  - Render results table (see section 4).
- Error:
  - Surface `error` string from response.
  - Re-enable inputs; "Try again" button.

### Edge cases
- Backend reachable but job errors: show error and keep input.
- Backend offline: show inline banner with retry + link to `/docs`.
- Backend missing provider keys: backend responds with a clear error; UI displays "Backend is not configured with required API keys. Please configure keys in backend `.env`." and disables Start until resolved.
- No results returned: render empty-state table with helpful message.

### Acceptance
- Valid keyword triggers start → polling → results or error.
- UI remains responsive; button states reflect in-flight work.

---

## 4) Results table (research output)

### Columns (read-only)
- `url` (link), `domain`, `title`, `contact_email`, `contact_form_url`, `guidelines_url`, `context_source`, `page_excerpt` (truncated, tooltip on hover).

### Table UX
- Sticky header, client-side pagination (e.g., 10–25 rows per page).
- Column resize optional; wrap long text; tooltips for long excerpts.
- Summary line: total rows, time completed.

### Actions
- None on landing page (no extra buttons). Table is read-only.

### Acceptance
- Renders all returned rows; links open in new tab.
- CSV download works when `saved_csv_path` is present.

---

## 5) Technical details

### Environment variables
- Frontend
  - `VITE_API_BASE_URL` → base URL for backend (e.g., `http://127.0.0.1:8000`).
  - `VITE_CLERK_PUBLISHABLE_KEY` → enables auth UI when valid.
- Backend (managed server-side; never shown/entered in UI)
  - `SERPER_API_KEY`, `FIRECRAWL_API_KEY`, `GEMINI_API_KEY`/`OPENAI_API_KEY`, `SENDGRID_API_KEY`, `MAILERSEND_API_KEY`, `SMTP_*`, etc.

### API client
- Use fetch/axios instance with `baseURL = VITE_API_BASE_URL`.
- Timeouts: 30s; JSON error handling with clear messages.
- Polling interval: 1500ms; stop when `done` or `error`.

### Loading & errors
- Use inline banners and toasts for start/poll/done/error.
- Keep table visible after success; allow new searches without page reload.

### Accessibility
- All buttons focusable; ARIA labels for status banners.
- Table navigable via keyboard; tooltips accessible.

---

## 6) Acceptance checklist (E2E)

- Anonymous user:
  - Sees Get Started button only.
  - Clicking Get Started opens Clerk login.
- After sign-in:
  - Sees keyword input and Start button.
  - Enters keyword → Start → sees progress → results or error.
  - Results table shows expected columns.
- Failure modes:
  - Backend down: clear inline message; no crash.
  - Job error: shows error and allows retry.

---

## 7) Future extensions (not in this scope)
- Phase 3 UI (email generation) consuming research job output.
- Phase 4 UI (sending) with provider credentials and dry-run.
- Campaign persistence, templates, approvals, analytics.
 - User-selectable `max_results` control (1–50) on the research input.

---

## 8) Repository structure (later)
- Keep a clean separation for clarity and onboarding:
  - `frontend/` — all React/Tailwind/MUI code, Vite config, and assets
  - `backend/` — FastAPI app (`app/`), core modules (`ai_backlinking.py`, `email_sender.py`), `requirements.backlinker.txt`, `README.md`, and `data/`
- No changes now; implement this reorganization only when requested.


---

## 9) Phase 3 — Email generation (UI plan)

### Goal
- From a completed research job, generate short, personalized email drafts using the backend (Gemini/OpenAI). Frontend never handles provider keys.

### Preconditions
- User is signed in (Clerk).
- At least one research job has completed in this session (the UI holds the latest `research_job_id`).

### UI (minimal)
- Panel: "Generate emails" (visible only when a research job is done).
- Fields:
  - `subject` (text, default "Guest post collaboration")
  - `take` (fixed default 5; not user-selectable for now)
- Button: "Generate Emails".
- After completion: read-only table with `to_email`, `subject`, `body` (no extra buttons).

### API contract
- Start: `POST /emails/generate/start`
  - Body (example): `{ "research_job_id": "<ID>", "provider": "gemini", "subject": "Guest post collaboration", "take": 5 }`
  - No provider keys are sent; backend reads them from its `.env`.
- Poll: `GET /emails/generate/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

### States
- Idle: form enabled; no results.
- Starting: banner "Generating emails…"; disable inputs.
- Polling: progress/spinner.
- Done: show drafts table; keep form available for a re-run.
- Error: show backend error; re-enable inputs.

### Table (read-only)
- Columns: `to_email`, `subject`, `body` (truncate long body with ellipsis; tooltip optional).

### Acceptance
- After a research job completes, the "Generate emails" panel appears.
- Clicking "Generate Emails" starts a job and polls until done.
- On success, UI shows a table with `to_email, subject, body`.
- No provider keys shown or requested; no extra buttons.



---

## 10) Phase 4 — Sending (UI plan)

### Goal
- From generated drafts (Phase 3) or a CSV, send emails via provider (SendGrid, Mailersend, or SMTP). Defaults to dry-run in dev.

### Preconditions
- User is signed in (Clerk).
- A completed email generation job exists in the session (preferred), or a user-supplied CSV is provided.

### UI (minimal)
- Panel: "Send emails" (visible when at least one email generation job is done OR when user selects CSV).
- Fields:
  - `provider`: radio (sendgrid | mailersend | smtp)
  - `from_email`: text (required)
  - `dry_run`: checkbox (default true in dev)
  - `rate_limit_per_sec`: number (default 10)
  - Optional: "Use last generated emails" vs "Upload CSV" (CSV schema: to_email,subject,body)
- Button: "Start Sending".
- After completion: read-only outcomes table.

### API contract
- Start: `POST /send/start`
  - If using previous job results: `{ "provider":"sendgrid", "from_email":"me@domain.com", "rows":[{to_email,subject,body},...], "rate_limit_per_sec":10, "dry_run":true }`
  - If using CSV: `{ "provider":"mailersend", "from_email":"me@domain.com", "in_csv":"/path or uploaded temp", "rate_limit_per_sec":10, "dry_run":true }`
  - Provider keys are NOT sent from UI; backend uses `.env` (SendGrid/Mailersend/SMTP vars).
- Poll: `GET /send/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

### States
- Idle → Starting → Polling → Done/Error. Disable inputs while in-flight. Show clear error text from backend.

### Table (read-only)
- Columns: `row`, `to_email`, `status`, `code`, `message`.

### Acceptance
- With valid provider setup, sends all rows (or dry-runs) and renders outcomes table.
- No provider keys appear in UI; no extra buttons.

---

## 11) Phase 5 — Responses & Follow-ups (backend-first plan)

### Goal
- Detect replies and enable polite follow-ups without manual tracking.

### Approach (incremental)
1) Backend IMAP checker (config via `.env`): periodically fetch unseen messages, associate by `to_email` or subject hash, store lightweight status (opened/replied/positive?)
2) Expose `GET /inbox/status` and `POST /followups/start` minimal endpoints (dry-run first).
3) UI (later): badge counts + read-only list per campaign; one-click "Schedule polite follow-up" (uses templates and respects opt-out).

### Acceptance (backend-first)
- IMAP checker runs and surfaces counts via API.
- Follow-up job accepts rows and records outcomes (dry-run in dev).

---

## 12) Milestones & Checklist

- M1: Research (frontend Phases 1–2) — DONE
- M2: Backend integration & .env loading — DONE
- M3: Email Generation (frontend Phase 3)
  - Add "Generate emails" panel gated by research completion
  - Wire to `/emails/generate/start` + polling to `/emails/generate/status/{job_id}`
- M4: Sending (frontend Phase 4)
  - Add "Send emails" panel, dry-run default
  - Wire to `/send/start` + `/send/status/{job_id}`; render outcomes
- M5: Responses/Follow-ups (backend-first)
  - IMAP checker + status endpoint; follow-up job (dry-run)

---

## 13) Notes

- Frontend never handles provider keys; backend loads from `.env` on startup.
- CSVs are generated under backend/data/ and ignored by Git.
- Keep landing minimal per product guidance; panels only appear as prior phases complete.
