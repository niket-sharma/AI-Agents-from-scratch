# Practical MCP Tutorial: Build Real AI Applications

This folder contains **practical, end-to-end MCP examples** that show you how to build real AI applications with MCP.

---

## The Missing Piece

Most MCP tutorials show you how to build servers... but then stop there. They don't show you how to actually **use those servers with LLMs to build useful applications**.

This tutorial fills that gap.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MCP Application Architecture                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐     ┌────────────────────┐     ┌─────────────────┐  │
│   │   User   │────>│     LLM Client     │────>│   MCP Server    │  │
│   │  Input   │     │  (OpenAI/Claude)   │     │  (Your Tools)   │  │
│   └──────────┘     └────────────────────┘     └─────────────────┘  │
│        │                    │                          │            │
│        │                    │  "Use tool X"            │            │
│        │                    │─────────────────────────>│            │
│        │                    │                          │            │
│        │                    │        Result            │            │
│        │                    │<─────────────────────────│            │
│        │                    │                          │            │
│        │     Response       │                          │            │
│        │<───────────────────│                          │            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `notes_mcp_server.py` | MCP server with SQLite database |
| `llm_mcp_client.py` | Bridge between LLMs and MCP servers |
| `ai_notes_assistant.py` | Complete runnable application |

---

## Quick Start

```bash
# 1. Install dependencies
pip install mcp openai python-dotenv

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Run the application
python tutorials/03-mcp-servers/practical/ai_notes_assistant.py
```

---

## Example Session

```
You: Save a note about Python list comprehensions
    [Calling create_note...]
Assistant: Created note #1 with your content about list comprehensions.

You: Find my notes about Python
    [Calling search_notes...]
Assistant: Found 1 note matching "Python":
  #1: Python List Comprehensions [programming, python]

You: Show me the database stats
    [Calling get_stats...]
Assistant: You have 1 note with 2 unique tags.
```

---

## Learning Path

1. **Read** `notes_mcp_server.py` - Understand MCP server structure
2. **Read** `llm_mcp_client.py` - See how to connect LLMs to MCP
3. **Run** `ai_notes_assistant.py` - Experience the complete application
4. **Modify** - Add your own tools or build a new server

---

## Key Concepts Demonstrated

### MCP Server Pattern
```python
class MyMCPServer:
    def __init__(self):
        self.server = Server("my-server")
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [Tool(name="my_tool", ...)]

        @self.server.call_tool()
        async def call_tool(name, arguments):
            # Execute tool and return result
            return [TextContent(type="text", text=result)]
```

### LLM Integration Pattern
```python
# Connect to MCP server
client = LLMMCPClient()
await client.connect("server.py")

# Chat with LLM - tools are called automatically
response = await client.chat("Use my tools to do something")
```

---

## Building Your Own

1. Copy `notes_mcp_server.py` as a template
2. Define your tools in `list_tools()`
3. Implement tool logic in `call_tool()`
4. Use `llm_mcp_client.py` to connect your LLM
5. Build an application like `ai_notes_assistant.py`

---

## Next Steps

- Try the other servers in `../basic/`, `../tools/`, `../resources/`
- Connect to Claude Desktop (see `../README.md`)
- Build your own MCP server for a real use case