"""Boss agent: reads a ticket via MCP and delegates to the specialists it needs.

Every delegated sub-agent run is appended to output/audit_trail.json for audit.
"""

from pathlib import Path

from pydantic_ai import Agent, RunContext

from backend.agents.accounting_agent import accounting_agent
from backend.agents.customer_service_agent import customer_service_agent
from backend.agents.facilities_agent import facilities_agent
from backend.agents.inventory_agent import inventory_agent
from backend.audit import log_agent_run
from backend.config import get_model
from backend.mcp_toolset import mcp_toolset_for
from backend.models import BossDecision

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "boss.md"

ALLOWED_TOOLS = {"get_open_tickets", "get_ticket_details", "get_desk_today"}

boss_agent = Agent(
    get_model(),
    output_type=BossDecision,
    system_prompt=PROMPT_PATH.read_text(),
    name="boss_agent",
    deps_type=int,  # the ticket_id being handled, for audit logging
    toolsets=[mcp_toolset_for("boss", ALLOWED_TOOLS)],
)


@boss_agent.tool
async def delegate_to_inventory(ctx: RunContext[int], question: str) -> str:
    """Ask the Inventory agent a question (stock levels, sizes, vendor lead times)."""
    result = await inventory_agent.run(question, usage=ctx.usage)
    log_agent_run("inventory_agent", ctx.deps, result)
    return result.output.model_dump_json()


@boss_agent.tool
async def delegate_to_accounting(ctx: RunContext[int], question: str) -> str:
    """Ask the Accounting agent a question (cash balance, invoices, payment drafts)."""
    result = await accounting_agent.run(question, usage=ctx.usage)
    log_agent_run("accounting_agent", ctx.deps, result)
    return result.output.model_dump_json()


@boss_agent.tool
async def delegate_to_facilities(ctx: RunContext[int], question: str) -> str:
    """Ask the Facilities agent a question (lease terms, rent due dates)."""
    result = await facilities_agent.run(question, usage=ctx.usage)
    log_agent_run("facilities_agent", ctx.deps, result)
    return result.output.model_dump_json()


@boss_agent.tool
async def delegate_to_customer_service(ctx: RunContext[int], question: str) -> str:
    """Ask the Customer Service agent to draft a reply, given facts gathered so far."""
    result = await customer_service_agent.run(question, usage=ctx.usage)
    log_agent_run("customer_service_agent", ctx.deps, result)
    return result.output.model_dump_json()
