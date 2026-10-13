import type {
  ApprovePaymentBody,
  ApprovePaymentResponse,
  AuditEntry,
  BossDecision,
  CashAccount,
  Ticket,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string" ? body.detail : `Request failed: ${res.status}`
    );
  }
  return res.json() as Promise<T>;
}

export const api = {
  getTickets: () => request<Ticket[]>("/api/tickets"),

  runTicket: (ticketId: number) =>
    request<{ ticket_id: number; decision: BossDecision }>(
      `/api/tickets/${ticketId}/run`,
      { method: "POST" }
    ),

  getRecentEvents: (limit = 100) =>
    request<AuditEntry[]>(`/api/events/recent?limit=${limit}`),

  approvePayment: (body: ApprovePaymentBody) =>
    request<ApprovePaymentResponse>("/api/payments/approve", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getCashBalance: (account = "checking") =>
    request<CashAccount>(`/api/cash/balance?account=${account}`),

  reset: () => request<{ status: string; restored_from: string }>("/api/reset", {
    method: "POST",
  }),
};
