"""Customer Service specialist agent. All shop facts come from the MCP server."""

from pathlib import Path

from pydantic_ai import Agent

from backend.config import get_model
from backend.mcp_toolset import mcp_toolset_for
from backend.models import CustomerServiceReply

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "customer_service.md"

ALLOWED_TOOLS = {"get_ticket_details"}

customer_service_agent = Agent(
    get_model(),
    output_type=CustomerServiceReply,
    system_prompt=PROMPT_PATH.read_text(),
    name="customer_service_agent",
    toolsets=[mcp_toolset_for("customer_service", ALLOWED_TOOLS)],
)
