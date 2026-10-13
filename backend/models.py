"""Pydantic data types shared across the Campus Customs multi-agent team."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Ticket(BaseModel):
    id: int
    type: str
    requester: str
    subject: str
    sku: Optional[str] = None
    size: Optional[str] = None
    qty: Optional[int] = None
    lease_id: Optional[int] = None
    invoice_id: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: str


class InventoryItem(BaseModel):
    sku: str
    name: str
    size: str
    qty: int
    location: str
    unit_cost: Optional[float] = None
    list_price: Optional[float] = None


class VendorInfo(BaseModel):
    id: int
    name: str
    specialty: str
    lead_days: int


class LeaseInfo(BaseModel):
    id: int
    space_name: str
    landlord: str
    monthly_rent: float
    next_due: str
    notes: Optional[str] = None


class InvoiceInfo(BaseModel):
    id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    amount: float
    due_date: str
    status: str
    description: Optional[str] = None


class CashAccount(BaseModel):
    name: str
    balance: float
    date: str


class PaymentRequest(BaseModel):
    """A payment an agent believes should happen. Never auto-executed.

    Every payment in this system requires a human to approve it before any
    row is written to the payments table.
    """

    kind: Literal["invoice", "rent"]
    ref_id: int
    amount: float
    account: str = "checking"
    reason: str
    requires_human_approval: bool = Field(default=True, frozen=True)


class InventoryFinding(BaseModel):
    sku: str
    requested_qty: Optional[int] = None
    size: Optional[str] = None
    stock_by_size: list[InventoryItem] = []
    can_fulfill: bool
    vendor_recommendation: Optional[str] = None
    summary: str


class AccountingFinding(BaseModel):
    cash_balance: float
    unpaid_invoices: list[InvoiceInfo] = []
    shipment_blocked: bool
    payment_request: Optional[PaymentRequest] = None
    summary: str


class FacilitiesFinding(BaseModel):
    lease: Optional[LeaseInfo] = None
    is_overdue: bool
    days_until_due: Optional[int] = None
    payment_request: Optional[PaymentRequest] = None
    summary: str


class CustomerServiceReply(BaseModel):
    ticket_id: int
    requester: str
    message: str


class BossDecision(BaseModel):
    ticket_id: int
    delegations: list[str] = Field(
        default_factory=list, description="Which specialist agents were consulted"
    )
    pending_human_approvals: list[PaymentRequest] = []
    final_summary: str
