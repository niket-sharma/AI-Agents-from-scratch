"""
LLM-Integrated MCP Client
=========================

This is THE KEY MISSING PIECE in most MCP tutorials!

This module shows how to:
1. Connect to an MCP server
2. Get tool definitions from the server
3. Convert MCP tools to OpenAI/Claude function calling format
4. Let the LLM decide which tools to use
5. Execute tools and return results to the LLM

This bridges the gap between:
- MCP servers (expose tools)
- LLM applications (need to use those tools)

Architecture:
-------------
    User Input
        |
        v
    LLM (OpenAI/Claude)
        |
        | "I want to use tool X with args Y"
        v
    LLM-MCP Client (this file)
        |
        | MCP Protocol
        v
    MCP Server (tools)
        |
        v
    Result back to LLM
"""

import asyncio
import json
import os
from typing import Optional, Any
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()


class LLMMCPClient:
    """
    An MCP client that integrates with LLMs for tool calling.

    This is the bridge between MCP servers and LLM applications.
    It handles:
    - Connecting to MCP servers
    - Converting MCP tools to LLM function format
    - Executing tools when the LLM requests them
    - Returning results back to the LLM
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()
        self.session: Optional[ClientSession] = None
        self.tools = []
        self._openai_tools = []
        self._context_stack = []

    async def connect(self, server_script_path: str):
        """
        Connect to an MCP server.

        Args:
            server_script_path: Path to the MCP server Python script
        """
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        # Use context manager for stdio_client
        stdio_context = stdio_client(server_params)
        transport = await stdio_context.__aenter__()
        self._context_stack.append(stdio_context)

        self.read_stream, self.write_stream = transport

        # Create and initialize session
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        self._context_stack.append(self.session)

        await self.session.initialize()

        # Get available tools
        tools_result = await self.session.list_tools()
        self.tools = tools_result.tools

        # Convert to OpenAI format
        self._openai_tools = self._convert_tools_to_openai_format()

        return len(self.tools)

    def _convert_tools_to_openai_format(self) -> list[dict]:
        """
        Convert MCP tools to OpenAI function calling format.

        This is the key conversion that makes MCP tools usable by LLMs!

        MCP Tool Format:
        {
            "name": "tool_name",
            "description": "What the tool does",
            "inputSchema": { JSON Schema }
        }

        OpenAI Function Format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "What the tool does",
                "parameters": { JSON Schema }
            }
        }
        """
        openai_tools = []

        for tool in self.tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        return openai_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            The tool's response as a string
        """
        if not self.session:
            return "Error: Not connected to server"

        try:
            result = await self.session.call_tool(tool_name, arguments)

            # Extract text from result
            response_text = ""
            for content in result.content:
                if content.type == "text":
                    response_text += content.text + "\n"

            return response_text.strip()

        except Exception as e:
            return f"Error calling tool: {str(e)}"

    async def chat(self, user_message: str, conversation_history: list = None) -> str:
        """
        Send a message to the LLM with MCP tools available.

        This is where the magic happens:
        1. User sends a message
        2. LLM sees the available tools
        3. LLM decides if/which tool to use
        4. We execute the tool via MCP
        5. We return the result to the LLM
        6. LLM generates final response

        Args:
            user_message: The user's message
            conversation_history: Previous messages (optional)

        Returns:
            The assistant's response
        """
        if conversation_history is None:
            conversation_history = []

        # Build messages
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant with access to tools.
Use the available tools to help the user. When you use a tool,
explain what you're doing and share the results."""
            }
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        # Call LLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._openai_tools if self._openai_tools else None
        )

        assistant_message = response.choices[0].message

        # Check if the LLM wants to use a tool
        if assistant_message.tool_calls:
            # Process each tool call
            tool_results = []

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute the tool via MCP
                result = await self.call_tool(tool_name, tool_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result
                })

            # Send tool results back to LLM for final response
            messages.append(assistant_message)
            messages.extend(tool_results)

            # Get final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return final_response.choices[0].message.content

        else:
            # No tool call, just return the response
            return assistant_message.content

    async def disconnect(self):
        """Disconnect from the MCP server."""
        # Close contexts in reverse order
        while self._context_stack:
            ctx = self._context_stack.pop()
            try:
                await ctx.__aexit__(None, None, None)
            except Exception:
                pass
        self.session = None

    def get_tools_info(self) -> str:
        """Get a formatted string of available tools."""
        if not self.tools:
            return "No tools available"

        lines = [f"Available tools ({len(self.tools)}):"]
        for tool in self.tools:
            lines.append(f"  - {tool.name}: {tool.description}")
        return "\n".join(lines)


async def demo():
    """Demonstrate the LLM-MCP integration."""
    print("=" * 70)
    print(" LLM + MCP Integration Demo ".center(70, "="))
    print("=" * 70)

    # Create client
    client = LLMMCPClient(model="gpt-4o-mini")

    # Connect to the notes server
    server_path = "tutorials/03-mcp-servers/practical/notes_mcp_server.py"
    print(f"\nConnecting to MCP server: {server_path}")

    try:
        num_tools = await client.connect(server_path)
        print(f"Connected! Found {num_tools} tools")
        print("\n" + client.get_tools_info())

    except Exception as e:
        print(f"Error connecting: {e}")
        print("\nMake sure you have:")
        print("  1. Installed mcp: pip install mcp")
        print("  2. Set OPENAI_API_KEY in your environment")
        return

    # Demo conversation
    print("\n" + "=" * 70)
    print(" Demo Conversation ".center(70, "="))
    print("=" * 70)

    demo_messages = [
        "Create a note titled 'Python Tips' with content 'Use list comprehensions for cleaner code' and tag it 'programming,python'",
        "Create another note titled 'Meeting Notes' with content 'Discussed Q1 roadmap' and tag it 'work,meetings'",
        "Search for notes about Python",
        "List all my notes",
        "Get the statistics for my notes database"
    ]

    for msg in demo_messages:
        print(f"\nUser: {msg}")
        response = await client.chat(msg)
        print(f"\nAssistant: {response}")
        print("-" * 70)
        await asyncio.sleep(1)

    await client.disconnect()
    print("\nDemo complete!")


async def interactive():
    """Interactive chat with MCP tools."""
    print("=" * 70)
    print(" Interactive LLM + MCP Chat ".center(70, "="))
    print("=" * 70)

    # Get server path
    print("\nAvailable servers:")
    print("1. Notes Server (practical/notes_mcp_server.py)")
    print("2. Calculator Server (basic/simple_mcp_server.py)")
    print("3. Weather Server (tools/weather_mcp_server.py)")
    print("4. Custom path")

    choice = input("\nSelect server (1-4): ").strip()

    server_paths = {
        "1": "tutorials/03-mcp-servers/practical/notes_mcp_server.py",
        "2": "tutorials/03-mcp-servers/basic/simple_mcp_server.py",
        "3": "tutorials/03-mcp-servers/tools/weather_mcp_server.py"
    }

    if choice in server_paths:
        server_path = server_paths[choice]
    elif choice == "4":
        server_path = input("Enter server path: ").strip()
    else:
        print("Invalid choice")
        return

    # Connect
    client = LLMMCPClient()

    try:
        print(f"\nConnecting to {server_path}...")
        num_tools = await client.connect(server_path)
        print(f"Connected! Found {num_tools} tools")
        print("\n" + client.get_tools_info())
    except Exception as e:
        print(f"Error: {e}")
        return

    # Chat loop
    print("\n" + "-" * 70)
    print("Chat started. Type 'quit' to exit.\n")

    conversation = []

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if not user_input:
                continue

            response = await client.chat(user_input, conversation)
            print(f"\nAssistant: {response}\n")

            # Update conversation history
            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            break

    await client.disconnect()
    print("\nGoodbye!")


async def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print(" LLM + MCP Client ".center(70, "="))
    print("=" * 70)
    print("\nThis demonstrates how to connect LLMs to MCP servers.")
    print("\n1. Run demo (automated)")
    print("2. Interactive chat")

    choice = input("\nChoice (1 or 2): ").strip()

    if choice == "1":
        await demo()
    elif choice == "2":
        await interactive()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
