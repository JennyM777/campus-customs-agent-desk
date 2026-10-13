import type { AuditEntry, BossDecision } from "../types";

const AGENT_LABEL: Record<string, string> = {
  boss_agent: "Boss",
  inventory_agent: "Inventory",
  accounting_agent: "Accounting",
  facilities_agent: "Facilities",
  customer_service_agent: "Customer Service",
};

function summaryText(output: Record<string, unknown>): string {
  if (typeof output.summary === "string") return output.summary;
  if (typeof output.message === "string") return output.message;
  return "No summary reported.";
}

interface Props {
  decision: BossDecision | null;
  agentEntries: AuditEntry[];
}

export function SummaryPanel({ decision, agentEntries }: Props) {
  if (!decision) {
    return (
      <div className="summary-panel empty">
        No decision yet for this ticket — run the team to see a summary here.
      </div>
    );
  }

  // one card per specialist actually consulted, most recent result first
  const perAgent = new Map<string, AuditEntry>();
  for (const entry of agentEntries) {
    if (entry.agent !== "boss_agent") perAgent.set(entry.agent, entry);
  }

  return (
    <div className="summary-panel">
      <h3>Final decision</h3>
      <p className="summary-text">{decision.final_summary}</p>

      {decision.delegations.length > 0 && (
        <div className="summary-delegations">
          <span className="summary-label">Delegated to:</span>{" "}
          {decision.delegations.join(", ")}
        </div>
      )}

      {perAgent.size > 0 && (
        <div className="summary-agents">
          {Array.from(perAgent.entries()).map(([agent, entry]) => (
            <div key={agent} className="summary-agent-card">
              <div className="summary-agent-name">{AGENT_LABEL[agent] ?? agent}</div>
              <div className="summary-agent-text">{summaryText(entry.final_output ?? {})}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
