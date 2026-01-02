# Finance Portfolio Analyzer - Claude Agent Tutorial

A comprehensive AI agent that demonstrates Claude's advanced capabilities including Skills, Computer Use, MCP integration, and Memory. This tutorial teaches you how to build a personal finance portfolio analyzer from scratch.

## 🚀 NEW: Enhanced Trading Features

This agent now includes professional-grade trading capabilities:

- **📈 Technical Analysis**: 15+ indicators (RSI, MACD, Bollinger, ADX, etc.)
- **🎯 Trading Strategies**: 5 built-in strategies with multi-strategy consensus
- **⚠️ Risk Management**: Position sizing, VaR, Sharpe/Sortino ratios
- **🔬 Backtesting**: Full strategy testing with walk-forward analysis
- **🔔 Alerts**: Price, technical, and portfolio alerts
- **📊 Market Data**: Real-time quotes, sector performance, screening

**See [FEATURES.md](FEATURES.md) for complete documentation of all trading features.**

## Features

- **Portfolio Analysis**: Analyze investment holdings with key financial metrics (returns, Sharpe ratio, risk level)
- **Excel Reports**: Generate professional formatted reports with charts and conditional formatting
- **Real-time Data**: Fetch current stock prices via MCP server integration
- **Persistent Memory**: Remember user preferences across sessions
- **Interactive CLI**: User-friendly command-line interface with quick commands

## Project Structure

```
finance-agent/
├── src/
│   ├── agent.py                    # Basic agent implementation
│   ├── finance_agent.py            # Enhanced agent with trading features
│   ├── agent_memory.py             # Memory capabilities
│   ├── portfolio.py                # Portfolio management & analysis
│   ├── technical_indicators.py     # 15+ technical indicators
│   ├── risk_management.py          # VaR, position sizing, risk metrics
│   ├── trading_strategy.py         # Strategy engine & signals
│   ├── backtesting.py              # Backtesting framework
│   ├── alerts.py                   # Alerts & notifications
│   └── market_data.py              # Market data service
├── .claude/
│   └── skills/
│       ├── portfolio-analysis/
│       │   ├── SKILL.md           # Portfolio analysis expertise
│       │   └── context/
│       │       └── benchmarks.md   # Market benchmark data
│       └── excel-reporting/
│           └── SKILL.md           # Excel report generation
├── mcp-servers/
│   └── stock-data/
│       ├── server.py              # Enhanced MCP server with 10+ tools
│       └── requirements.txt
├── data/
│   └── sample_portfolio.csv       # Example portfolio data
├── tests/
│   ├── test_agent.py
│   ├── test_skills.py
│   └── test_mcp.py
├── requirements.txt
├── mcp_config.json               # MCP server configuration
├── main.py                       # Enhanced CLI interface
├── FEATURES.md                   # Detailed trading features guide
└── README.md
```

## Prerequisites

- Python 3.10 or higher
- Anthropic API key (get one at https://console.anthropic.com/)
- Alpha Vantage API key (optional, free tier at https://www.alphavantage.co/)

## Installation

### 1. Navigate to Tutorial

```bash
cd tutorials/10-finance-portfolio-analyzer-agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install MCP Server Dependencies

```bash
cd mcp-servers/stock-data
pip install -r requirements.txt
cd ../..
```

### 5. Set Up Environment Variables

Add your API keys to the repository's root `.env` file (located at `../../.env`):

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ALPHA_VANTAGE_KEY=demo
```

> **Note**: The tutorial uses the repository's existing `.env` file. You can use `demo` as the Alpha Vantage key for testing, but it has rate limits.

## Usage

### Run the CLI Interface

```bash
python main.py
```

### Interactive Commands

Once running, you can use these commands:

- `quit` - Exit the application
- `reset` - Clear conversation history
- `memory` - View current memory
- `clear memory` - Erase all preferences

### Example Interactions

#### 1. Set Preferences

```
You: I'm a conservative investor focused on retirement

Agent: Great! I'll remember that you're a conservative investor focused on retirement...
```

#### 2. Analyze Portfolio

```
You: Analyze the portfolio in data/sample_portfolio.csv

Agent: [Loads portfolio-analysis skill and analyzes the CSV]

       PORTFOLIO SUMMARY
       =================
       Total Value: $52,420.00
       Total Return: 12.3%
       Risk Level: Moderate
       ...
```

#### 3. Fetch Real-time Data

```
You: What's Apple's current price?

Agent: [Calls MCP server to fetch data]

       AAPL: $180.25
       Change: +$2.50 (+1.41%)
       Volume: 52,487,900
```

#### 4. Generate Excel Report

```
You: Generate an Excel report for my portfolio

Agent: [Creates formatted Excel file with charts]

       Report created: computer:///mnt/user-data/outputs/portfolio_report.xlsx
```

## Architecture Layers

The agent is built progressively in layers:

### Layer 1: Basic Conversation
- Simple chat functionality
- Conversation history management
- System prompts

**Code**: `agent.chat(message)`

### Layer 2: Skills Integration
- Portfolio analysis expertise
- Excel reporting capabilities
- Code execution enabled

**Code**: `agent.chat_with_skills(message)`

### Layer 3: Computer Use
- File operations (/mnt/user-data/)
- Read CSV files
- Create Excel reports

**Code**: `agent.chat_with_computer(message)`

### Layer 4: MCP Server
- Real-time stock price data
- Market status checking
- External API integration

**Files**: `mcp-servers/stock-data/server.py`, `mcp_config.json`

### Layer 5: Memory
- Persistent user preferences
- Important facts tracking
- Automatic preference extraction

**Code**: `agent.chat_with_memory(message)` (used by default in CLI)

### Layer 6: CLI Interface
- User-friendly interaction
- Command handling
- Error management

**File**: `main.py`

## Skills

### Portfolio Analysis Skill

Located at: `.claude/skills/portfolio-analysis/SKILL.md`

Provides expertise in:
- Calculating financial metrics (returns, Sharpe ratio, max drawdown)
- Risk classification (Conservative/Moderate/Aggressive)
- Diversification analysis
- Portfolio summaries

Context data: `.claude/skills/portfolio-analysis/context/benchmarks.md`

### Excel Reporting Skill

Located at: `.claude/skills/excel-reporting/SKILL.md`

Provides expertise in:
- Creating multi-sheet Excel workbooks
- Professional formatting (colors, fonts, borders)
- Charts (pie charts, bar charts)
- Conditional formatting

## MCP Server

### Stock Data Server

The MCP server provides three tools:

1. **get_stock_price(symbol)** - Get current price for one stock
2. **get_multiple_quotes(symbols)** - Get prices for multiple stocks
3. **get_market_status()** - Check if market is open

Uses Alpha Vantage API for real-time data.

### Running the MCP Server Standalone

```bash
cd mcp-servers/stock-data
python server.py
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific test files:

```bash
pytest tests/test_agent.py -v
pytest tests/test_skills.py -v
pytest tests/test_mcp.py -v
```

### Test Coverage

- **test_agent.py**: Agent initialization, conversation history, memory operations
- **test_skills.py**: Skill files existence, portfolio data format
- **test_mcp.py**: MCP configuration, server files, market status logic

## Customization

### Add New Skills

1. Create a new skill directory: `.claude/skills/your-skill/`
2. Create `SKILL.md` with YAML frontmatter:

```yaml
---
name: your-skill
description: What this skill does
version: 1.0.0
---

# Your Skill Content
...
```

3. Update `agent.py` to include the new skill ID

### Modify Memory Extraction

Edit `src/agent_memory.py` → `_extract_and_save_preferences()` to add custom keywords or use Claude's structured extraction.

### Add MCP Tools

Edit `mcp-servers/stock-data/server.py` to add new tools to the `@server.list_tools()` decorator.

## Troubleshooting

### API Key Issues

```
ERROR: ANTHROPIC_API_KEY not found in environment variables
```

**Solution**: Ensure `.env` file exists in the repository root with valid API key

### Import Errors

```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution**: Install dependencies with `pip install -r requirements.txt`

### MCP Server Connection Issues

**Solution**: Check `mcp_config.json` paths are correct and MCP dependencies are installed

### Skills Not Loading

**Solution**: Ensure `.claude/skills/` directory exists with correct SKILL.md files

## Learning Path

### Beginner
1. Start with Layer 1 (Basic Chat)
2. Explore conversation history
3. Test with simple financial questions

### Intermediate
4. Add Skills (Layer 2)
5. Analyze sample portfolio
6. Understand skill integration

### Advanced
7. Enable Computer Use (Layer 3)
8. Generate Excel reports
9. Set up MCP server (Layer 4)
10. Implement Memory (Layer 5)

## Example Workflows

### Complete Portfolio Analysis

```python
# In main.py or custom script
agent = FinanceAgent()

# Set context
agent.chat_with_memory("I'm a moderate investor saving for retirement in 10 years")

# Analyze portfolio
agent.chat_with_memory("Analyze data/sample_portfolio.csv")

# Get current prices
agent.chat_with_memory("Update with current prices for all holdings")

# Generate report
agent.chat_with_memory("Create an Excel report with recommendations")

# View memory
print(agent.view_memory())
```

## Best Practices

1. **Skills**: Keep skills focused on specific domains
2. **Memory**: Only store important, long-term preferences
3. **Error Handling**: Wrap API calls in try-except blocks
4. **Testing**: Test each layer independently before combining
5. **Security**: Never commit `.env` file with real API keys

## Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Skills Guide](https://docs.anthropic.com/en/docs/build-with-claude/skills)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)

## License

This is an educational tutorial. Feel free to modify and extend for your own learning!

## Contributing

Found an issue or have an improvement? Contributions welcome!

## Acknowledgments

Built with:
- Anthropic Claude Sonnet 4.5
- Model Context Protocol (MCP)
- Alpha Vantage API
- Python ecosystem (pandas, openpyxl, requests, pytest)

---

**Happy Building!** Start with Layer 1 and progressively add capabilities. Each layer builds on the previous one, teaching you agent architecture step by step.
