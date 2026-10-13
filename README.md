# Campus Customs — Multi-Agent Operations Desk

A multi-agent system (PydanticAI + an MCP server + a FastAPI backend + a React dashboard) that triages and resolves operational tickets for Campus Customs, a Yale-area campus apparel and gifts shop — restocking decisions, vendor invoices, rent, and bulk pricing requests — with every payment gated on human approval.

## Repository layout

```
.
├── AI_prompts.md              # Log of every prompt used, by problem
├── requirements.txt            # Top-level Python deps (mcp_server + backend)
├── .env.example                 # Copy to .env and fill in PORTKEY_API_KEY
├── .mcp.json                    # MCP client config (how a vibe coder connects to mcp_server/)
├── data/
│   ├── campus_customs.db        # Original, untouched database
│   └── campus_customs_new.db    # Working copy agents/backend read & write
├── mcp_server/                  # FastMCP server: the only path to shop data
│   ├── server.py
│   └── README.md
├── backend/                     # PydanticAI agents + FastAPI API
│   ├── agents/                  # boss, inventory, accounting, facilities, customer_service
│   ├── prompts/                 # one detailed .md system prompt per agent
│   ├── config.py                # single source of truth for the model (gpt-6-luna via Portkey)
│   ├── models.py                # shared Pydantic schemas
│   ├── mcp_toolset.py            # per-agent MCP tool allowlists
│   ├── audit.py                  # appends every agent run to output/audit_trail.json
│   ├── main.py                   # FastAPI routes the dashboard calls
│   └── run.py                    # CLI: python -m backend.run <ticket_id>
├── frontend/                    # React + Vite + TypeScript dashboard ("Agent Desk")
└── output/                      # All deliverables: harness.md, desk_tickets.html,
                                  # resolved_tickets.json, resolved_board.html,
                                  # audit_trail.json, design.md, mcp_smoke.json,
                                  # github_url.txt, screenshots/
```

## Setup

1. **Python deps**
   ```bash
   pip install -r requirements.txt
   ```
2. **Node deps**
   ```bash
   cd frontend && npm install
   ```
3. **Environment**
   ```bash
   cp .env.example .env
   # then edit .env and set PORTKEY_API_KEY
   ```

## Running it

Start all three in separate terminals:

```bash
# 1. Backend (needs PORTKEY_API_KEY set, e.g. via `export $(cat .env | xargs)`)
cd backend && uvicorn main:app --reload --port 8000

# 2. Frontend
cd frontend && npm run dev
# open http://localhost:5173
```

The MCP server (`mcp_server/server.py`) isn't run standalone in normal use — the backend's agents launch it themselves as a subprocess per `.mcp.json`/`backend/mcp_toolset.py`.

To run one ticket from the CLI instead of the dashboard:
```bash
cd backend && python -m backend.run 101
```

To reset the working database back to its original state:
```bash
curl -X POST http://localhost:8000/api/reset
```

## Where to read more

- **`output/harness.md`** — the full reference: every database table, every MCP tool, all five agents, every FastAPI route, the frontend dashboard, and the safety guardrails.
- **`output/desk_tickets.html`** — the planning + actual-execution + reflection write-up for tickets 101, 102, and 103.
- **`output/design.md`** — the dashboard's design rationale.
- **`AI_prompts.md`** — every prompt used to build this project, organized by problem.
