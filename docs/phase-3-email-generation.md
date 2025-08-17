## Phase 3 — Email Generation (UI plan)

### Goal
- From a completed research job, generate short, personalized email drafts via backend (Gemini/OpenAI). Frontend never handles provider keys.

### Preconditions
- User is signed in (Clerk).
- At least one research job has completed (UI holds `research_job_id`).

### UI (with selection + HITL)
- Panel: "Generate emails" (visible only when a research job is done).
- Fields:
  - `subject` (default: "Guest post collaboration")
  - `take` (default 5; range 1–100)
  - `provider` (select: gemini | openai; default gemini)
  - `model` (optional text select; shows sensible defaults per provider, e.g., gemini-2.5-flash / gpt-4o-mini)
  - Selection source: user selects rows in the Research results table (checkbox per row; selection preserved across pagination). The panel reads the current selection.
  - Inline contact fixes: if a row is missing `contact_email`, the user can edit/add it directly in the results table before generation (email format validated).
- Button: "Generate Emails".
- After completion: drafts table supports HITL review and inline edits of `subject` and `body` prior to sending.

### API contract
- Start: `POST /emails/generate/start`
  - Body (examples):
    - Minimal: `{ "research_job_id": "<ID>", "provider": "gemini", "subject": "Guest post collaboration", "take": 5 }`
    - With selections: `{ "research_job_id": "<ID>", "provider": "openai", "model": "gpt-4o-mini", "selected_urls": ["https://...","https://..."], "subject": "Guest post collaboration", "take": 5 }`
- Poll: `GET /emails/generate/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

### States
- Idle → Starting → Polling → Done/Error.
  - Idle: form enabled, shows last successful drafts (if any) below.
  - Starting: disable controls; banner "Generating emails…".
  - Polling: progress/spinner with job_id tooltip; allow Cancel.
  - Done: render drafts table; re-enable form.
  - Error: show error text from backend; re-enable form; keep last successful drafts visible until replaced.

### Drafts table (HITL editable)
- Columns: `to_email`, `subject`, `body` (truncate with ellipsis; tooltip/expandable preview).
- Editable cells: `subject`, `body`. Changes are kept client-side until Phase 4 sending.
- Row actions:
  - Copy body to clipboard
  - Expand to preview full body
- Bulk actions (optional): Download CSV (current drafts)

### Acceptance
- After a research job completes, the "Generate emails" panel appears.
- Clicking "Generate Emails" starts a job and polls until done.
- On success, UI shows a table with `to_email, subject, body`.

---

## Detailed UX/Dev Plan

### Component structure
- `GenerateEmailsPanel`
  - Props: `latestResearchJobId`, `latestResearchRows` (optional)
  - Internal state: subject, take, provider, model, selectedUrls[] (derived from table selection), jobId, status, results[]
  - Children: `DraftsTable`
- `DraftsTable`
  - Props: rows, onCopy (optional), onChange(rowId, {subject,body})
  - Renders table with expand/copy/download and inline edits for subject/body

### Data flow & state
- Start → call `POST /emails/generate/start`
  - Build body from form values; include `research_job_id`, `subject`, `take`, `provider`, `model?`, `selected_urls?` (from table selection)
  - Save returned `job_id` to local state
### Pre-generation selection & edits
- Research table provides multi-select checkboxes per row; selection is stored globally (e.g., context) and read by the panel.
- Research table allows inline edit for `contact_email` prior to generation. Email format validation applies.
- Poll every 1500ms → `GET /emails/generate/status/{job_id}` until `done|error`
  - On done: set `results`, stop polling
  - On error: show error, stop polling

### Validation
- `subject`: 3–120 chars; trim; disallow only whitespace-only
- `take`: integer 1–100
- `selected_urls`: optional; must be subset of latest research URLs
 - `contact_email` (pre-generation): must be valid email syntax if provided

### UI/Styling (Tailwind + MUI)
- Use MUI `TextField` for subject, `Select` for provider/model, `Button` for submit
- Use MUI `DataGrid` or simple table for drafts; Tailwind for spacing/typography
- Keep color and spacing consistent with existing research page

### Accessibility
- Labels and `aria-live` region for status messages
- Keyboard navigation for table rows and expand/copy actions

### Error handling
- Network/5xx: show inline banner with retry
- Backend validation: render returned `error` string
- Missing backend keys: backend responds consistently; surface message "Backend not configured for selected provider"

### Performance
- Cap `take` at 100; lazy-render long bodies; avoid re-render storms during polling

### Testing checklist
- Start with valid inputs → reaches `done`, renders N rows
- Invalid `take` → disabled submit with helper text
- Missing `research_job_id` → panel hidden / disabled state
- Provider switch (gemini/openai) → request reflects selection
- Polling stops on `done` and on `error`
- Copy to clipboard works; CSV download includes all rows

### Future extensions (post-MVP)
- Per-row edit/in-place tweaks before sending (Phase 4)
- Template selection and variables
- Save drafts to backend for persistence across sessions


