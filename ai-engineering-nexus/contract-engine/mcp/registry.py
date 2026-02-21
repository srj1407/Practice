from base_tool import ToolBase
from mcp.server.fastmcp import FastMCP

class ToolRegistry():
    def __init__(self, mcp_server: FastMCP):
        self.server = mcp_server

    def register_tool(self, tool_instance: ToolBase):
        """Registers the tool and its pydantic schema with the MCP server"""

        @self.server.tool(name=tool_instance.name, description=tool_instance.description)
        async def tool_wrapper(params: tool_instance.args_schema):
            return await tool_instance.execute(**params.model_dump())