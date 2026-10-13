import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { AuditEntry, BossDecision, CashAccount, PaymentRequest, Ticket } from "./types";
import { TicketCard } from "./components/TicketCard";
import { AgentFeed } from "./components/AgentFeed";
import { SummaryPanel } from "./components/SummaryPanel";
import { ApprovalQueue } from "./components/ApprovalQueue";
import { CashBalanceBadge } from "./components/CashBalanceBadge";
import "./App.css";

function latestBossDecisionByTicket(entries: AuditEntry[]): Record<number, BossDecision> {
  const out: Record<number, BossDecision> = {};
  for (const e of entries) {
    if (e.agent === "boss_agent" && e.ticket_id != null) {
      out[e.ticket_id] = e.final_output as unknown as BossDecision;
    }
  }
  return out;
}

export default function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [feedByTicket, setFeedByTicket] = useState<Record<number, AuditEntry[]>>({});
  const [decisionByTicket, setDecisionByTicket] = useState<Record<number, BossDecision>>({});
  const [cash, setCash] = useState<CashAccount | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const loadBoard = async () => {
    const [t, events, c] = await Promise.all([
      api.getTickets(),
      api.getRecentEvents(500),
      api.getCashBalance(),
    ]);
    setTickets(t);
    setCash(c);
    const grouped: Record<number, AuditEntry[]> = {};
    for (const e of events) {
      if (e.ticket_id == null) continue;
      (grouped[e.ticket_id] ??= []).push(e);
    }
    setFeedByTicket(grouped);
    setDecisionByTicket(latestBossDecisionByTicket(events));
    if (t.length > 0 && selectedId === null) setSelectedId(t[0].id);
  };

  useEffect(() => {
    loadBoard().catch((e) => setError(String(e.message ?? e)));
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRun = async (ticketId: number) => {
    setError(null);
    setRunningId(ticketId);
    setSelectedId(ticketId);

    pollRef.current = window.setInterval(async () => {
      try {
        const events = await api.getRecentEvents(500);
        const forTicket = events.filter((e) => e.ticket_id === ticketId);
        setFeedByTicket((prev) => ({ ...prev, [ticketId]: forTicket }));
      } catch {
        /* keep polling even if one tick fails */
      }
    }, 900);

    try {
      const { decision } = await api.runTicket(ticketId);
      setDecisionByTicket((prev) => ({ ...prev, [ticketId]: decision }));
      await loadBoard();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      if (pollRef.current) {
        window.clearInterval(pollRef.current);
        pollRef.current = null;
      }
      setRunningId(null);
    }
  };

  const handleApprove = async (req: PaymentRequest, approvedBy: string) => {
    try {
      await api.approvePayment({
        kind: req.kind,
        ref_id: req.ref_id,
        amount: req.amount,
        account: req.account,
        reason: req.reason,
        approved_by: approvedBy,
      });
      const c = await api.getCashBalance();
      setCash(c);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleReset = async () => {
    if (!window.confirm("Reset the sandbox database back to its original values?")) return;
    try {
      await api.reset();
      setFeedByTicket({});
      setDecisionByTicket({});
      setSelectedId(null);
      await loadBoard();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const selectedTicket = tickets.find((t) => t.id === selectedId) ?? null;
  const selectedFeed = selectedId != null ? feedByTicket[selectedId] ?? [] : [];
  const selectedDecision = selectedId != null ? decisionByTicket[selectedId] ?? null : null;
  const pendingApprovals = selectedDecision?.pending_human_approvals ?? [];

  return (
    <div className="desk">
      <header className="desk-header">
        <div className="desk-title">
          <span className="desk-logo">🐾</span>
          <div>
            <h1>Campus Customs — Agent Desk</h1>
            <p>Operations console for the Boss, Inventory, Accounting, Facilities &amp; Customer Service team</p>
          </div>
        </div>
        <div className="desk-header-right">
          <CashBalanceBadge account={cash} />
          <button className="reset-btn" onClick={handleReset}>
            ↺ Reset sandbox
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner" onClick={() => setError(null)}>
          ⚠ {error} <span className="dismiss">(dismiss)</span>
        </div>
      )}

      <main className="desk-main">
        <section className="board-column">
          <h2 className="column-title">Ticket Tray</h2>
          <div className="ticket-list">
            {tickets.map((t) => (
              <TicketCard
                key={t.id}
                ticket={t}
                isSelected={t.id === selectedId}
                isRunning={runningId === t.id}
                onSelect={() => setSelectedId(t.id)}
                onRun={() => handleRun(t.id)}
              />
            ))}
            {tickets.length === 0 && <p className="muted">Loading tickets…</p>}
          </div>
        </section>

        <section className="feed-column">
          <h2 className="column-title">
            {selectedTicket ? `Live activity — Ticket #${selectedTicket.id}` : "Live activity"}
          </h2>
          <div className="feed-panel">
            <AgentFeed entries={selectedFeed} isRunning={runningId === selectedId} />
          </div>
        </section>

        <section className="side-column">
          <h2 className="column-title">Decision &amp; Approvals</h2>
          <SummaryPanel decision={selectedDecision} agentEntries={selectedFeed} />
          <ApprovalQueue pending={pendingApprovals} onApprove={handleApprove} />
        </section>
      </main>
    </div>
  );
}
