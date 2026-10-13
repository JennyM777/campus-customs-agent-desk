"""CLI entry point: run the Campus Customs multi-agent team against one ticket.

Usage:
    python -m backend.run <ticket_id>

Requires PORTKEY_API_KEY to be set; every agent is pinned to gpt-6-luna via
Portkey (see backend/config.py). Every delegated step, plus this top-level
run, is appended to output/audit_trail.json.
"""

import sys

from backend.agents.boss_agent import boss_agent
from backend.audit import log_agent_run


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m backend.run <ticket_id>")
        raise SystemExit(1)

    ticket_id = int(sys.argv[1])
    prompt = (
        f"Handle open ticket {ticket_id}. Look it up, delegate to whichever "
        "specialists you need, and give me your final decision."
    )
    result = boss_agent.run_sync(prompt, deps=ticket_id)
    log_agent_run("boss_agent", ticket_id, result)
    print(result.output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
