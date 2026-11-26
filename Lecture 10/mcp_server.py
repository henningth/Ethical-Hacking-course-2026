
"""
Simple MCP server for lecture 10 in the course Ethical Hacking.

This server only has one tool, which returns a greeting to the caller.
"""

from mcp.server.mcpserver import MCPServer

# Create MCP server
mcp = MCPServer("Hello World Server")


# Define a tool
@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


# Start server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")