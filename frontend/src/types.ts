export interface Ticket {
  id: number;
  type: string;
  requester: string;
  subject: string;
  status: string;
}

export interface PaymentRequest {
  kind: "invoice" | "rent";
  ref_id: number;
  amount: number;
  account: string;
  reason: string;
  requires_human_approval: boolean;
}

export interface BossDecision {
  ticket_id: number;
  delegations: string[];
  pending_human_approvals: PaymentRequest[];
  final_summary: string;
}

export interface AuditStep {
  type: "tool_call" | "tool_return" | "text";
  tool_name?: string;
  args?: Record<string, unknown>;
  content?: unknown;
}

export interface AuditEntry {
  agent: string;
  ticket_id: number | null;
  timestamp: string;
  steps: AuditStep[];
  final_output: Record<string, unknown>;
}

export interface CashAccount {
  name: string;
  balance: number;
  date: string;
}

export interface ApprovePaymentBody {
  kind: "invoice" | "rent";
  ref_id: number;
  amount: number;
  account: string;
  reason: string;
  approved_by: string;
}

export interface ApprovePaymentResponse {
  status: string;
  account: string;
  new_balance: number;
}
