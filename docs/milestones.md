## Milestones & Checklist

- M1: Research (frontend Phases 1–2) — DONE
- M2: Backend integration & `.env` loading — DONE
- M3: Email Generation (frontend Phase 3)
  - Add "Generate emails" panel gated by research completion
  - Wire to `/emails/generate/start` + poll `/emails/generate/status/{job_id}`
- M4: Sending (frontend Phase 4)
  - Add "Send emails" panel, dry-run default
  - Wire to `/send/start` + `/send/status/{job_id}`; render outcomes
- M5: Responses/Follow-ups (backend-first)
  - IMAP checker + status endpoint; follow-up job (dry-run)

## Notes
- Frontend never handles provider keys; backend loads from `.env`.
- CSVs are generated under `backend/data/` and ignored by Git.
- Keep landing minimal; reveal panels as prior phases complete.


