# Quick Start Guide

Get up and running with the Finance Portfolio Analyzer in 5 minutes!

## 1. Install Dependencies (2 minutes)

```bash
cd tutorials/10-finance-portfolio-analyzer-agent
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## 2. Set Up API Key (1 minute)

Add to the repository's root `.env` file (at `../../.env`):

```bash
ANTHROPIC_API_KEY=your_api_key_here
ALPHA_VANTAGE_KEY=demo
```

Get your Anthropic API key from: https://console.anthropic.com/

## 3. Run the Agent (2 minutes)

```bash
python main.py
```

## 4. Try These Commands

### Basic Chat
```
You: What is a good portfolio diversification strategy?
```

### Analyze Portfolio
```
You: Analyze the portfolio in data/sample_portfolio.csv
```

### Set Preferences
```
You: I'm a conservative investor focused on retirement
You: memory
```

### Get Stock Price (if MCP configured)
```
You: What's the current price of AAPL?
```

## Layer-by-Layer Testing

Want to test each layer independently? Use Python:

```python
from dotenv import load_dotenv
load_dotenv()

from src.agent import FinanceAgent
agent = FinanceAgent()

# Layer 1: Basic Chat
response = agent.chat("What is the Sharpe ratio?")
print(response)

# Layer 2: Skills
response = agent.chat_with_skills("Explain how to calculate portfolio returns")
print(response)

# Layer 3: Computer Use
response = agent.chat_with_computer("Read and analyze data/sample_portfolio.csv")
print(response)

# Layer 5: Memory
response = agent.chat_with_memory("I prefer aggressive growth stocks")
print(agent.view_memory())
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the skills in `.claude/skills/`
3. Modify `data/sample_portfolio.csv` with your own holdings
4. Run tests: `pytest tests/ -v`
5. Customize memory extraction in `src/agent_memory.py`

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure `.env` file exists in the repository root directory
- Check that the file name is exactly `.env` (not `.env.txt`)
- Ensure `python-dotenv` is installed

**"ModuleNotFoundError"**
- Activate virtual environment first
- Run `pip install -r requirements.txt`

**"Skills not working"**
- Ensure `.claude/skills/` directories exist
- Check SKILL.md files have correct YAML frontmatter

## Learning Tips

1. **Start Simple**: Begin with Layer 1 (basic chat)
2. **Progress Gradually**: Add one layer at a time
3. **Read the Code**: Each layer is well-documented
4. **Experiment**: Try different portfolios and questions
5. **Test Often**: Run `pytest` after making changes

Happy coding!
