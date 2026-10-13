import type { AuditEntry, AuditStep } from "../types";

const AGENT_LABEL: Record<string, string> = {
  boss_agent: "Boss",
  inventory_agent: "Inventory",
  accounting_agent: "Accounting",
  facilities_agent: "Facilities",
  customer_service_agent: "Customer Service",
};

function summaryText(output: Record<string, unknown> | undefined): string | null {
  if (!output) return null;
  if (typeof output.summary === "string") return output.summary;
  if (typeof output.message === "string") return output.message;
  return null;
}

const AGENT_CLASS: Record<string, string> = {
  boss_agent: "agent-boss",
  inventory_agent: "agent-inventory",
  accounting_agent: "agent-accounting",
  facilities_agent: "agent-facilities",
  customer_service_agent: "agent-cs",
};

function renderStep(step: AuditStep, key: number) {
  if (step.type === "tool_call") {
    return (
      <div key={key} className="feed-step feed-call">
        <span className="feed-icon">🔧</span>
        <code>{step.tool_name}</code>
        <span className="feed-args">{JSON.stringify(step.args ?? {})}</span>
      </div>
    );
  }
  if (step.type === "tool_return") {
    const preview = JSON.stringify(step.content ?? null);
    return (
      <div key={key} className="feed-step feed-return">
        <span className="feed-icon">↩</span>
        <code>{step.tool_name}</code>
        <span className="feed-args">
          {preview.length > 140 ? preview.slice(0, 140) + "…" : preview}
        </span>
      </div>
    );
  }
  return (
    <div key={key} className="feed-step feed-text">
      <span className="feed-icon">💬</span>
      <span>{String(step.content ?? "")}</span>
    </div>
  );
}

interface Props {
  entries: AuditEntry[];
  isRunning: boolean;
}

export function AgentFeed({ entries, isRunning }: Props) {
  if (entries.length === 0) {
    return (
      <div className="feed-empty">
        {isRunning
          ? "Waiting on the first agent call…"
          : "Run a ticket to see the team's live activity here."}
      </div>
    );
  }

  return (
    <div className="agent-feed">
      {entries.map((entry, i) => (
        <div
          key={i}
          className={`feed-entry ${AGENT_CLASS[entry.agent] ?? ""} feed-enter`}
        >
          <div className="feed-entry-header">
            <span className="feed-agent-name">
              {AGENT_LABEL[entry.agent] ?? entry.agent}
            </span>
            <span className="feed-timestamp">
              {new Date(entry.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className="feed-steps">
            {entry.steps.map((s, j) => renderStep(s, j))}
          </div>
          {summaryText(entry.final_output) && (
            <div className="feed-summary">
              <span className="feed-icon">📝</span> {summaryText(entry.final_output)}
            </div>
          )}
        </div>
      ))}
      {isRunning && (
        <div className="feed-live-indicator">
          <span className="pulse-dot" /> live — polling for more activity…
        </div>
      )}
    </div>
  );
}
