"""
Tutorial 03-A: Simple MCP Server from Scratch
==============================================

MCP (Model Context Protocol) is a standardized protocol that allows
AI assistants to securely connect to external tools and data sources.

This tutorial shows you how to build a basic MCP server that exposes
simple functionality to AI agents.

What is MCP?
------------
- A protocol for AI agents to interact with external tools
- Similar to how REST APIs work for web services
- Allows you to give AI access to local files, databases, APIs, etc.

MCP Components:
--------------
1. Server: Exposes tools and resources
2. Client: Consumes the server (usually the AI assistant)
3. Tools: Functions the AI can call
4. Resources: Data the AI can access
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


class SimpleMCPServer:
    """
    A basic MCP server that demonstrates core concepts.

    This server exposes a simple calculator tool that the AI can use.
    """

    def __init__(self):
        # Create MCP server instance
        self.server = Server("simple-calculator-server")

        # Register handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Register tool handlers with the MCP server."""

        # List available tools
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """
            This handler tells the AI what tools are available.
            The AI will see this list and can choose which tool to call.
            """
            return [
                Tool(
                    name="add",
                    description="Add two numbers together",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "First number"},
                            "b": {"type": "number", "description": "Second number"}
                        },
                        "required": ["a", "b"]
                    }
                ),
                Tool(
                    name="multiply",
                    description="Multiply two numbers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "First number"},
                            "b": {"type": "number", "description": "Second number"}
                        },
                        "required": ["a", "b"]
                    }
                ),
                Tool(
                    name="power",
                    description="Raise a number to a power (a^b)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "base": {"type": "number", "description": "Base number"},
                            "exponent": {"type": "number", "description": "Exponent"}
                        },
                        "required": ["base", "exponent"]
                    }
                )
            ]

        # Call a tool
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """
            This handler executes the tool when the AI calls it.

            Args:
                name: The name of the tool to call
                arguments: The arguments passed by the AI

            Returns:
                The result of the tool execution
            """

            if name == "add":
                a = arguments.get("a")
                b = arguments.get("b")
                result = a + b
                return [
                    TextContent(
                        type="text",
                        text=f"The sum of {a} and {b} is {result}"
                    )
                ]

            elif name == "multiply":
                a = arguments.get("a")
                b = arguments.get("b")
                result = a * b
                return [
                    TextContent(
                        type="text",
                        text=f"The product of {a} and {b} is {result}"
                    )
                ]

            elif name == "power":
                base = arguments.get("base")
                exponent = arguments.get("exponent")
                result = base ** exponent
                return [
                    TextContent(
                        type="text",
                        text=f"{base} raised to the power of {exponent} is {result}"
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server using stdio transport."""
        # Use stdio for communication (standard input/output)
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("🚀 Simple MCP Server started!", file=sys.stderr)
            print("Available tools: add, multiply, power", file=sys.stderr)
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# For standalone testing
async def main():
    """Run the server."""
    import sys
    server = SimpleMCPServer()
    await server.run()


if __name__ == "__main__":
    import sys
    print("="*60, file=sys.stderr)
    print("SIMPLE MCP SERVER - Calculator", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("\nThis is an MCP server that exposes calculator tools.", file=sys.stderr)
    print("It communicates via stdio (standard input/output).", file=sys.stderr)
    print("\nTo use this server:", file=sys.stderr)
    print("1. Install: pip install mcp", file=sys.stderr)
    print("2. Configure it in your MCP client (like Claude Desktop)", file=sys.stderr)
    print("3. The AI will be able to use these calculator tools!", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("", file=sys.stderr)

    asyncio.run(main())
