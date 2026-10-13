"""Inventory specialist agent. All shop facts come from the MCP server."""

from pathlib import Path

from pydantic_ai import Agent

from backend.config import get_model
from backend.mcp_toolset import mcp_toolset_for
from backend.models import InventoryFinding

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "inventory.md"

ALLOWED_TOOLS = {"check_inventory", "list_vendors", "get_unpaid_invoices_for_vendor"}

inventory_agent = Agent(
    get_model(),
    output_type=InventoryFinding,
    system_prompt=PROMPT_PATH.read_text(),
    name="inventory_agent",
    toolsets=[mcp_toolset_for("inventory", ALLOWED_TOOLS)],
)
