from mcp.server.fastmcp import FastMCP
from registry import ToolRegistry
from schemas import CalculatorTool, WeatherTool

mcp = FastMCP("MyToolSuite")
mcp = FastMCP(
    "MyToolSuite",
    host="0.0.0.0",
    port=8000
)

registry = ToolRegistry(mcp)

registry.register_tool(CalculatorTool())
registry.register_tool(WeatherTool())

if __name__ == '__main__':
    mcp.run(transport="streamable-http", mount_path="/mcp")