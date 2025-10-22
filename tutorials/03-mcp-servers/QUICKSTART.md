# MCP Quick Start Guide

Get up and running with MCP servers in 5 minutes!

## Step 1: Install Dependencies

```bash
cd tutorials/03-mcp-servers
pip install -r requirements.txt
```

Or install manually:
```bash
pip install mcp
```

## Step 2: Run Your First Server

Open a terminal and run:

```bash
python basic/simple_mcp_server.py
```

You should see:
```
============================================================
SIMPLE MCP SERVER - Calculator
============================================================
Available tools: add, multiply, power
```

**Leave this running!** The server is now waiting for connections.

## Step 3: Test with the Client

Open a **new terminal** (keep the server running) and run:

```bash
python client/mcp_client_example.py
```

Choose option `1` to run all demos.

You'll see:
- ✅ Client connecting to server
- 📋 List of available tools
- 🛠️ Tools being called with results

## Step 4: Try Interactive Mode

```bash
python client/mcp_client_example.py
```

Choose option `2` for interactive mode, then:
1. Select a server (calculator, weather, or file explorer)
2. Choose "Call a tool"
3. Select which tool to use
4. Enter arguments as JSON

Example for calculator `add` tool:
```json
{"a": 10, "b": 5}
```

## Step 5: Explore Other Servers

### Weather Server
```bash
# Terminal 1
python tools/weather_mcp_server.py

# Terminal 2
python client/mcp_client_example.py
# Choose option 2, then server 2
```

Try calling:
- `get_current_weather` with `{"city": "New York", "units": "fahrenheit"}`
- `compare_weather` with `{"city1": "New York", "city2": "London"}`

### File Explorer Server
```bash
# Terminal 1
python resources/file_explorer_server.py

# Terminal 2
python client/mcp_client_example.py
# Choose option 2, then server 3
```

Try calling:
- `search_files` with `{"pattern": "*.py"}`
- `get_file_info` with `{"filename": "README.md"}`

## Step 6: Connect to Claude Desktop (Optional)

### Windows

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add your server configuration:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:/Users/YOUR_USERNAME/llmapp/AI-Agents-from-scratch/tutorials/03-mcp-servers/basic/simple_mcp_server.py"
      ]
    }
  }
}
```

3. **Replace `YOUR_USERNAME`** with your actual Windows username
4. Restart Claude Desktop
5. Ask Claude: "Add 10 and 5"

### macOS

1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add your server configuration (same as above, but with macOS paths)
3. Restart Claude Desktop

### Verify It's Working

Ask Claude:
- "What tools do you have access to?"
- "Use the calculator to add 25 and 17"
- "What's the weather in Tokyo?"

Claude will automatically use your MCP servers!

## Common Issues

### "ModuleNotFoundError: No module named 'mcp'"
```bash
pip install mcp
```

### Server exits immediately
- Check for syntax errors
- Make sure you're in the correct directory
- Run with: `python -u server.py` to see all output

### Client can't connect
- Make sure server is still running
- Check the server path is correct
- Try running both in the same directory

### Claude Desktop doesn't see the server
- Check config file path is correct
- Verify JSON syntax (use a JSON validator)
- Make sure paths use forward slashes (`/`) not backslashes
- Restart Claude Desktop completely

## Next Steps

1. ✅ Read the [full README](README.md) for detailed explanations
2. ✅ Modify the calculator server - add subtraction and division
3. ✅ Build your own MCP server for a real use case
4. ✅ Check the code comments in each example

## Quick Reference

### Server Template
```python
from mcp.server import Server
import mcp.server.stdio

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [...]

@server.call_tool()
async def call_tool(name, arguments):
    return [...]

# Run server
async with mcp.server.stdio.stdio_server() as (r, w):
    await server.run(r, w, server.create_initialization_options())
```

### Testing a Server
```bash
# Run server
python my_server.py

# Test with client
python client/mcp_client_example.py
```

### Available Examples

| Example | File | What it teaches |
|---------|------|-----------------|
| Calculator | `basic/simple_mcp_server.py` | Basic tools |
| Weather | `tools/weather_mcp_server.py` | Advanced tools |
| File Explorer | `resources/file_explorer_server.py` | Resources |
| Client | `client/mcp_client_example.py` | Testing servers |

Happy building! 🚀
