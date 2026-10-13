"""Appends every agent run's execution steps to output/audit_trail.json.

Always appends to the existing list of runs; never overwrites prior entries.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic_ai import messages as _messages

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"


def _extract_steps(result: Any) -> list[dict]:
    steps: list[dict] = []
    for message in result.new_messages():
        for part in message.parts:
            if isinstance(part, _messages.ToolCallPart):
                steps.append(
                    {
                        "type": "tool_call",
                        "tool_name": part.tool_name,
                        "args": part.args_as_dict(),
                    }
                )
            elif isinstance(part, _messages.ToolReturnPart):
                steps.append(
                    {
                        "type": "tool_return",
                        "tool_name": part.tool_name,
                        "content": part.content,
                    }
                )
            elif isinstance(part, _messages.TextPart):
                steps.append({"type": "text", "content": part.content})
    return steps


def log_agent_run(agent_name: str, ticket_id: int | None, result: Any) -> None:
    """Append one execution record for this agent run to output/audit_trail.json."""
    output = result.output
    entry = {
        "agent": agent_name,
        "ticket_id": ticket_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps": _extract_steps(result),
        "final_output": output.model_dump() if hasattr(output, "model_dump") else output,
    }

    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if AUDIT_PATH.exists():
        existing = json.loads(AUDIT_PATH.read_text())
    else:
        existing = []
    existing.append(entry)
    AUDIT_PATH.write_text(json.dumps(existing, indent=2, default=str))
