from mcp.server.fastmcp import FastMCP
from registry import ToolRegistry
from schemas import CalculatorTool

mcp = FastMCP("MyToolSuite")

registry = ToolRegistry(mcp)

registry.register_tool(CalculatorTool())

if __name__ == '__main__':
    mcp.run(transport='stdio')