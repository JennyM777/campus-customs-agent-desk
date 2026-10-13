"""Accounting specialist agent. All shop facts come from the MCP server."""

from pathlib import Path

from pydantic_ai import Agent

from backend.config import get_model
from backend.mcp_toolset import mcp_toolset_for
from backend.models import AccountingFinding

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "accounting.md"

ALLOWED_TOOLS = {"get_desk_today", "get_cash_account", "get_invoice", "get_unpaid_invoices_for_vendor"}

accounting_agent = Agent(
    get_model(),
    output_type=AccountingFinding,
    system_prompt=PROMPT_PATH.read_text(),
    name="accounting_agent",
    toolsets=[mcp_toolset_for("accounting", ALLOWED_TOOLS)],
)
