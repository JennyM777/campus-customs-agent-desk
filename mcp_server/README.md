# Campus Customs Ticket MCP Server

A FastMCP server that gives agents read-only access to the Campus Customs shop database so they can triage and resolve open tickets without inventing data. This is the *only* path any agent uses to reach shop data — the PydanticAI team in `backend/` has no direct database access.

**Database:** `data/campus_customs_new.db` (the working copy of `campus_customs.db`).

## Tools

### `get_open_tickets()`
Returns every row from `tickets` where `status = 'open'`. The entry point for discovering what work is outstanding.

### `get_ticket_details(ticket_id)`
Returns a single ticket's full row plus whatever is actually linked to it: the matching `leases` row (via `lease_id`), the matching `invoices` row joined with its `vendors` row (via `invoice_id`), and the `inventory`/`pricing` rows (via `sku`). Only fields that genuinely exist on the ticket are populated — nothing is fabricated.

### `check_inventory(sku, size=None)`
Returns `inventory` rows for a given sku (optionally narrowed to one size), each annotated with `unit_cost` and `list_price` from `pricing`. Used to check stock levels and margin before approving an order or discount.

### `get_desk_today()`
Returns the shop's current date from the `desk` table — the only valid reference point for deciding whether an invoice or lease payment is overdue.

### `list_vendors()`
Returns every row from `vendors` (name, specialty, lead_days). Used to pick the right supplier for a restock and estimate turnaround time.

### `get_lease(lease_id)`
Returns a single `leases` row: space name, landlord, monthly rent, and next_due date.

### `get_invoice(invoice_id)`
Returns a single `invoices` row joined with its vendor's name.

### `get_unpaid_invoices_for_vendor(vendor_id)`
Returns every `invoices` row for a vendor whose status is not `'paid'` — used to confirm whether a new shipment from that vendor is currently blocked.

### `get_cash_account(name="checking")`
Returns a `cash_accounts` row (balance, as-of date) — used to confirm a proposed payment won't push the balance negative.

## Running

```bash
pip install -r requirements.txt
python server.py
```
