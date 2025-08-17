## Phase 4 — Sending (UI plan)

### Goal
- Send emails from generated drafts (Phase 3) or a CSV via provider (SendGrid, Mailersend, SMTP). Default to dry-run in development.

### Preconditions
- User is signed in (Clerk).
- A completed email generation job exists, or a user-supplied CSV is provided.

### UI (minimal)
- Panel: "Send emails" (visible when a generation job is done OR CSV is selected).
- Fields:
  - `provider`: radio (sendgrid | mailersend | smtp)
  - `from_email`: text (required)
  - `dry_run`: checkbox (default true)
  - `rate_limit_per_sec`: number (default 10)
  - Source: "Use last generated emails" or "Upload CSV" (CSV schema: to_email,subject,body)
- Button: "Start Sending".
- After completion: read-only outcomes table.

### API contract
- Start: `POST /send/start`
  - Rows payload example: `{ "provider":"sendgrid", "from_email":"me@domain.com", "rows":[{to_email,subject,body},...], "rate_limit_per_sec":10, "dry_run":true }`
  - CSV payload example: `{ "provider":"mailersend", "from_email":"me@domain.com", "in_csv":"/path or uploaded temp", "rate_limit_per_sec":10, "dry_run":true }`
- Poll: `GET /send/status/{job_id}` every 1.5s until `status ∈ {"done","error"}`.

### States
- Idle → Starting → Polling → Done/Error. Disable inputs while in-flight.

### Outcomes table (read-only)
- Columns: `row`, `to_email`, `status`, `code`, `message`.

### Acceptance
- With valid provider config, sends (or dry-runs) and renders outcomes table.


