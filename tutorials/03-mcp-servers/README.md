# Tutorial 03: MCP (Model Context Protocol) from Scratch

## What is MCP?

**MCP (Model Context Protocol)** is a standardized protocol that allows AI assistants to securely connect to external tools and data sources.

Think of it like this:
- **REST APIs** let web apps talk to servers
- **MCP** lets AI agents talk to tools and data

### Why MCP?

Before MCP, every AI tool integration was custom. Now:
- ✅ Standardized protocol
- ✅ Works with any MCP-compatible AI (Claude Desktop, etc.)
- ✅ Secure local access to files, databases, APIs
- ✅ Easy to build and share

---

## MCP Architecture

```
┌─────────────────┐
│   AI Assistant  │  (Client - e.g., Claude Desktop)
│   (MCP Client)  │
└────────┬────────┘
         │
         │ MCP Protocol
         │
┌────────┴────────┐
│   MCP Server    │  (Your Code)
│                 │
│  ┌───────────┐  │
│  │   Tools   │  │  Functions AI can call
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Resources │  │  Data AI can read
│  └───────────┘  │
└─────────────────┘
```

### Key Concepts

1. **Server**: Your Python code that exposes functionality
2. **Client**: The AI assistant (or your test client)
3. **Tools**: Functions the AI can call (like API endpoints)
4. **Resources**: Data the AI can read (like files or DB records)

---

## Tutorial Structure

This tutorial contains 4 complete examples:

### 1. **Basic Server** - Simple Calculator
- **File**: `basic/simple_mcp_server.py`
- **What it teaches**: Basic MCP server structure, tools
- **Tools**: add, multiply, power
- **Complexity**: ⭐ Beginner

### 2. **Advanced Tools** - Weather Service
- **File**: `tools/weather_mcp_server.py`
- **What it teaches**: Complex tools, real-world patterns
- **Tools**: get_current_weather, get_forecast, compare_weather, save_weather_alert
- **Complexity**: ⭐⭐ Intermediate

### 3. **Resources** - File Explorer
- **File**: `resources/file_explorer_server.py`
- **What it teaches**: Exposing data as resources, URIs
- **Resources**: Local files (.txt, .json, .py)
- **Tools**: search_files, count_lines, get_file_info
- **Complexity**: ⭐⭐ Intermediate

### 4. **Client** - MCP Test Client
- **File**: `client/mcp_client_example.py`
- **What it teaches**: How to consume MCP servers
- **Features**: Connect to servers, call tools, read resources
- **Complexity**: ⭐⭐⭐ Advanced

---

## Quick Start

### Installation

```bash
# Install MCP package
pip install mcp

# Install async dependencies
pip install asyncio
```

### Run Your First MCP Server

```bash
# 1. Run the calculator server
python tutorials/03-mcp-servers/basic/simple_mcp_server.py

# The server will start and wait for connections
# (Press Ctrl+C to stop)
```

### Test with the MCP Client

```bash
# 2. In another terminal, run the client
python tutorials/03-mcp-servers/client/mcp_client_example.py

# Choose option 1 to run all demos automatically
# Or option 2 for interactive mode
```

---

## Example 1: Calculator Server

The simplest MCP server - exposes basic math operations.

**File**: [basic/simple_mcp_server.py](basic/simple_mcp_server.py)

```python
# Key parts of the code:

# 1. Create server
server = Server("simple-calculator-server")

# 2. Define tools
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={...}
        )
    ]

# 3. Handle tool calls
@server.call_tool()
async def call_tool(name, arguments):
    if name == "add":
        return a + b
```

**Try it:**
```bash
python tutorials/03-mcp-servers/basic/simple_mcp_server.py
```

---

## Example 2: Weather Server

A more realistic server with multiple tools and data processing.

**File**: [tools/weather_mcp_server.py](tools/weather_mcp_server.py)

**Features:**
- Multiple tools with different purposes
- JSON data handling
- File I/O (saving alerts)
- Simulated API (weather database)

**Tools:**
1. `get_current_weather` - Get weather for a city
2. `get_forecast` - Get 3-day forecast
3. `compare_weather` - Compare two cities
4. `save_weather_alert` - Save alerts to disk

**Try it:**
```bash
# Run the server
python tutorials/03-mcp-servers/tools/weather_mcp_server.py

# Test with client
python tutorials/03-mcp-servers/client/mcp_client_example.py
# Choose option 1, then demo 2
```

---

## Example 3: File Explorer Server

Shows how to expose **resources** (data) not just tools (functions).

**File**: [resources/file_explorer_server.py](resources/file_explorer_server.py)

**Features:**
- Exposes local files as MCP resources
- AI can list and read files
- URI-based resource identification
- Security checks (root directory restriction)

**Resources:**
- All `.txt` files in directory
- All `.json` files
- All `.py` files

**Tools:**
- `search_files` - Find files by pattern
- `count_lines` - Count lines in file
- `get_file_info` - Get file metadata

**Try it:**
```bash
# Run with current directory
python tutorials/03-mcp-servers/resources/file_explorer_server.py

# Or specify a directory
python tutorials/03-mcp-servers/resources/file_explorer_server.py /path/to/folder
```

---

## Example 4: MCP Client

Learn how AI assistants interact with MCP servers.

**File**: [client/mcp_client_example.py](client/mcp_client_example.py)

**Features:**
- Connect to any MCP server
- List available tools and resources
- Call tools with arguments
- Read resources
- Interactive testing mode

**Automatic Demo:**
```bash
python tutorials/03-mcp-servers/client/mcp_client_example.py
# Choose option 1
```

**Interactive Mode:**
```bash
python tutorials/03-mcp-servers/client/mcp_client_example.py
# Choose option 2
# Then select a server and interact with it
```

---

## Tools vs Resources

### Tools (Functions AI Can Call)

```python
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="calculate_sum",
            description="Add numbers",
            inputSchema={...}
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "calculate_sum":
        return sum(arguments["numbers"])
```

**Use tools for:**
- Actions (save, delete, update)
- Computations (calculate, analyze)
- API calls (fetch, search)

### Resources (Data AI Can Read)

```python
@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="file:///path/to/file.txt",
            name="My File",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def read_resource(uri):
    return open(uri).read()
```

**Use resources for:**
- Files (documents, configs)
- Database records
- API endpoints
- Live data streams

---

## Connecting to Claude Desktop

To use your MCP server with Claude Desktop:

### 1. Create a config file

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Content:**
```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:/Users/YourName/path/to/tutorials/03-mcp-servers/basic/simple_mcp_server.py"
      ]
    },
    "weather": {
      "command": "python",
      "args": [
        "C:/Users/YourName/path/to/tutorials/03-mcp-servers/tools/weather_mcp_server.py"
      ]
    }
  }
}
```

### 2. Restart Claude Desktop

### 3. Test it!

Ask Claude:
- "Add 10 and 5" (uses calculator server)
- "What's the weather in New York?" (uses weather server)

Claude will automatically detect and use your MCP servers!

---

## Building Your Own MCP Server

### Basic Template

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

class MyMCPServer:
    def __init__(self):
        self.server = Server("my-server-name")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="my_tool",
                    description="What this tool does",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string"}
                        },
                        "required": ["param1"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name, arguments):
            if name == "my_tool":
                # Your logic here
                result = do_something(arguments["param1"])
                return [TextContent(type="text", text=result)]

    async def run(self):
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

if __name__ == "__main__":
    server = MyMCPServer()
    asyncio.run(server.run())
```

### Step-by-Step

1. **Create Server**: `Server("your-server-name")`
2. **Define Tools**: Use `@server.list_tools()` decorator
3. **Handle Calls**: Use `@server.call_tool()` decorator
4. **Run Server**: Use `stdio_server()` for communication
5. **Test**: Use the client or Claude Desktop

---

## Common Use Cases

### 1. **Local File Access**
Give AI access to your files (like the file explorer example)

### 2. **Database Integration**
Query databases, fetch records

### 3. **API Wrapper**
Wrap external APIs (weather, stocks, news)

### 4. **System Tools**
Git operations, file manipulation, shell commands

### 5. **Custom Business Logic**
Calculations, data processing, workflows

---

## Debugging Tips

### Server Not Starting?

```bash
# Check MCP is installed
pip show mcp

# Run with verbose output
python your_server.py 2>&1 | tee server.log
```

### Client Can't Connect?

```bash
# Make sure server path is correct
python tutorials/03-mcp-servers/client/mcp_client_example.py

# Check server is running
ps aux | grep python
```

### Tool Not Working?

1. Check tool name matches exactly
2. Verify inputSchema is valid JSON Schema
3. Test arguments with the client
4. Check return type is `list[TextContent]`

---

## Advanced Topics

### Error Handling

```python
@server.call_tool()
async def call_tool(name, arguments):
    try:
        result = risky_operation(arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### Validation

```python
def validate_arguments(args, required_fields):
    for field in required_fields:
        if field not in args:
            raise ValueError(f"Missing required field: {field}")
```

### Logging

```python
import sys

# Log to stderr (stdout is for MCP protocol)
print(f"Processing request: {name}", file=sys.stderr)
```

---

## Next Steps

1. ✅ Run all the example servers
2. ✅ Test them with the client
3. ✅ Modify the calculator server (add new operations)
4. ✅ Build your own MCP server for a real use case
5. ✅ Connect to Claude Desktop

---

## Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Examples**: This tutorial folder!

---

## Troubleshooting

### Import Error: No module named 'mcp'
```bash
pip install mcp
```

### Server exits immediately
- Make sure you're running the server correctly
- Check for syntax errors
- Look at stderr output

### Claude Desktop doesn't see server
- Check config file location
- Verify JSON syntax
- Restart Claude Desktop
- Check server path is absolute

---

## Summary

You've learned:
- ✅ What MCP is and why it's useful
- ✅ How to build MCP servers (3 examples)
- ✅ How to create tools (functions AI can call)
- ✅ How to expose resources (data AI can read)
- ✅ How to test servers with a client
- ✅ How to connect to Claude Desktop

**MCP unlocks powerful integrations between AI and your local tools/data!**

Start building your own MCP servers and give AI superpowers! 🚀
