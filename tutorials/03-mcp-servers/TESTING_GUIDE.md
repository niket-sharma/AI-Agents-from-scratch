# MCP Server Testing Guide

This guide shows you exactly how to test each MCP server example.

---

## Prerequisites

```bash
# Make sure you're in the right directory
cd tutorials/03-mcp-servers

# Install dependencies
pip install mcp

# Verify installation
python -c "import mcp; print('MCP installed successfully!')"
```

---

## Test 1: Calculator Server

### Start the Server

**Terminal 1:**
```bash
python basic/simple_mcp_server.py
```

**Expected output:**
```
============================================================
SIMPLE MCP SERVER - Calculator
============================================================

This is an MCP server that exposes calculator tools.
It communicates via stdio (standard input/output).

Available tools: add, multiply, power
============================================================
```

**Server is now running!** (Leave this terminal open)

### Test with Client

**Terminal 2:**
```bash
python client/mcp_client_example.py
```

**Choose option 1** (Run all demos automatically)

**Expected output:**
```
======================================================================
 DEMO: Calculator MCP Server
======================================================================

🔌 Connecting to MCP server: tutorials/03-mcp-servers/basic/simple_mcp_server.py
✅ Connected to MCP server!

📋 Fetching available tools...
   Found 3 tools:

   1. add
      Description: Add two numbers together
      Parameters: a, b

   2. multiply
      Description: Multiply two numbers
      Parameters: a, b

   3. power
      Description: Raise a number to a power (a^b)
      Parameters: base, exponent

🛠️  Calling tool: add
    Arguments: {
      "a": 10,
      "b": 5
    }

✅ Tool Response:
------------------------------------------------------------
The sum of 10 and 5 is 15
------------------------------------------------------------
```

### Manual Testing (Interactive)

**Terminal 2:**
```bash
python client/mcp_client_example.py
```

**Choose option 2** (Interactive mode), then:
1. Enter `1` (Calculator Server)
2. Enter `1` (Call a tool)
3. Enter `1` (add tool)
4. Enter `{"a": 25, "b": 17}`

**Result:** Should show "The sum of 25 and 17 is 42"

---

## Test 2: Weather Server

### Start the Server

**Terminal 1:**
```bash
python tools/weather_mcp_server.py
```

**Expected output:**
```
============================================================
WEATHER MCP SERVER
============================================================

Available Tools:
  • get_current_weather - Get current weather for a city
  • get_forecast - Get weather forecast
  • compare_weather - Compare weather between cities
  • save_weather_alert - Save weather alerts

Server running... waiting for MCP client connection.
============================================================
```

### Test with Client

**Terminal 2:**
```bash
python client/mcp_client_example.py
```

**Choose option 1**, or for manual testing:

1. **Choose option 2** (Interactive)
2. **Enter `2`** (Weather Server)
3. **Enter `1`** (Call a tool)
4. **Enter `1`** (get_current_weather)
5. **Enter:** `{"city": "New York", "units": "fahrenheit"}`

**Expected result:**
```json
{
  "city": "New York",
  "temperature": "72°F",
  "condition": "Sunny",
  "humidity": "60%",
  "timestamp": "2024-..."
}
```

### Try Different Tools

**Get Forecast:**
```json
{"city": "Tokyo", "days": 3}
```

**Compare Weather:**
```json
{"city1": "New York", "city2": "London"}
```

**Save Alert:**
```json
{
  "city": "Miami",
  "alert_type": "storm",
  "message": "Hurricane warning in effect"
}
```

Check the `weather_alerts/` folder for saved alerts!

---

## Test 3: File Explorer Server

### Start the Server

**Terminal 1:**
```bash
python resources/file_explorer_server.py
```

**Expected output:**
```
============================================================
FILE EXPLORER MCP SERVER
============================================================

Root Directory: C:\Users\...\tutorials\03-mcp-servers

Resources:
  • Exposes .txt, .json, and .py files
  • AI can list and read these files

Tools:
  • search_files - Search by pattern
  • count_lines - Count lines in a file
  • get_file_info - Get file metadata

Server running...
============================================================
```

### Test with Client

**Terminal 2:**
```bash
python client/mcp_client_example.py
```

**Interactive test:**
1. Choose option `2`
2. Choose server `3`
3. Choose `1` (Call a tool)
4. Choose `1` (search_files)
5. Enter: `{"pattern": "*.py"}`

**Expected result:**
```json
{
  "pattern": "*.py",
  "matches": [
    "simple_mcp_server.py",
    "weather_mcp_server.py",
    "file_explorer_server.py",
    "mcp_client_example.py"
  ],
  "count": 4
}
```

### Test Resources

1. Choose `2` (Read a resource)
2. Select a resource from the list
3. See the file contents displayed

---

## Automated Test Suite

Run all tests automatically:

```bash
python client/mcp_client_example.py
```

Choose option `1` and watch as it:
1. ✅ Tests calculator server (3 tools)
2. ✅ Tests weather server (4 tools)
3. ✅ Tests file explorer (tools + resources)

**Total time:** ~30 seconds

---

## Troubleshooting Tests

### Problem: "ModuleNotFoundError: No module named 'mcp'"

**Solution:**
```bash
pip install mcp
```

### Problem: Server exits immediately

**Check for errors:**
```bash
python basic/simple_mcp_server.py 2>&1 | tee server_log.txt
```

**Common causes:**
- Syntax errors in code
- Missing imports
- Wrong Python version (need 3.8+)

### Problem: Client says "Connection failed"

**Checklist:**
- [ ] Is the server running?
- [ ] Is the server path correct?
- [ ] Are you in the right directory?
- [ ] Did the server start without errors?

**Solution:**
```bash
# Make sure server is running
# Terminal 1
python basic/simple_mcp_server.py

# Terminal 2 - check it's running
ps aux | grep python

# Then try client again
python client/mcp_client_example.py
```

### Problem: Tool call fails

**Check arguments format:**
- Must be valid JSON
- Must match the inputSchema
- Required fields must be present

**Example - Wrong:**
```json
{city: "New York"}  # Missing quotes around key
```

**Example - Right:**
```json
{"city": "New York"}
```

---

## Test Scenarios by Feature

### Testing Basic Tools
```bash
# Server
python basic/simple_mcp_server.py

# Client - try each tool
add: {"a": 10, "b": 5}
multiply: {"a": 7, "b": 8}
power: {"base": 2, "exponent": 10}
```

### Testing Complex Tools
```bash
# Server
python tools/weather_mcp_server.py

# Client - try different cities
get_current_weather: {"city": "Tokyo", "units": "celsius"}
get_forecast: {"city": "Paris", "days": 5}
compare_weather: {"city1": "Sydney", "city2": "London"}
```

### Testing Resources
```bash
# Server
python resources/file_explorer_server.py

# Client
1. List resources (should show all .txt, .json, .py files)
2. Read a resource (select one from the list)
3. Call search_files: {"pattern": "*.json"}
4. Call get_file_info: {"filename": "README.md"}
```

---

## Performance Testing

### Test Server Startup Time

```bash
time python basic/simple_mcp_server.py
# Should start in < 1 second
```

### Test Tool Execution Time

Use the client's automatic mode and check timestamps:
```bash
python client/mcp_client_example.py
# Choose option 1
# Watch execution times
```

**Expected times:**
- Calculator tools: < 100ms
- Weather tools: < 200ms
- File operations: < 500ms

---

## Integration Testing

### Test with Multiple Servers

Run all three servers simultaneously:

**Terminal 1:**
```bash
python basic/simple_mcp_server.py
```

**Terminal 2:**
```bash
python tools/weather_mcp_server.py
```

**Terminal 3:**
```bash
python resources/file_explorer_server.py
```

**Terminal 4:**
```bash
python client/mcp_client_example.py
# Test each server one by one
```

---

## Validation Checklist

Before considering your MCP servers production-ready:

### Server Checklist
- [ ] Server starts without errors
- [ ] All tools are listed correctly
- [ ] Tool descriptions are clear
- [ ] Input schemas are valid JSON Schema
- [ ] Error handling works (try invalid inputs)
- [ ] Resources are properly exposed (if applicable)
- [ ] Security checks are in place

### Client Checklist
- [ ] Can connect to server
- [ ] Can list tools
- [ ] Can call each tool successfully
- [ ] Can handle errors gracefully
- [ ] Can list resources (if applicable)
- [ ] Can read resources (if applicable)

### Integration Checklist
- [ ] Claude Desktop config is correct
- [ ] Server path uses absolute paths
- [ ] Server runs from any directory
- [ ] Tools work as expected in Claude
- [ ] Error messages are helpful

---

## Test Results Log

Keep track of your testing:

```
Date: 2024-XX-XX
Test: Calculator Server
Status: ✅ PASS
Notes: All 3 tools working correctly

Date: 2024-XX-XX
Test: Weather Server
Status: ✅ PASS
Notes: All 4 tools tested, alerts saving correctly

Date: 2024-XX-XX
Test: File Explorer Server
Status: ✅ PASS
Notes: Resources listing correctly, tools working

Date: 2024-XX-XX
Test: Claude Desktop Integration
Status: ✅ PASS
Notes: All servers accessible from Claude Desktop
```

---

## Next Steps

After successful testing:

1. ✅ Modify servers (add new tools)
2. ✅ Build your own MCP server
3. ✅ Connect to Claude Desktop
4. ✅ Create production-ready servers
5. ✅ Share your servers with others!

---

## Quick Reference

### Start Server
```bash
python <server_script>.py
```

### Test with Client (Automatic)
```bash
python client/mcp_client_example.py
# Choose 1
```

### Test with Client (Interactive)
```bash
python client/mcp_client_example.py
# Choose 2
```

### Check Server is Running
```bash
ps aux | grep python
```

### Stop Server
```
Ctrl+C in server terminal
```

---

Happy testing! 🧪
