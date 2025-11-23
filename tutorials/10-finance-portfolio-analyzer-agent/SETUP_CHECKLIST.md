# Setup Checklist

Use this checklist to verify your installation is complete and working.

## Prerequisites ✓

- [ ] Python 3.10 or higher installed
  ```bash
  python --version
  ```

- [ ] Anthropic API key obtained from https://console.anthropic.com/

- [ ] (Optional) Alpha Vantage API key from https://www.alphavantage.co/

## Installation Steps ✓

- [ ] Virtual environment created
  ```bash
  python -m venv venv
  ```

- [ ] Virtual environment activated
  ```bash
  # Windows
  venv\Scripts\activate
  # macOS/Linux
  source venv/bin/activate
  ```

- [ ] Main dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] MCP server dependencies installed
  ```bash
  cd mcp-servers/stock-data
  pip install -r requirements.txt
  cd ../..
  ```

- [ ] API keys added to repository root `.env` file
  ```bash
  # Repository root .env (at ../../.env) should contain:
  ANTHROPIC_API_KEY=sk-...
  ALPHA_VANTAGE_KEY=demo  # or your key
  ```

## File Structure Validation ✓

- [ ] Core application files exist:
  - [ ] `src/agent.py`
  - [ ] `src/agent_memory.py`
  - [ ] `src/__init__.py`
  - [ ] `main.py`

- [ ] Skills directory exists:
  - [ ] `.claude/skills/portfolio-analysis/SKILL.md`
  - [ ] `.claude/skills/portfolio-analysis/context/benchmarks.md`
  - [ ] `.claude/skills/excel-reporting/SKILL.md`

- [ ] MCP server exists:
  - [ ] `mcp-servers/stock-data/server.py`
  - [ ] `mcp_config.json`

- [ ] Data files exist:
  - [ ] `data/sample_portfolio.csv`

- [ ] Test files exist:
  - [ ] `tests/test_agent.py`
  - [ ] `tests/test_skills.py`
  - [ ] `tests/test_mcp.py`

## Functionality Tests ✓

### Layer 1: Basic Chat

- [ ] Can import agent
  ```python
  from src.agent import FinanceAgent
  agent = FinanceAgent()
  ```

- [ ] Basic chat works
  ```python
  response = agent.chat("What is portfolio diversification?")
  print(response)
  ```

### Layer 2: Skills

- [ ] Skills are accessible
  ```python
  response = agent.chat_with_skills("How do I calculate Sharpe ratio?")
  print(response)
  ```

### Layer 3: Computer Use

- [ ] Can read CSV file
  ```python
  response = agent.chat_with_computer("Read data/sample_portfolio.csv")
  print(response)
  ```

### Layer 4: MCP Server

- [ ] MCP server can start
  ```bash
  cd mcp-servers/stock-data
  python server.py
  # Should run without errors (Ctrl+C to stop)
  ```

### Layer 5: Memory

- [ ] Memory functions work
  ```python
  agent.update_memory("risk_tolerance", "conservative")
  print(agent.view_memory())
  agent.clear_memory()
  ```

### Layer 6: CLI

- [ ] CLI starts successfully
  ```bash
  python main.py
  # Should show welcome message
  ```

- [ ] Commands work:
  - [ ] Chat with agent
  - [ ] Type `memory` to view memory
  - [ ] Type `reset` to clear history
  - [ ] Type `quit` to exit

## Unit Tests ✓

- [ ] All tests pass
  ```bash
  pytest tests/ -v
  ```

- [ ] Individual test files pass:
  ```bash
  pytest tests/test_agent.py -v
  pytest tests/test_skills.py -v
  pytest tests/test_mcp.py -v
  ```

## Common Issues ✓

### Issue: "ANTHROPIC_API_KEY not found"
- [ ] Verify `.env` file exists in repository root directory (../../.env)
- [ ] Check file is named exactly `.env` (not `.env.txt`)
- [ ] Ensure no spaces around `=` in `.env`
- [ ] Ensure `python-dotenv` is installed

### Issue: "ModuleNotFoundError: No module named 'anthropic'"
- [ ] Virtual environment is activated
- [ ] Run `pip install -r requirements.txt`
- [ ] Try `pip list` to see installed packages

### Issue: Skills not working
- [ ] Verify `.claude/skills/` directory structure
- [ ] Check SKILL.md files have YAML frontmatter (lines starting with `---`)
- [ ] Ensure skill_ids in agent.py match skill names

### Issue: MCP server errors
- [ ] Install MCP dependencies: `cd mcp-servers/stock-data && pip install -r requirements.txt`
- [ ] Check `mcp_config.json` has correct paths
- [ ] Verify Python path in mcp_config.json

## Documentation Review ✓

- [ ] Read README.md for comprehensive overview
- [ ] Review QUICKSTART.md for quick setup
- [ ] Check TUTORIAL_SUMMARY.md for architecture understanding
- [ ] Browse code comments for implementation details

## Next Steps ✓

Once all items are checked:

1. [ ] Run a complete workflow:
   ```
   python main.py

   > I'm a conservative investor focused on retirement
   > Analyze data/sample_portfolio.csv
   > memory
   > quit
   ```

2. [ ] Try customization:
   - [ ] Edit `data/sample_portfolio.csv` with different stocks
   - [ ] Modify memory keywords in `src/agent_memory.py`
   - [ ] Add a new skill in `.claude/skills/`

3. [ ] Experiment with layers:
   - [ ] Start with Layer 1 only (basic chat)
   - [ ] Gradually enable each layer
   - [ ] Understand how each layer adds capability

## Success Criteria ✓

You've successfully set up the Finance Portfolio Analyzer when:

- ✅ All tests pass (`pytest tests/ -v`)
- ✅ CLI runs without errors (`python main.py`)
- ✅ Agent can analyze the sample portfolio
- ✅ Memory persists across sessions
- ✅ You understand the 5-layer architecture

## Getting Help

If stuck:
1. Check error messages carefully
2. Review relevant documentation files
3. Ensure all prerequisites are met
4. Try running tests to isolate the issue
5. Check that file paths are correct (especially on Windows)

## Verification Script

Run this to quickly verify installation:

```python
#!/usr/bin/env python3
import os
import sys

print("🔍 Verifying Finance Portfolio Analyzer Setup...\n")

checks = {
    "Python version": sys.version_info >= (3, 10),
    ".env file exists": os.path.exists(".env"),
    "agent.py exists": os.path.exists("src/agent.py"),
    "portfolio skill exists": os.path.exists(".claude/skills/portfolio-analysis/SKILL.md"),
    "sample data exists": os.path.exists("data/sample_portfolio.csv"),
    "MCP config exists": os.path.exists("mcp_config.json"),
}

try:
    from dotenv import load_dotenv
    load_dotenv()
    checks["dotenv installed"] = True
    checks["API key set"] = bool(os.getenv("ANTHROPIC_API_KEY"))
except:
    checks["dotenv installed"] = False
    checks["API key set"] = False

try:
    import anthropic
    checks["anthropic installed"] = True
except:
    checks["anthropic installed"] = False

try:
    import pandas
    checks["pandas installed"] = True
except:
    checks["pandas installed"] = False

passed = 0
failed = 0

for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")
    if result:
        passed += 1
    else:
        failed += 1

print(f"\n📊 Results: {passed} passed, {failed} failed")

if failed == 0:
    print("\n🎉 All checks passed! You're ready to go.")
else:
    print("\n⚠️  Some checks failed. Review SETUP_CHECKLIST.md for troubleshooting.")
```

Save as `verify_setup.py` and run with `python verify_setup.py`

---

**Checklist complete? Start building!** 🚀
