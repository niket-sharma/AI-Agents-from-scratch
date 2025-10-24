# How to Run the MCP Examples

## Quick Start (Choose ONE method)

### Method 1: Double-Click Batch Files (Easiest for Windows)

1. **Run Simple Demo**
   - Double-click: `simple_demo.py`
   - This shows you what MCP is without needing to run servers

2. **Run Calculator Server**
   - Double-click: `run_calculator_server.bat`
   - Server will start and wait for connections
   - Press Ctrl+C to stop

3. **Run Weather Server**
   - Double-click: `run_weather_server.bat`
   - Press Ctrl+C to stop

4. **Run File Explorer**
   - Double-click: `run_file_server.bat`
   - Press Ctrl+C to stop

---

### Method 2: Command Line (If you have spaces in your path)

**Important**: When your path has spaces (like "Niket Sharma"), you need to:
1. Use quotes around the ENTIRE path
2. OR navigate to the directory first

#### Option A: Navigate First (Recommended)
```bash
# Open PowerShell or Command Prompt
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch\tutorials\03-mcp-servers"

# Then run any script:
python simple_demo.py
python basic\simple_mcp_server.py
python tools\weather_mcp_server.py
python resources\file_explorer_server.py
```

#### Option B: Use Full Quoted Path
```bash
python "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch\tutorials\03-mcp-servers\simple_demo.py"
```

---

### Method 3: Using the Launcher Scripts

```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch\tutorials\03-mcp-servers"

# Run any launcher:
run_client.bat
run_calculator_server.bat
run_weather_server.bat
run_file_server.bat
```

---

## What Each File Does

### `simple_demo.py` ★ START HERE
- **What it is**: Interactive introduction to MCP
- **What it does**: Shows you MCP concepts with a mini demo
- **Run**: `python simple_demo.py`
- **Time**: 2 minutes
- **Best for**: Understanding what MCP is

### `basic/simple_mcp_server.py`
- **What it is**: Calculator MCP server
- **What it does**: Exposes 3 math tools (add, multiply, power)
- **Run**: `python basic\simple_mcp_server.py`
- **Use**: Connects to Claude Desktop or test client

### `tools/weather_mcp_server.py`
- **What it is**: Weather service MCP server
- **What it does**: Provides weather tools (get_weather, forecast, etc.)
- **Run**: `python tools\weather_mcp_server.py`
- **Use**: Connects to Claude Desktop or test client

### `resources/file_explorer_server.py`
- **What it is**: File system MCP server
- **What it does**: Exposes local files as resources
- **Run**: `python resources\file_explorer_server.py`
- **Use**: Connects to Claude Desktop or test client

### `client/mcp_client_example.py`
- **What it is**: MCP test client
- **What it does**: Tests MCP servers (alternative to Claude Desktop)
- **Run**: `python client\mcp_client_example.py`
- **Note**: Requires `mcp` package (`pip install mcp`)

---

## Common Errors and Solutions

### Error: "python: can't find '__main__' module"

**Cause**: Path has spaces and isn't quoted properly

**Solution**:
```bash
# BAD (doesn't work with spaces):
python C:\Users\Niket Sharma\file.py

# GOOD (works with spaces):
cd "C:\Users\Niket Sharma\folder"
python file.py

# OR use quotes:
python "C:\Users\Niket Sharma\file.py"
```

### Error: "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
```bash
pip install mcp
```

### Error: "UnicodeEncodeError" or weird characters

**Solution**: Use the batch files or run `simple_demo.py` which handles encoding

### Server exits immediately

**Solution**: The server needs a client to connect. Either:
1. Use Claude Desktop (configured with the server)
2. Use the test client (if MCP SDK is compatible)
3. Just understand the code - read the source files

---

## Step-by-Step: Your First Time

### Step 1: See the Demo (2 min)
```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch\tutorials\03-mcp-servers"
python simple_demo.py
```

Press Enter when done.

### Step 2: Read the Concepts (10 min)
Open and read:
- `README.md` - Main tutorial
- `QUICKSTART.md` - Quick start guide
- `MCP_EXPLAINED.md` - Deep dive

### Step 3: Look at Code (5 min)
Open in your editor:
- `basic/simple_mcp_server.py` - See how a simple server works

### Step 4: Connect to Claude Desktop (Optional, 10 min)

1. **Find Claude config location**:
   - Windows: Press `Win+R`, type `%APPDATA%\Claude`, press Enter
   - Create/edit `claude_desktop_config.json`

2. **Copy from example**:
   - Open `claude_desktop_config.example.json`
   - Copy the contents

3. **Update paths**:
   - Replace `C:/Users/YourName/` with your actual path
   - Use forward slashes (`/`) not backslashes
   - Use absolute paths

4. **Example**:
   ```json
   {
     "mcpServers": {
       "calculator": {
         "command": "python",
         "args": [
           "C:/Users/Niket Sharma/llmapp/AI-Agents-from-scratch/tutorials/03-mcp-servers/basic/simple_mcp_server.py"
         ]
       }
     }
   }
   ```

5. **Restart Claude Desktop**

6. **Test**:
   - Open Claude Desktop
   - Ask: "What tools do you have?"
   - Ask: "Add 10 and 5"

---

## Troubleshooting Paths with Spaces

Your path: `c:\Users\Niket Sharma\llmapp\...`

The space in "Niket Sharma" causes issues. Here's how to handle it:

### In PowerShell/CMD:
```bash
# Always use quotes:
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch\tutorials\03-mcp-servers"

# Then run without path:
python simple_demo.py
```

### In Claude Desktop Config:
```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:/Users/Niket Sharma/llmapp/AI-Agents-from-scratch/tutorials/03-mcp-servers/basic/simple_mcp_server.py"
      ]
    }
  }
}
```

**Note**: Use forward slashes `/` in JSON, not backslashes `\`

### In Batch Files:
The `.bat` files handle spaces automatically - just double-click them!

---

## Summary

**Simplest way to start**:
1. Double-click `simple_demo.py`
2. Read the output
3. Read `README.md`
4. Try connecting to Claude Desktop

**Questions?** Check:
- `QUICKSTART.md` - Fast start guide
- `TESTING_GUIDE.md` - Complete testing instructions
- `MCP_EXPLAINED.md` - Conceptual explanations

Happy learning! 🚀
