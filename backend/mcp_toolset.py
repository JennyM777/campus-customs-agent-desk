"""The only way any agent reaches shop data: a toolset wired to our MCP server.

No agent file may query data/campus_customs_new.db directly. Every fact an
agent uses comes from a call through mcp_server/server.py over MCP.
"""

from pathlib import Path

from pydantic_ai import RunContext
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.tools import ToolDefinition

SERVER_SCRIPT = Path(__file__).resolve().parent.parent / "mcp_server" / "server.py"


def mcp_toolset_for(agent_name: str, allowed_tools: set[str]) -> MCPToolset:
    """Connect to the Campus Customs MCP server, restricted to one agent's allowed tool names."""
    transport = StdioTransport(command="python3", args=[str(SERVER_SCRIPT)])
    toolset = MCPToolset(transport, id=f"campus-customs-mcp-{agent_name}")

    async def _only_allowed(ctx: RunContext, tool_def: ToolDefinition) -> bool:
        return tool_def.name in allowed_tools

    return toolset.filtered(_only_allowed)
