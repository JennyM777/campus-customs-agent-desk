# Campus Customs Database Harness

A comprehensive reference for the Campus Customs multi-agent system: the database tables, the MCP server's tools, the five agents, the FastAPI routes, the frontend dashboard, and the safety rules that govern all of it.

**Contents:** [Database Tables](#database-tables) · [MCP Tools](#mcp-tools) · [The Five Agents](#the-five-agents) · [Agents and Their MCP Tools](#agents-and-their-mcp-tools) · [Safety Guardrails](#safety-guardrails) · [FastAPI Routes](#fastapi-routes) · [Frontend Dashboard](#frontend-dashboard)

## Database Tables

A table-by-table reference to `campus_customs_new.db`, noting every field and why the table matters to our multi-agent team.

## desk
- `date_today` — the current date as the shop sees it.
- `notes` — free-text notes for the day.

Why it matters: gives agents a stable notion of "today" and any ambient context, so date-sensitive decisions (e.g. is an invoice overdue) are anchored correctly.

## tickets
- `id` — unique ticket identifier.
- `type` — category of request (e.g. customer_order, rent_notice, price_override).
- `requester` — who raised the ticket.
- `subject` — short description of the issue.
- `sku` — related inventory item, if any.
- `size` — related inventory size, if any.
- `qty` — quantity involved, if any.
- `lease_id` — linked lease, if any.
- `invoice_id` — linked invoice, if any.
- `status` — open/closed state of the ticket.
- `notes` — free-text detail.
- `created_at` — timestamp the ticket was raised.

Why it matters: this is the task queue — the entry point that tells agents what work exists and which other tables they need to cross-reference to resolve it.

## inventory
- `sku` — product identifier (part of composite PK with size).
- `name` — product name.
- `size` — size variant (part of composite PK with sku).
- `qty` — units on hand.
- `location` — storage location in the shop.

Why it matters: tells agents whether a requested item can actually be fulfilled, or whether a shortage needs to be escalated (restock, backorder, substitution).

## pricing
- `sku` — product identifier (PK).
- `unit_cost` — cost to acquire/produce one unit.
- `list_price` — standard selling price.

Why it matters: lets agents evaluate margin and decide how far a discount or price override can go before it erodes profit.

## vendors
- `id` — vendor identifier (PK).
- `name` — vendor name.
- `specialty` — what the vendor supplies/does.
- `lead_days` — typical turnaround time for orders.

Why it matters: helps agents pick the right supplier for a restock and set realistic expectations on timing.

## leases
- `id` — lease identifier (PK).
- `space_name` — the leased space's name.
- `landlord` — landlord/property manager.
- `monthly_rent` — recurring rent amount.
- `next_due` — date the next rent payment is due.
- `notes` — free-text detail.

Why it matters: lets agents recognize and prioritize recurring fixed obligations (rent) against available cash.

## cash_accounts
- `name` — account identifier (PK).
- `balance` — current balance.
- `date` — as-of date for the balance.

Why it matters: gives agents the funds available to approve payments, so they don't authorize spending beyond what's on hand.

## payments
- `id` — payment identifier (PK).
- `kind` — type of payment (e.g. invoice, rent).
- `ref_id` — id of the related record (invoice/lease) being paid.
- `amount` — amount paid.
- `account` — which cash account the payment drew from.
- `paid_at` — timestamp of payment.
- `approved_by` — who authorized the payment.

Why it matters: serves as the audit trail confirming what has actually been settled, letting agents distinguish outstanding obligations from resolved ones.

## invoices
- `id` — invoice identifier (PK).
- `vendor_id` — vendor the invoice is owed to.
- `amount` — amount owed.
- `due_date` — payment deadline.
- `status` — open/paid state.
- `description` — what the invoice is for.

Why it matters: tracks money owed to vendors, so agents can flag overdue bills and connect them back to the inventory/tickets that triggered them.

## MCP Tools

A breakdown of the three tools in `mcp_server/server.py`, each tied to the specific ticket it is best suited to unlock.

### `get_open_tickets`
- **Table read:** `tickets`
- **Ticket it unlocks:** 102
- **Why:** Ticket 102 is a time-sensitive `rent_notice` with no sku/invoice to chase down, so the only thing standing between the team and noticing "rent is due in 2 days" is this tool surfacing it from the open-tickets queue before `next_due` (2026-09-02) arrives.

### `get_ticket_details`
- **Table read:** `tickets` joined with `leases` and `invoices` (which itself joins `vendors`), plus `inventory`/`pricing` when a sku is present
- **Ticket it unlocks:** 101
- **Why:** Ticket 101 carries an `invoice_id` of 501, and only this tool's join against `invoices`/`vendors` reveals that a $840 rush reprint from Bulldog Print Co. is already open and overdue (due 2026-08-28) — the exact fact needed to tell Tauhid Zaman a restock is already underway rather than starting one from scratch.

### `check_inventory`
- **Table read:** `inventory`, annotated with `unit_cost`/`list_price` from `pricing`
- **Ticket it unlocks:** 103
- **Why:** Ticket 103 asks for a 20-unit bulk discount on CC-HOOD-NAVY size M, and only this tool's sku-wide query (no size filter) exposes that size M alone has just 8 units in stock while the pricing columns show a $36 margin per unit — the two numbers needed to judge whether 20 units can be fulfilled and how much room exists to discount.

## The Five Agents

All five are PydanticAI `Agent`s defined under `backend/agents/`, each loading its system prompt from a dedicated file under `backend/prompts/`, and every one of them is pinned to the same model via `backend/config.py`'s `get_model()` — `gpt-6-luna`, routed through Portkey using `PORTKEY_API_KEY`. No other model name appears anywhere in the codebase.

| Agent | File | Prompt | Output type | Role |
|---|---|---|---|---|
| Boss | `backend/agents/boss_agent.py` | `backend/prompts/boss.md` | `BossDecision` | Reads the ticket, delegates to whichever specialists are actually needed, and produces the final decision + any pending `PaymentRequest`s. |
| Inventory | `backend/agents/inventory_agent.py` | `backend/prompts/inventory.md` | `InventoryFinding` | Checks stock across sizes, names a restock vendor and lead time when short, and checks whether that vendor has an unpaid invoice blocking a new order. |
| Accounting | `backend/agents/accounting_agent.py` | `backend/prompts/accounting.md` | `AccountingFinding` | Checks cash balance and invoice status, and drafts (never executes) a `PaymentRequest` when one is warranted and affordable. |
| Facilities | `backend/agents/facilities_agent.py` | `backend/prompts/facilities.md` | `FacilitiesFinding` | Checks lease terms against `desk.date_today`, and drafts (never executes) a rent `PaymentRequest` when due and affordable. |
| Customer Service | `backend/agents/customer_service_agent.py` | `backend/prompts/customer_service.md` | `CustomerServiceReply` | Drafts the reply to the ticket's requester, grounded only in facts the other specialists (or the ticket itself) actually reported. |

The Boss delegates via four async tools (`delegate_to_inventory`, `delegate_to_accounting`, `delegate_to_facilities`, `delegate_to_customer_service`) that call the other agents' `.run()` directly in-process, threading `ctx.usage` through for combined token tracking — not a second MCP hop.

## Agents and Their MCP Tools

Every fact an agent uses comes from a tool call to `mcp_server/server.py` over `data/campus_customs_new.db` — no agent queries the database directly. Each agent connects to the same MCP server but is restricted (via `backend/mcp_toolset.py`'s `.filtered()` wrapper) to only the tools relevant to its role.

### Boss agent
| Tool | Table(s) read |
|---|---|
| `get_open_tickets` | `tickets` |
| `get_ticket_details` | `tickets`, `leases`, `invoices`, `vendors`, `inventory`, `pricing` |
| `get_desk_today` | `desk` |

Plus four non-MCP delegation tools (`delegate_to_inventory`, `delegate_to_accounting`, `delegate_to_facilities`, `delegate_to_customer_service`) that call the other four agents directly in-process.

### Inventory agent
| Tool | Table(s) read |
|---|---|
| `check_inventory` | `inventory`, `pricing` |
| `list_vendors` | `vendors` |
| `get_unpaid_invoices_for_vendor` | `invoices`, `vendors` |

### Accounting agent
| Tool | Table(s) read |
|---|---|
| `get_desk_today` | `desk` |
| `get_cash_account` | `cash_accounts` |
| `get_invoice` | `invoices`, `vendors` |
| `get_unpaid_invoices_for_vendor` | `invoices`, `vendors` |

### Facilities agent
| Tool | Table(s) read |
|---|---|
| `get_desk_today` | `desk` |
| `get_lease` | `leases` |
| `get_cash_account` | `cash_accounts` |

### Customer Service agent
| Tool | Table(s) read |
|---|---|
| `get_ticket_details` | `tickets`, `leases`, `invoices`, `vendors`, `inventory`, `pricing` |

## Safety Guardrails

This team touches real customers' requests and the shop's actual cash, so the following limits are non-negotiable and are enforced in every agent's prompt:

- **No agent executes a payment.** Accounting and Facilities may only produce a `PaymentRequest` object (see `backend/models.py`); nothing in this codebase writes to the `payments` table. A human must review and approve every payment before it happens.
- **Unpaid invoices block new shipments.** The Inventory agent is instructed to check a vendor's unpaid invoices (via `get_unpaid_invoices_for_vendor`) before recommending a new order with that vendor, and to refuse to recommend one if a blocker exists.
- **Cash can never go negative.** Accounting and Facilities must compare any proposed payment amount against the live `checking` balance (via `get_cash_account`) and report a blocker instead of proposing a payment the shop can't afford.
- **All dates are anchored to `desk.date_today`**, never to an assumed real-world date, so overdue/due-soon determinations stay consistent with the shop's own data.
- **No agent invents data.** Every number, date, sku, or status that ends up in a finding or a customer-facing reply must trace back to an MCP tool call — this is enforced by instruction in every prompt file under `backend/prompts/`.
- **Every execution step is audited.** `backend/audit.py` appends each agent run's tool calls, tool results, and final structured output to `output/audit_trail.json`, so any decision the team makes can be traced back to the exact data it was based on.

### Token-usage limits

- **Each specialist agent is scoped to a small, fixed tool allowlist** (3–4 tools each, enforced via `.filtered()` in `backend/mcp_toolset.py`), so a single run can't accidentally explore the entire tool surface and burn tokens on irrelevant calls.
- **Structured `output_type`s keep responses short.** Every agent returns a typed Pydantic model (`InventoryFinding`, `AccountingFinding`, etc.) instead of free-form prose, which caps how much the model can ramble per turn.
- **Delegation is one level deep.** The Boss agent calls a specialist once per question; specialists don't call each other, which keeps the total number of model calls per ticket bounded (at most 1 Boss call + 1 call per specialist actually needed).
- **`ctx.usage` is threaded through every delegation call**, so the Boss agent's run accumulates and can report total token usage across the whole team for one ticket, making runaway usage visible rather than hidden inside sub-agent calls.

## FastAPI Routes

Every route the dashboard uses, defined in `backend/main.py`. Start the server from `backend/` with `uvicorn main:app --reload --port 8000`.

| Method & URL | What it does |
|---|---|
| `GET /api/tickets` | Returns all three tickets with their current `status` (open/resolved). |
| `POST /api/tickets/{ticket_id}/run` | Runs the Boss agent (and whichever specialists it delegates to) on that ticket, logs the run to the audit trail, and marks the ticket resolved. |
| `GET /api/events/recent?limit=20` | Returns the most recent entries from `output/audit_trail.json` — each agent's tool calls, tool results, and final output — for the dashboard to poll. |
| `POST /api/payments/approve` | The only route that moves money: inserts a row into `payments`, deducts the amount from the given `cash_accounts` balance, marks the linked invoice `paid` if applicable, rejects (400) any payment that would push the balance negative, and rejects (409) a duplicate approval for a `kind`+`ref_id` already paid. |
| `GET /api/cash/balance?account=checking` | Returns a `cash_accounts` row's current balance and as-of date. |
| `POST /api/reset` | Copies `data/campus_customs.db` back over `data/campus_customs_new.db`, discarding every change agents or approved payments made during the session. |

## Frontend Dashboard

`frontend/` is a React + Vite + TypeScript single-page app (the "Agent Desk") that is the human operator's console for everything above. It talks only to the FastAPI routes — no direct database or MCP access.

- **Ticket Tray** (left column) — all three tickets from `GET /api/tickets`, each with an open/resolved status pill and a "Run team" button that calls `POST /api/tickets/{id}/run`.
- **Live activity** (center column) — while a run is in flight, polls `GET /api/events/recent` roughly every 900ms and renders each agent's tool calls, tool results, and text as they're written to `output/audit_trail.json`, color-coded per agent.
- **Decision & Approvals** (right column) — the Boss's `final_summary` plus a one-line finding per specialist actually consulted, and an `ApprovalQueue` that lists any drafted `PaymentRequest`s with an "Approve & pay" button wired to `POST /api/payments/approve`.
- **Cash badge** (header) — `GET /api/cash/balance`, with a brief red/green flash when the balance changes after an approval.
- **Reset button** (header) — `POST /api/reset`, with a confirmation prompt before wiping the working database back to its original state.

Run it with the backend already up on `:8000`: `npm install && npm run dev` from `frontend/`, then open `http://localhost:5173`. See `frontend/README.md` for details and `output/design.md` for the design rationale.
