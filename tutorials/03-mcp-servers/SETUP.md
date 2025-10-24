# MCP Tutorial - Complete Setup Guide

## Problem You Just Hit

You saw this error:
```
ModuleNotFoundError: No module named 'mcp'
```

**Why?** The `mcp` package wasn't installed in your virtual environment.

**Solution:** Follow the steps below!

---

## Quick Fix (2 Minutes)

### Option 1: Run the Setup Script (Easiest)

Double-click: **`setup.bat`**

This will:
1. Activate your virtual environment
2. Install the MCP package
3. Verify installation

Then try running the server again!

### Option 2: Manual Install

```bash
# Open PowerShell in project root
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"

# Activate virtual environment
venv\Scripts\activate

# Install MCP
pip install mcp

# Verify
python -c "import mcp; print('MCP installed!')"
```

---

## Understanding the Issue

### What Happened

1. You ran: `run_calculator_server.bat`
2. It tried to run Python code
3. Code tried `from mcp.server import Server`
4. Python said: "I don't have that package!"

### Why It Happened

**Virtual environments** isolate Python packages. You have to install packages **inside** the venv, not globally.

Your setup:
```
Global Python  --> Has MCP (you installed it earlier)
Virtual Env    --> Didn't have MCP (until we just installed it)
```

When running from the project, it uses the **virtual env** Python.

---

## Complete First-Time Setup

If you're setting this up for the first time:

### Step 1: Verify Virtual Environment Exists

```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"
dir venv
```

**If venv doesn't exist:**
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

**PowerShell:**
```bash
venv\Scripts\activate
```

**Command Prompt:**
```bash
venv\Scripts\activate.bat
```

You should see `(venv)` in your prompt.

### Step 3: Install All Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Verify MCP is installed
python -c "import mcp; print('MCP version:', mcp.__version__)"
```

### Step 4: Test!

```bash
# Run simple demo
python tutorials\03-mcp-servers\simple_demo.py

# Or use batch files (they auto-activate venv now!)
tutorials\03-mcp-servers\run_calculator_server.bat
```

---

## The Fixed Batch Files

All `.bat` files now automatically:
1. Navigate to project root
2. Activate virtual environment
3. Run the script

So you can just **double-click** them!

---

## Troubleshooting

### "venv not found"

Create it:
```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"
python -m venv venv
```

### "pip not recognized"

Make sure venv is activated:
```bash
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Still getting ModuleNotFoundError

Try:
```bash
# Activate venv
venv\Scripts\activate

# Uninstall and reinstall
pip uninstall mcp -y
pip install mcp

# Test
python -c "import mcp; print('Works!')"
```

### "Permission denied"

Run PowerShell or CMD as Administrator, then:
```bash
pip install --user mcp
```

---

## What Each File Does Now

### `setup.bat`
- **NEW!** One-click setup
- Activates venv
- Installs MCP
- Verifies installation

### `run_calculator_server.bat`
- **UPDATED!** Now activates venv automatically
- Runs calculator server
- Just double-click!

### `run_weather_server.bat`
- **UPDATED!** Auto-activates venv
- Runs weather server

### `run_file_server.bat`
- **UPDATED!** Auto-activates venv
- Runs file explorer server

### `run_client.bat`
- **UPDATED!** Auto-activates venv
- Runs test client

---

## Verification Checklist

After setup, verify everything works:

- [ ] Virtual environment exists: `dir venv`
- [ ] MCP is installed: `venv\Scripts\python -c "import mcp"`
- [ ] Simple demo runs: `python tutorials\03-mcp-servers\simple_demo.py`
- [ ] Batch files work: Double-click `run_calculator_server.bat`

---

## Running MCP Examples - 3 Ways

### Way 1: Batch Files (Easiest)
Double-click any `.bat` file in `tutorials/03-mcp-servers/`

### Way 2: PowerShell with Venv Activated
```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"
venv\Scripts\activate
python tutorials\03-mcp-servers\basic\simple_mcp_server.py
```

### Way 3: Direct (if venv activated in current session)
```bash
# Only if (venv) shows in your prompt!
cd tutorials\03-mcp-servers
python basic\simple_mcp_server.py
```

---

## Dependencies Installed

After setup, you'll have:

- `mcp` >= 1.18.0 - Model Context Protocol SDK
- `anyio` - Async I/O support
- `httpx` - HTTP client
- `pydantic` - Data validation
- `starlette` - ASGI framework
- `uvicorn` - ASGI server
- All other dependencies from `requirements.txt`

---

## Next Steps After Setup

1. **Test the simple demo:**
   ```bash
   python tutorials\03-mcp-servers\simple_demo.py
   ```

2. **Run a server:**
   ```bash
   # Double-click
   run_calculator_server.bat

   # OR in terminal
   venv\Scripts\activate
   python tutorials\03-mcp-servers\basic\simple_mcp_server.py
   ```

3. **Read the docs:**
   - `README.md` - Complete tutorial
   - `QUICKSTART.md` - Quick start
   - `HOW_TO_RUN.md` - Running examples

4. **Try Claude Desktop integration:**
   - See `claude_desktop_config.example.json`
   - Follow instructions in README.md

---

## Common Questions

**Q: Do I need to activate venv every time?**
A: No! The `.bat` files do it automatically. If running Python commands manually, yes.

**Q: Why use a virtual environment?**
A: It keeps project dependencies separate. Prevents conflicts between projects.

**Q: Can I install MCP globally instead?**
A: Yes, but not recommended. Virtual environments are best practice.

**Q: The batch file says "venv not found"**
A: Create it: `python -m venv venv` from project root.

**Q: How do I know if venv is activated?**
A: You'll see `(venv)` at the start of your terminal prompt.

---

## Summary

✅ **Setup is complete** if:
- MCP package is installed in venv
- Batch files auto-activate venv
- `simple_demo.py` runs without errors
- You can run servers with batch files

✅ **You're ready to:**
- Learn MCP concepts
- Run the example servers
- Build your own MCP servers
- Connect to Claude Desktop

---

## Get Help

If you're still stuck:

1. **Check:** Is venv activated? Look for `(venv)` in prompt
2. **Try:** Run `setup.bat` again
3. **Verify:** `venv\Scripts\python -c "import mcp"`
4. **Read:** `HOW_TO_RUN.md` for detailed running instructions

Happy coding! 🚀
