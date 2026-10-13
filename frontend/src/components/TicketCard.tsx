import type { Ticket } from "../types";

const TYPE_LABEL: Record<string, string> = {
  customer_order: "Customer Order",
  rent_notice: "Rent Notice",
  price_override: "Price Override",
};

const TYPE_ICON: Record<string, string> = {
  customer_order: "🧾",
  rent_notice: "🏠",
  price_override: "🏷️",
};

interface Props {
  ticket: Ticket;
  isSelected: boolean;
  isRunning: boolean;
  onSelect: () => void;
  onRun: () => void;
}

export function TicketCard({ ticket, isSelected, isRunning, onSelect, onRun }: Props) {
  const resolved = ticket.status === "resolved";

  return (
    <div
      className={`ticket-card ${isSelected ? "selected" : ""} ${resolved ? "resolved" : ""}`}
      onClick={onSelect}
    >
      <div className="ticket-card-top">
        <span className="ticket-icon">{TYPE_ICON[ticket.type] ?? "📋"}</span>
        <span className="ticket-id">#{ticket.id}</span>
        <span className={`status-pill ${resolved ? "status-resolved" : "status-open"}`}>
          {resolved ? "Resolved" : "Open"}
        </span>
      </div>
      <div className="ticket-type">{TYPE_LABEL[ticket.type] ?? ticket.type}</div>
      <div className="ticket-subject">{ticket.subject}</div>
      <div className="ticket-requester">from {ticket.requester}</div>

      <button
        className="run-btn"
        disabled={isRunning || resolved}
        onClick={(e) => {
          e.stopPropagation();
          onRun();
        }}
      >
        {isRunning ? (
          <>
            <span className="spinner" /> Running…
          </>
        ) : resolved ? (
          "Resolved"
        ) : (
          "▶ Run team"
        )}
      </button>
    </div>
  );
}
