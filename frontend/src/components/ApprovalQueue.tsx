import { useState } from "react";
import type { PaymentRequest } from "../types";

interface Props {
  pending: PaymentRequest[];
  onApprove: (req: PaymentRequest, approvedBy: string) => Promise<void>;
}

export function ApprovalQueue({ pending, onApprove }: Props) {
  const [approvedBy, setApprovedBy] = useState("Jenny Meng");
  const [busyIndex, setBusyIndex] = useState<number | null>(null);
  const [done, setDone] = useState<Set<number>>(new Set());

  if (pending.length === 0) return null;

  const handleApprove = async (req: PaymentRequest, idx: number) => {
    setBusyIndex(idx);
    try {
      await onApprove(req, approvedBy || "Unknown");
      setDone((prev) => new Set(prev).add(idx));
    } finally {
      setBusyIndex(null);
    }
  };

  return (
    <div className="approval-queue">
      <h3>⏳ Pending human approval</h3>
      <div className="approval-name-row">
        <label htmlFor="approver-name">Approving as</label>
        <input
          id="approver-name"
          value={approvedBy}
          onChange={(e) => setApprovedBy(e.target.value)}
        />
      </div>
      {pending.map((req, idx) => {
        const isDone = done.has(idx);
        return (
          <div key={idx} className={`approval-card ${isDone ? "approved" : ""}`}>
            <div className="approval-top">
              <span className="approval-kind">{req.kind === "invoice" ? "Invoice" : "Rent"}</span>
              <span className="approval-amount">${req.amount.toLocaleString()}</span>
            </div>
            <div className="approval-reason">{req.reason}</div>
            <div className="approval-meta">
              ref #{req.ref_id} · from {req.account}
            </div>
            <button
              className="approve-btn"
              disabled={isDone || busyIndex === idx}
              onClick={() => handleApprove(req, idx)}
            >
              {isDone ? "✓ Approved & paid" : busyIndex === idx ? "Processing…" : "Approve & pay"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
