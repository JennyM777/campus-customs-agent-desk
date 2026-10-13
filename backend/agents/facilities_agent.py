"""Facilities specialist agent. All shop facts come from the MCP server."""

from pathlib import Path

from pydantic_ai import Agent

from backend.config import get_model
from backend.mcp_toolset import mcp_toolset_for
from backend.models import FacilitiesFinding

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "facilities.md"

ALLOWED_TOOLS = {"get_desk_today", "get_lease", "get_cash_account"}

facilities_agent = Agent(
    get_model(),
    output_type=FacilitiesFinding,
    system_prompt=PROMPT_PATH.read_text(),
    name="facilities_agent",
    toolsets=[mcp_toolset_for("facilities", ALLOWED_TOOLS)],
)
