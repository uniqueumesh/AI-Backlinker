## Phase 1 — Getting Started (Landing, Auth)

### Goals
- Gate research behind sign-in (Clerk Google/GitHub).
- Minimal flow: Get Started → Login → go to Research panel.
- Frontend never handles provider API keys. Backend reads keys from its own `.env`.

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
- Providers enabled: Google and GitHub (in Clerk dashboard).
- Frontend env: `VITE_CLERK_PUBLISHABLE_KEY` set.
- Allowed origins/redirects include current dev URL.

### UI
- No extra login buttons on the landing page besides "Get Started".
- After sign-in, show a minimal sign-out control (e.g., small "Sign out").

### Behavior
- On successful OAuth, page shows research input panel.
- On failure, surface Clerk’s error and remain on landing.
- On sign-out, return to landing state showing only "Get Started".

### Acceptance
- SignedOut → no research input visible.
- SignedIn → research input visible.
- Clerk sign-in modal displays Google and GitHub (when enabled).
- Sign-out returns the UI to signed-out landing state.

---

## Environment variables (frontend)
- `VITE_API_BASE_URL` → backend base URL (e.g., `http://127.0.0.1:8000`).
- `VITE_CLERK_PUBLISHABLE_KEY` → enables auth UI.

Note: Backend provider keys are not handled by the UI and live in backend `.env`.


