# MCP Tutorial - What You've Built

## Overview

You now have a **complete MCP (Model Context Protocol) tutorial** with 4 working examples that teach you how to build servers that AI assistants can use!

---

## Files Created

### 📁 Directory Structure

```
tutorials/03-mcp-servers/
├── README.md                              # Complete tutorial guide
├── QUICKSTART.md                          # 5-minute getting started
├── TUTORIAL_SUMMARY.md                    # This file
├── requirements.txt                       # Dependencies
├── claude_desktop_config.example.json     # Config for Claude Desktop
│
├── basic/
│   └── simple_mcp_server.py              # Example 1: Calculator server
│
├── tools/
│   └── weather_mcp_server.py             # Example 2: Weather tools
│
├── resources/
│   └── file_explorer_server.py           # Example 3: File resources
│
└── client/
    └── mcp_client_example.py             # Example 4: Test client
```

---

## What Each Example Teaches

### 1. **Simple Calculator Server** ⭐ Beginner
**File**: `basic/simple_mcp_server.py`

**Concepts:**
- Basic MCP server structure
- Creating tools (functions AI can call)
- Input schema definition
- Tool execution handlers

**Tools Provided:**
- `add(a, b)` - Add two numbers
- `multiply(a, b)` - Multiply two numbers
- `power(base, exponent)` - Raise to power

**Try it:**
```bash
python basic/simple_mcp_server.py
```

---

### 2. **Weather Service Server** ⭐⭐ Intermediate
**File**: `tools/weather_mcp_server.py`

**Concepts:**
- Multiple complex tools
- Working with JSON data
- File I/O operations
- Simulated API integration

**Tools Provided:**
- `get_current_weather(city, units)` - Get current weather
- `get_forecast(city, days)` - Get multi-day forecast
- `compare_weather(city1, city2)` - Compare two cities
- `save_weather_alert(city, alert_type, message)` - Save alerts

**Try it:**
```bash
python tools/weather_mcp_server.py
```

---

### 3. **File Explorer Server** ⭐⭐ Intermediate
**File**: `resources/file_explorer_server.py`

**Concepts:**
- MCP Resources (not just tools!)
- URI-based resource identification
- Security (root directory restrictions)
- Both tools AND resources in one server

**Resources Provided:**
- All `.txt` files in directory
- All `.json` files
- All `.py` files

**Tools Provided:**
- `search_files(pattern)` - Find files by glob pattern
- `count_lines(filename)` - Count lines in a file
- `get_file_info(filename)` - Get file metadata

**Try it:**
```bash
python resources/file_explorer_server.py
```

---

### 4. **MCP Test Client** ⭐⭐⭐ Advanced
**File**: `client/mcp_client_example.py`

**Concepts:**
- How MCP clients work
- Connecting to servers
- Listing tools and resources
- Calling tools with arguments
- Reading resources

**Features:**
- Automatic demo mode (tests all servers)
- Interactive mode (manual testing)
- Connects to any MCP server

**Try it:**
```bash
python client/mcp_client_example.py
```

---

## Quick Start (5 Minutes)

### Terminal 1: Run a Server
```bash
cd tutorials/03-mcp-servers
python basic/simple_mcp_server.py
```

### Terminal 2: Test with Client
```bash
python client/mcp_client_example.py
# Choose option 1 for automatic demo
```

---

## Connect to Claude Desktop

### Step 1: Find your config file

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Step 2: Add server configuration

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:/Users/YOUR_USERNAME/llmapp/AI-Agents-from-scratch/tutorials/03-mcp-servers/basic/simple_mcp_server.py"
      ]
    },
    "weather": {
      "command": "python",
      "args": [
        "C:/Users/YOUR_USERNAME/llmapp/AI-Agents-from-scratch/tutorials/03-mcp-servers/tools/weather_mcp_server.py"
      ]
    }
  }
}
```

### Step 3: Restart Claude Desktop

### Step 4: Test!

Ask Claude:
- "What tools do you have?"
- "Add 10 and 5"
- "What's the weather in New York?"

---

## Key Concepts You Learned

### 1. **MCP Architecture**
```
AI Assistant (Client)
        ↓
   MCP Protocol
        ↓
   Your Server
        ↓
   Tools & Resources
```

### 2. **Tools vs Resources**

**Tools** (Functions):
- AI can CALL them
- Like API endpoints
- Used for actions (save, calculate, fetch)

**Resources** (Data):
- AI can READ them
- Like files or database records
- Identified by URIs (`file:///path/to/file`)

### 3. **Server Structure**

```python
from mcp.server import Server

# 1. Create server
server = Server("my-server")

# 2. List tools
@server.list_tools()
async def list_tools():
    return [Tool(...)]

# 3. Handle calls
@server.call_tool()
async def call_tool(name, arguments):
    # Your logic
    return [TextContent(...)]

# 4. Run server
async with stdio_server() as (r, w):
    await server.run(r, w, ...)
```

---

## What You Can Do Now

### ✅ Immediate Next Steps

1. **Run all examples** - See them in action
2. **Modify calculator** - Add subtraction, division
3. **Add new weather tool** - e.g., `get_air_quality(city)`
4. **Connect to Claude Desktop** - Use your servers with Claude!

### 🚀 Build Your Own Server

Ideas for your own MCP servers:
- **Database server** - Query your database
- **Git server** - Git operations (status, commit, log)
- **Email server** - Send/read emails
- **Todo server** - Manage tasks
- **System info server** - CPU, memory, disk usage
- **API wrapper** - Wrap any external API

### 📚 Learn More

- **MCP Spec**: https://spec.modelcontextprotocol.io/
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Examples**: Browse the code in this tutorial!

---

## Common Patterns

### Pattern 1: Simple Calculator-style Tool
```python
Tool(
    name="add",
    description="Add numbers",
    inputSchema={
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
)
```

### Pattern 2: File Resource
```python
Resource(
    uri="file:///path/to/file.txt",
    name="My File",
    description="A text file",
    mimeType="text/plain"
)
```

### Pattern 3: Error Handling
```python
@server.call_tool()
async def call_tool(name, arguments):
    try:
        result = do_something(arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
```

---

## Troubleshooting

### Server won't start
```bash
# Check MCP is installed
pip install mcp

# Run with full output
python -u your_server.py
```

### Client can't connect
- Make sure server is running
- Check server path is correct
- Verify both use same Python environment

### Claude Desktop doesn't see server
- Check config file path
- Verify JSON syntax
- Use absolute paths
- Restart Claude Desktop completely

---

## Summary

You've successfully built:
- ✅ 3 MCP servers (calculator, weather, file explorer)
- ✅ 1 MCP client (test tool)
- ✅ Understanding of Tools vs Resources
- ✅ Ready to connect to Claude Desktop
- ✅ Knowledge to build your own servers!

**MCP unlocks powerful integrations between AI and your local tools!**

Start building and give AI superpowers! 🚀

---

## Next Steps in Your Learning Journey

1. Complete this MCP tutorial
2. Move to [Tutorial 04: Tool Integration](../04-tools/)
3. Learn [Tutorial 05: Planning and Reasoning](../05-planning/)
4. Master [Tutorial 06: Advanced Features](../06-advanced/)

Happy building! 🎉
