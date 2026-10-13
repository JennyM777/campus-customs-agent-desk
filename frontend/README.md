# Campus Customs — Agent Desk (frontend)

React + Vite + TypeScript dashboard for operating the Campus Customs multi-agent team.

## Run it

1. Start the backend first (from `backend/`, with `PORTKEY_API_KEY` set):
   ```bash
   uvicorn main:app --reload --port 8000
   ```
2. In this directory:
   ```bash
   npm install
   npm run dev
   ```
3. Open http://localhost:5173

If the backend runs on a different host/port, set `VITE_API_BASE` (e.g. in a `.env.local` file) before starting the dev server.

## What it does

- **Ticket Tray** (left) — all three tickets with open/resolved status; click "Run team" to trigger the Boss agent on one.
- **Live activity** (center) — polls `/api/events/recent` every ~900ms while a run is in progress, streaming each agent's tool calls, tool results, and findings as they happen.
- **Decision & Approvals** (right) — the Boss agent's final summary, a one-line finding per specialist consulted, and an approval queue for any `PaymentRequest` the team drafted (approving calls `/api/payments/approve`, which executes the transfer).
- **Checking balance** (header) — pulled from `/api/cash/balance`, flashes when it changes after an approval.
- **Reset sandbox** (header) — calls `/api/reset` to restore the working database to its original values.
