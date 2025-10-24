# -*- coding: utf-8 -*-
"""
Simple MCP Demo - No Client Needed
===================================

This script demonstrates MCP servers without needing a client.
Just run the server and it will show you how it works!
"""

import sys
import io

# Force UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("""
===================================================================
                   MCP TUTORIAL - SIMPLE DEMO
===================================================================

Welcome to the MCP (Model Context Protocol) Tutorial!

MCP allows AI assistants like Claude Desktop to access YOUR tools and data.

This tutorial has 3 working MCP servers:

1. Calculator Server (basic/simple_mcp_server.py)
   - Tools: add, multiply, power
   - Perfect for learning MCP basics

2. Weather Server (tools/weather_mcp_server.py)
   - Tools: get_weather, forecast, compare, save_alert
   - Shows advanced patterns

3. File Explorer Server (resources/file_explorer_server.py)
   - Resources: Local files (.txt, .json, .py)
   - Tools: search_files, count_lines, get_file_info
   - Shows resources (not just tools)

===================================================================

HOW TO USE:
-----------

Option 1: Test Servers Individually
---------------------------------───
Run any server directly to see it start:

  python basic/simple_mcp_server.py
  python tools/weather_mcp_server.py
  python resources/file_explorer_server.py

The server will start and wait for connections.
Press Ctrl+C to stop.

Option 2: Use with Claude Desktop
---------------------------------─
1. Copy claude_desktop_config.example.json
2. Update paths to absolute paths on your system
3. Save to Claude Desktop config location:
   Windows: %%APPDATA%%\\Claude\\claude_desktop_config.json
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
4. Restart Claude Desktop
5. Ask Claude: "What tools do you have?"

Option 3: Build Your Own Server
----------------------──────────
Use the examples as templates to build your own MCP server!
See README.md for a complete tutorial.

===================================================================

QUICK DEMONSTRATION:
-----------─────────

Let me show you what an MCP server looks like internally...
""")

import sys

print("\nCreating a mini calculator MCP server...")
print("-" * 70)

# Simulate MCP server structure
class MiniCalculator:
    """A simplified version of an MCP server to show the concept."""

    def __init__(self):
        self.name = "mini-calculator"

    def list_tools(self):
        """List available tools."""
        return [
            {
                "name": "add",
                "description": "Add two numbers",
                "parameters": ["a", "b"]
            },
            {
                "name": "multiply",
                "description": "Multiply two numbers",
                "parameters": ["a", "b"]
            }
        ]

    def call_tool(self, name, arguments):
        """Execute a tool."""
        if name == "add":
            return arguments["a"] + arguments["b"]
        elif name == "multiply":
            return arguments["a"] * arguments["b"]
        else:
            return f"Unknown tool: {name}"

# Demo the concept
calc = MiniCalculator()

print(f"\nServer created: {calc.name}")
print(f"\nAvailable tools:")
for tool in calc.list_tools():
    print(f"   - {tool['name']}: {tool['description']}")
    print(f"     Parameters: {', '.join(tool['parameters'])}")

print(f"\nTesting the tools:")
print(f"\n   Calling: add(a=10, b=5)")
result1 = calc.call_tool("add", {"a": 10, "b": 5})
print(f"   Result: {result1}")

print(f"\n   Calling: multiply(a=7, b=8)")
result2 = calc.call_tool("multiply", {"a": 7, "b": 8})
print(f"   Result: {result2}")

print("\n" + "-" * 70)
print("\nThis is the CORE CONCEPT of MCP!")
print("""
1. Server defines tools (functions AI can call)
2. AI lists available tools
3. AI calls a tool with arguments
4. Server executes and returns result

The REAL MCP servers in this tutorial work the same way,
but use the standardized MCP protocol so they work with
Claude Desktop and other MCP-compatible AI assistants!

===================================================================

NEXT STEPS:
-----------

1. Read README.md for the full tutorial
2. Read QUICKSTART.md to get started in 5 minutes
3. Read MCP_EXPLAINED.md for deep understanding
4. Try running: python basic/simple_mcp_server.py
5. Connect to Claude Desktop!

===================================================================

TROUBLESHOOTING:
-----------─────

If you get "ModuleNotFoundError: No module named 'mcp'":
  pip install mcp

If paths don't work (spaces in folder names):
  Use absolute paths or the run_*.bat scripts

Need help?
  Check TESTING_GUIDE.md for complete testing instructions

===================================================================

Happy building!

Press Enter to exit...
""")

try:
    input()
except:
    pass
