"""FastMCP server exposing read-only tools over campus_customs_new.db for handling tickets."""

import sqlite3
from pathlib import Path

from fastmcp import FastMCP

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs_new.db"

mcp = FastMCP("campus-customs-tickets")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row) for row in rows]


@mcp.tool()
def get_open_tickets() -> list[dict]:
    """Return every ticket in the tickets table whose status is 'open'."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE status = 'open' ORDER BY created_at"
        ).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


@mcp.tool()
def get_ticket_details(ticket_id: int) -> dict:
    """Return a ticket's full row plus any linked lease, invoice (with vendor), and inventory/pricing records found via the ticket's sku, size, lease_id, or invoice_id."""
    conn = _connect()
    try:
        ticket_row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        if ticket_row is None:
            return {"error": f"No ticket found with id {ticket_id}"}
        ticket = dict(ticket_row)

        result: dict = {"ticket": ticket, "lease": None, "invoice": None, "inventory": [], "pricing": None}

        if ticket.get("lease_id") is not None:
            lease_row = conn.execute(
                "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],)
            ).fetchone()
            result["lease"] = dict(lease_row) if lease_row else None

        if ticket.get("invoice_id") is not None:
            invoice_row = conn.execute(
                """
                SELECT invoices.*, vendors.name AS vendor_name, vendors.specialty AS vendor_specialty,
                       vendors.lead_days AS vendor_lead_days
                FROM invoices
                JOIN vendors ON vendors.id = invoices.vendor_id
                WHERE invoices.id = ?
                """,
                (ticket["invoice_id"],),
            ).fetchone()
            result["invoice"] = dict(invoice_row) if invoice_row else None

        if ticket.get("sku"):
            inventory_rows = conn.execute(
                "SELECT * FROM inventory WHERE sku = ? ORDER BY size",
                (ticket["sku"],),
            ).fetchall()
            result["inventory"] = _rows_to_dicts(inventory_rows)

            pricing_row = conn.execute(
                "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],)
            ).fetchone()
            result["pricing"] = dict(pricing_row) if pricing_row else None

        return result
    finally:
        conn.close()


@mcp.tool()
def check_inventory(sku: str, size: str | None = None) -> list[dict]:
    """Return inventory rows for a sku (optionally filtered to one size), each annotated with its unit_cost and list_price from the pricing table."""
    conn = _connect()
    try:
        query = "SELECT * FROM inventory WHERE sku = ?"
        params: list = [sku]
        if size is not None:
            query += " AND size = ?"
            params.append(size)
        query += " ORDER BY size"

        inventory_rows = _rows_to_dicts(conn.execute(query, params).fetchall())

        pricing_row = conn.execute(
            "SELECT unit_cost, list_price FROM pricing WHERE sku = ?", (sku,)
        ).fetchone()
        pricing = dict(pricing_row) if pricing_row else None

        for row in inventory_rows:
            row["unit_cost"] = pricing["unit_cost"] if pricing else None
            row["list_price"] = pricing["list_price"] if pricing else None

        return inventory_rows
    finally:
        conn.close()


@mcp.tool()
def get_desk_today() -> str:
    """Return the shop's current date from the desk table — the only valid reference point for overdue checks."""
    conn = _connect()
    try:
        row = conn.execute("SELECT date_today FROM desk LIMIT 1").fetchone()
        if row is None:
            raise ValueError("desk table has no rows")
        return row["date_today"]
    finally:
        conn.close()


@mcp.tool()
def list_vendors() -> list[dict]:
    """Return every vendor with its specialty and lead_days, for restock decisions."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM vendors").fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


@mcp.tool()
def get_lease(lease_id: int) -> dict | None:
    """Return a single lease's space name, landlord, monthly rent, and next_due date."""
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


@mcp.tool()
def get_invoice(invoice_id: int) -> dict | None:
    """Return a single invoice (amount, due_date, status, description) joined with its vendor's name."""
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT invoices.*, vendors.name AS vendor_name
            FROM invoices
            JOIN vendors ON vendors.id = invoices.vendor_id
            WHERE invoices.id = ?
            """,
            (invoice_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


@mcp.tool()
def get_unpaid_invoices_for_vendor(vendor_id: int) -> list[dict]:
    """Return every invoice owed to a vendor whose status is not 'paid' — used to confirm whether a new shipment from that vendor is blocked."""
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT invoices.*, vendors.name AS vendor_name
            FROM invoices
            JOIN vendors ON vendors.id = invoices.vendor_id
            WHERE invoices.vendor_id = ? AND invoices.status != 'paid'
            """,
            (vendor_id,),
        ).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


@mcp.tool()
def get_cash_account(name: str = "checking") -> dict | None:
    """Return a cash account's current balance and as-of date — used to confirm a payment won't push the balance negative."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM cash_accounts WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
