"""
AI Notes Assistant - Complete End-to-End MCP Application
=========================================================

This is a COMPLETE, RUNNABLE application that demonstrates the full
MCP + LLM workflow. Run this file to experience how MCP enables
powerful AI applications.

What This Does:
---------------
- Starts an MCP server (notes database)
- Connects an LLM to it via MCP
- Provides a natural language interface for note-taking

Example Interactions:
--------------------
User: "Save a note about Python decorators"
AI: Uses create_note tool -> "Created note #1: Python Decorators"

User: "What notes do I have about Python?"
AI: Uses search_notes tool -> Shows matching notes

User: "Delete note 1"
AI: Uses delete_note tool -> "Deleted note #1"

Run: python tutorials/03-mcp-servers/practical/ai_notes_assistant.py
"""

import asyncio
import json
import os
import sys
from typing import Optional

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()


class AINotesAssistant:
    """
    A complete AI-powered notes assistant using MCP.

    This class demonstrates the full pattern:
    1. Connect to MCP server
    2. Get tools and convert to LLM format
    3. Handle conversation with tool calling
    4. Execute tools and return results
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()
        self.session: Optional[ClientSession] = None
        self.tools = []
        self._openai_tools = []
        self.conversation_history = []
        self._context_stack = []

        self.system_prompt = """You are an intelligent notes assistant. You help users manage their personal notes database.

You have access to these tools:
- create_note: Create a new note with title, content, and optional tags
- search_notes: Search notes by keyword
- get_note: Get a specific note by ID
- update_note: Update an existing note
- delete_note: Delete a note
- list_notes: List all notes
- get_stats: Get database statistics

Guidelines:
- When creating notes, suggest good titles if not provided
- Use appropriate tags to help organize notes
- When searching, try different keywords if the first search fails
- Always confirm destructive actions (delete) before proceeding
- Be conversational and helpful

Examples of natural language you should understand:
- "Remember that the meeting is at 3pm" -> create_note
- "What did I write about Python?" -> search_notes
- "Show me my notes" -> list_notes
- "Update note 5 to add more details" -> update_note
- "Remove the old todo list" -> (ask for note ID, then delete_note)
"""

    async def connect(self, server_script_path: str):
        """Connect to the notes MCP server."""
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

        tools_result = await self.session.list_tools()
        self.tools = tools_result.tools
        self._openai_tools = self._convert_to_openai_format()

        return len(self.tools)

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

    def _convert_to_openai_format(self) -> list[dict]:
        """Convert MCP tools to OpenAI function format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in self.tools
        ]

    async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool via MCP and return the result."""
        if not self.session:
            return "Error: Not connected to server"

        try:
            result = await self.session.call_tool(tool_name, arguments)
            response = ""
            for content in result.content:
                if content.type == "text":
                    response += content.text + "\n"
            return response.strip()
        except Exception as e:
            return f"Tool error: {str(e)}"

    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return the assistant's response.

        This handles the full flow:
        1. Send message to LLM with tools
        2. If LLM wants to use tools, execute them
        3. Return final response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages for LLM
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._openai_tools
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            # Execute each tool call
            tool_messages = []

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Show what we're doing
                print(f"    [Calling {tool_name}...]")

                # Execute tool
                result = await self._execute_tool(tool_name, tool_args)

                tool_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result
                })

            # Add tool call and results to conversation
            messages.append(assistant_message)
            messages.extend(tool_messages)

            # Get final response from LLM
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            final_content = final_response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_content
            })

            return final_content

        else:
            # No tools used, just add response to history
            content = assistant_message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            return content

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []


def print_banner():
    """Print the application banner."""
    print("\n" + "=" * 70)
    print(r"""
       _    ___   _   _       _              _            _     _              _
      / \  |_ _| | \ | | ___ | |_ ___  ___  / \   ___ ___(_)___| |_ __ _ _ __ | |_
     / _ \  | |  |  \| |/ _ \| __/ _ \/ __| / _ \ / __/ __| / __| __/ _` | '_ \| __|
    / ___ \ | |  | |\  | (_) | ||  __/\__ \/ ___ \\__ \__ \ \__ \ || (_| | | | | |_
   /_/   \_\___| |_| \_|\___/ \__\___||___/_/   \_\___/___/_|___/\__\__,_|_| |_|\__|
    """)
    print("=" * 70)
    print("Your AI-powered notes assistant using MCP (Model Context Protocol)")
    print("=" * 70)


def print_help():
    """Print help information."""
    print("""
Commands:
  /help     - Show this help message
  /reset    - Clear conversation history
  /tools    - List available tools
  /stats    - Show database statistics
  /quit     - Exit the application

Example prompts:
  - "Create a note about today's meeting"
  - "Save this code snippet: def hello(): print('world')"
  - "Find my notes about Python"
  - "List all my notes tagged with 'work'"
  - "Delete note #3"
  - "Update note #1 with new information"
""")


async def main():
    """Main application entry point."""
    print_banner()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nError: OPENAI_API_KEY not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  # or add to .env file")
        return

    # Initialize assistant
    print("\nInitializing AI Notes Assistant...")

    assistant = AINotesAssistant()

    # Connect to MCP server
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "notes_mcp_server.py"
    )

    try:
        num_tools = await assistant.connect(server_path)
        print(f"Connected to notes server with {num_tools} tools")
    except Exception as e:
        print(f"\nError connecting to MCP server: {e}")
        print("\nMake sure you have installed the required packages:")
        print("  pip install mcp openai python-dotenv")
        return

    # Main loop
    print_help()
    print("\n" + "-" * 70)
    print("Ready! Start chatting with your notes assistant.\n")

    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    cmd = user_input.lower()

                    if cmd in ["/quit", "/exit", "/q"]:
                        print("\nGoodbye! Your notes are saved.")
                        break

                    elif cmd == "/help":
                        print_help()
                        continue

                    elif cmd == "/reset":
                        assistant.reset_conversation()
                        print("Conversation history cleared.\n")
                        continue

                    elif cmd == "/tools":
                        print("\nAvailable tools:")
                        for tool in assistant.tools:
                            print(f"  - {tool.name}: {tool.description}")
                        print()
                        continue

                    elif cmd == "/stats":
                        response = await assistant.chat("Show me the database statistics")
                        print(f"\nAssistant: {response}\n")
                        continue

                    else:
                        print(f"Unknown command: {cmd}. Type /help for commands.\n")
                        continue

                # Regular chat
                response = await assistant.chat(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    finally:
        # Cleanup
        await assistant.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
