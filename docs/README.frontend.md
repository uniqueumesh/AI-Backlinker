## AI Backlinker Frontend (React) — Plan

Simple, non‑tech friendly UI for the existing FastAPI backend. Three steps: Research → Generate → Send. Clear progress, CSV import/export, and minimal credentials handling.

### Goals
- Keep backend and frontend separate (API-only integration)
- Make each phase one clear screen with progress and results
- Allow CSV upload/download at each phase
- No secret storage in Git or localStorage

### Tech Choices
- React + TypeScript + Vite
- Data fetching/polling: React Query (or SWR)
- UI: MUI or TailwindCSS + HeadlessUI
- CSV parsing: PapaParse
- Validation: Zod
- Toasts: react-hot-toast

### Environment
- `.env` (Vite):
  - `VITE_API_BASE_URL=http://127.0.0.1:8000`
  - `VITE_API_KEY=` (optional; maps to `X-API-Key` if enabled)
- Backend CORS must include the frontend origin (e.g., http://localhost:5173)

### App Structure
```
src/
  App.tsx            # routes and layout
  config.ts          # reads env vars
  services/
    api.ts           # axios client + endpoints
  hooks/
    useJobPolling.ts # generic polling hook
  pages/
    ResearchPage.tsx
    EmailsPage.tsx
    SendPage.tsx
    SettingsPage.tsx (optional)
  components/
    JobProgress.tsx
    ResultsTable.tsx
    CsvUploader.tsx
    ProviderCredentialsForm.tsx
    HealthBadge.tsx
  types/             # mirrors backend models
```

### Pages and Flows
- Research
  - Inputs: keyword or URLs list, max_results, optional Serper/Firecrawl keys
  - POST `/research/start` → get `job_id` → poll `/research/status/{id}`
  - Show progress and table: url, domain, contact_email, excerpt
  - Actions: Download CSV (use `saved_csv_path`), "Use in Emails"

- Emails
  - Source: choose a completed research job or upload research CSV
  - Inputs: subject, your_name, your_email, topic, LLM provider/key (optional)
  - POST `/emails/generate/start` → poll `/emails/generate/status/{id}`
  - Show table: to_email, subject, body; Download CSV; "Use in Send"

- Send
  - Source: upload Emails CSV or use rows from previous step
  - Provider tabs: SMTP | SendGrid | MailerSend (show only required fields)
  - Toggle: dry run
  - POST `/send/start` → poll `/send/status/{id}`
  - Show outcomes table and download outcomes CSV

### API Client (minimal)
```ts
// src/services/api.ts
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    ...(import.meta.env.VITE_API_KEY ? { "X-API-Key": import.meta.env.VITE_API_KEY } : {}),
  },
});

export const startResearch = (body: any) => api.post("/research/start", body).then(r => r.data);
export const getResearchStatus = (id: string) => api.get(`/research/status/${id}`).then(r => r.data);
export const startEmailGen = (body: any) => api.post("/emails/generate/start", body).then(r => r.data);
export const getEmailGenStatus = (id: string) => api.get(`/emails/generate/status/${id}`).then(r => r.data);
export const startSend = (body: any) => api.post("/send/start", body).then(r => r.data);
export const getSendStatus = (id: string) => api.get(`/send/status/${id}`).then(r => r.data);
```

### Polling Hook (React Query)
```ts
// src/hooks/useJobPolling.ts
import { useQuery } from "@tanstack/react-query";

export function useJobPolling<T>(key: any[], fetcher: () => Promise<T>, enabled: boolean) {
  return useQuery({
    queryKey: key,
    queryFn: fetcher,
    enabled,
    refetchInterval: (data: any) => (data?.status && ["done","error"].includes(data.status) ? false : 1500),
  });
}
```

### Research Page Skeleton
```tsx
// src/pages/ResearchPage.tsx
import { useState } from "react";
import { startResearch, getResearchStatus } from "../services/api";
import { useJobPolling } from "../hooks/useJobPolling";

export default function ResearchPage() {
  const [jobId, setJobId] = useState<string | null>(null);

  async function onSubmit(form: { keyword?: string; urls?: string[]; max_results?: number }) {
    const r = await startResearch(form);
    setJobId(r.job_id);
  }

  const { data: status } = useJobPolling(["research", jobId], () => getResearchStatus(jobId!), !!jobId);

  return (
    <div>
      {/* form inputs + submit button */}
      {/* when jobId set, show progress and results */}
    </div>
  );
}
```

### Security
- Never commit API keys. Prefer entering keys per-request; do not persist in localStorage.
- If backend enables `X-API-Key`, include it via `VITE_API_KEY` env.
- Mask sensitive inputs in forms; clear on navigation.

### CSV Handling
- Use PapaParse; expect UTF‑8 with BOM for Excel compatibility
- Validate columns pre-upload:
  - Research CSV: `url,domain,title,contact_email,...`
  - Emails CSV: `to_email,subject,body`

### Testing
- Unit: `services/api.ts`, `hooks/useJobPolling.ts`
- Integration: page forms (start → poll → render)
- E2E: Cypress with MSW to mock backend jobs

### Deployment
- Build: `npm run build` (Vite)
- Host: Netlify/Vercel; set `VITE_API_BASE_URL` to the backend URL
- Ensure backend CORS allows the deployed origin

### Incremental Rollout
1) Scaffold app shell + HealthBadge (calls `/health`)
2) Research page end-to-end
3) Emails page end-to-end
4) Send page end-to-end (start with dry-run)
5) CSV upload/download polish + validations
6) Optional: X-API-Key auth, provider presets, template editor


