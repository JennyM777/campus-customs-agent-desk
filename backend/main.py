"""FastAPI backend for the Campus Customs desk dashboard.

This is the one place outside the MCP server where the working database is
written to directly — and only for actions a human has already authorized
(approving a payment, resetting the sandbox) or for ticket lifecycle status.
Agents themselves never write; they only read via mcp_server/server.py and
draft PaymentRequests for a human to approve here.
"""

import json
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parent.parent
# Allow `uvicorn main:app` to work from inside backend/, where the `backend`
# package itself wouldn't otherwise be importable, as well as `python -m
# backend.main` from the project root.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.boss_agent import boss_agent
from backend.audit import AUDIT_PATH, log_agent_run

ORIGINAL_DB = ROOT / "data" / "campus_customs.db"
WORKING_DB = ROOT / "data" / "campus_customs_new.db"

app = FastAPI(title="Campus Customs Desk API")

# The Vite dev server for frontend/ runs on localhost:5173 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(WORKING_DB)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------------------------------
# 1. Tickets: list all three with their current open/resolved status
# --------------------------------------------------------------------------


class TicketSummary(BaseModel):
    id: int
    type: str
    requester: str
    subject: str
    status: str


@app.get("/api/tickets", response_model=list[TicketSummary])
def list_tickets() -> list[TicketSummary]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, type, requester, subject, status FROM tickets ORDER BY id"
        ).fetchall()
        return [TicketSummary(**dict(r)) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------
# 2. Run the multi-agent team on one ticket
# --------------------------------------------------------------------------


class RunResult(BaseModel):
    ticket_id: int
    decision: dict


@app.post("/api/tickets/{ticket_id}/run", response_model=RunResult)
async def run_ticket(ticket_id: int) -> RunResult:
    conn = _connect()
    try:
        row = conn.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"No ticket with id {ticket_id}")

    prompt = (
        f"Handle open ticket {ticket_id}. Look it up, delegate to whichever "
        "specialists you need, and give me your final decision."
    )
    try:
        result = await boss_agent.run(prompt, deps=ticket_id)
    except Exception as exc:  # noqa: BLE001 - surface any agent/model failure to the caller
        raise HTTPException(status_code=502, detail=f"Agent run failed: {exc}") from exc

    log_agent_run("boss_agent", ticket_id, result)

    conn = _connect()
    try:
        conn.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
        conn.commit()
    finally:
        conn.close()

    return RunResult(ticket_id=ticket_id, decision=result.output.model_dump())


# --------------------------------------------------------------------------
# 3. Recent agent events, for the dashboard to refresh against
# --------------------------------------------------------------------------


@app.get("/api/events/recent")
def recent_events(limit: int = 20) -> list[dict]:
    if not AUDIT_PATH.exists():
        return []
    entries = json.loads(AUDIT_PATH.read_text())
    return entries[-limit:]


# --------------------------------------------------------------------------
# 4. Human-approved payments: the only route that moves money
# --------------------------------------------------------------------------


class ApprovePaymentBody(BaseModel):
    kind: Literal["invoice", "rent"]
    ref_id: int
    amount: float
    account: str = "checking"
    reason: str
    approved_by: str


@app.post("/api/payments/approve")
def approve_payment(body: ApprovePaymentBody) -> dict:
    conn = _connect()
    try:
        existing = conn.execute(
            "SELECT id FROM payments WHERE kind = ? AND ref_id = ?",
            (body.kind, body.ref_id),
        ).fetchone()
        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"A {body.kind} payment for ref_id {body.ref_id} was already "
                    "approved and paid; refusing to pay it twice."
                ),
            )

        acct_row = conn.execute(
            "SELECT balance FROM cash_accounts WHERE name = ?", (body.account,)
        ).fetchone()
        if acct_row is None:
            raise HTTPException(status_code=404, detail=f"No cash account named {body.account}")

        balance = acct_row["balance"]
        if body.amount > balance:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Payment of {body.amount} would exceed {body.account}'s "
                    f"balance of {balance}; refusing to let cash go negative."
                ),
            )

        desk_row = conn.execute("SELECT date_today FROM desk LIMIT 1").fetchone()
        paid_at = desk_row["date_today"] if desk_row else None

        conn.execute(
            """
            INSERT INTO payments (kind, ref_id, amount, account, paid_at, approved_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (body.kind, body.ref_id, body.amount, body.account, paid_at, body.approved_by),
        )
        conn.execute(
            "UPDATE cash_accounts SET balance = balance - ?, date = ? WHERE name = ?",
            (body.amount, paid_at, body.account),
        )
        if body.kind == "invoice":
            conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (body.ref_id,))
        conn.commit()

        new_balance = conn.execute(
            "SELECT balance FROM cash_accounts WHERE name = ?", (body.account,)
        ).fetchone()["balance"]
        return {"status": "paid", "account": body.account, "new_balance": new_balance}
    finally:
        conn.close()


# --------------------------------------------------------------------------
# 5. Current checking balance
# --------------------------------------------------------------------------


@app.get("/api/cash/balance")
def cash_balance(account: str = "checking") -> dict:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM cash_accounts WHERE name = ?", (account,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No cash account named {account}")
        return dict(row)
    finally:
        conn.close()


# --------------------------------------------------------------------------
# 6. Reset the working database back to the original, untouched values
# --------------------------------------------------------------------------


@app.post("/api/reset")
def reset_database() -> dict:
    shutil.copyfile(ORIGINAL_DB, WORKING_DB)
    return {"status": "reset", "restored_from": ORIGINAL_DB.name}
