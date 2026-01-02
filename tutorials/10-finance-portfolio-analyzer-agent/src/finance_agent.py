"""
Enhanced Finance Portfolio Analyzer Agent

This module implements a comprehensive AI trading agent with:
- Portfolio management and analysis
- Technical analysis and trading signals
- Risk management and position sizing
- Backtesting and strategy evaluation
- Alerts and notifications
- Market data integration via MCP
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic

from agent_memory import MemoryMixin
from portfolio import Portfolio, Position, AssetClass
from technical_indicators import TechnicalIndicators, generate_technical_report, Signal
from risk_management import (
    RiskProfile, RiskLevel, PositionSizer, VaRCalculator,
    RiskAdjustedMetrics, DrawdownAnalyzer, generate_risk_report
)
from market_data import MarketDataService, ScreenerService
from trading_strategy import (
    StrategyEngine, create_default_strategy_engine,
    OrderManager, OrderSide, OrderType
)
from backtesting import Backtester, BacktestConfig, generate_sample_price_data
from alerts import AlertManager, AlertCondition, AlertPriority, WatchlistManager


class FinanceAgent(MemoryMixin):
    """Enhanced AI Agent for personal finance and trading"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Finance Agent

        Args:
            api_key: Anthropic API key (if not provided, loads from ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        self.memory_file = "agent_memory.json"
        self.memory: Dict[str, Any] = self._load_memory()
        
        # Initialize components
        self.market_data = MarketDataService()
        self.screener = ScreenerService(self.market_data)
        self.strategy_engine = create_default_strategy_engine()
        self.order_manager = OrderManager()
        self.alert_manager = AlertManager()
        self.watchlist_manager = WatchlistManager()
        self.risk_profile = RiskProfile()
        self.portfolio: Optional[Portfolio] = None
        
        # Enhanced system prompt with all capabilities
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        return """You are an expert financial advisor and trading assistant with deep knowledge of:

PORTFOLIO MANAGEMENT:
- Portfolio analysis, diversification, and rebalancing
- Asset allocation strategies
- Position sizing and risk management
- Dividend income optimization

TECHNICAL ANALYSIS:
- Chart patterns and trend analysis
- Technical indicators (RSI, MACD, Bollinger Bands, ADX, etc.)
- Support and resistance levels
- Trading signal generation

RISK MANAGEMENT:
- Value at Risk (VaR) calculations
- Sharpe ratio, Sortino ratio, and other risk metrics
- Position sizing (Kelly Criterion, fixed fractional)
- Stop loss and take profit strategies
- Drawdown analysis

TRADING STRATEGIES:
- Trend following strategies
- Mean reversion strategies
- Momentum strategies
- Multi-strategy consensus approach

MARKET ANALYSIS:
- Sector rotation and performance
- Market indices analysis
- Fundamental analysis
- Economic indicators

When providing advice:
1. Always consider the user's risk tolerance and investment goals
2. Provide specific, actionable recommendations
3. Explain the reasoning behind your analysis
4. Include relevant metrics and data
5. Warn about potential risks
6. Never guarantee returns or make promises about performance

You have access to real-time market data, technical analysis tools, and backtesting capabilities.
"""

    def load_portfolio(self, filepath: str) -> str:
        """Load portfolio from CSV file"""
        try:
            self.portfolio = Portfolio.from_csv(filepath, name="My Portfolio")
            return f"Portfolio loaded with {len(self.portfolio.positions)} positions"
        except Exception as e:
            return f"Error loading portfolio: {e}"

    def create_portfolio(self, name: str = "My Portfolio") -> Portfolio:
        """Create a new empty portfolio"""
        self.portfolio = Portfolio(name=name)
        return self.portfolio

    def add_position(
        self,
        symbol: str,
        shares: float,
        purchase_price: float,
        current_price: Optional[float] = None
    ) -> str:
        """Add a position to the portfolio"""
        if not self.portfolio:
            self.create_portfolio()
        
        if current_price is None:
            quote = self.market_data.get_quote(symbol)
            current_price = quote.price
        
        position = Position(
            symbol=symbol.upper(),
            shares=shares,
            purchase_price=purchase_price,
            current_price=current_price
        )
        
        self.portfolio.add_position(position)
        return f"Added {shares} shares of {symbol} at ${purchase_price}"

    def analyze_portfolio(self) -> Dict:
        """Get comprehensive portfolio analysis"""
        if not self.portfolio:
            return {"error": "No portfolio loaded"}
        
        # Update prices
        symbols = [p.symbol for p in self.portfolio.positions]
        quotes = self.market_data.get_multiple_quotes(symbols)
        prices = {s: q.price for s, q in quotes.items()}
        self.portfolio.update_prices(prices)
        
        # Get analysis
        metrics = self.portfolio.calculate_portfolio_metrics()
        allocation = self.portfolio.get_allocation_by_asset_class()
        concentration = self.portfolio.calculate_concentration_risk()
        top_performers = self.portfolio.get_top_performers(5)
        bottom_performers = self.portfolio.get_bottom_performers(5)
        
        return {
            "metrics": metrics,
            "allocation": allocation,
            "concentration_risk": concentration,
            "top_performers": top_performers,
            "bottom_performers": bottom_performers,
            "positions": [p.to_dict() for p in self.portfolio.positions]
        }

    def get_technical_analysis(self, symbol: str) -> Dict:
        """Get technical analysis for a symbol"""
        # Get historical data
        bars = self.market_data.get_historical_data(symbol)
        
        if len(bars) < 50:
            return {"error": "Insufficient data for analysis"}
        
        closes = [b.close for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        volumes = [b.volume for b in bars]
        
        return generate_technical_report(closes, highs, lows, volumes)

    def get_trading_signals(self, symbol: str) -> Dict:
        """Get trading signals from all strategies"""
        bars = self.market_data.get_historical_data(symbol)
        
        if len(bars) < 50:
            return {"error": "Insufficient data for signal generation"}
        
        closes = [b.close for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        volumes = [b.volume for b in bars]
        
        return self.strategy_engine.get_consensus_signal(
            symbol, closes, highs, lows, volumes
        )

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: float
    ) -> Dict:
        """Calculate position size based on risk parameters"""
        if not self.portfolio:
            return {"error": "No portfolio loaded"}
        
        portfolio_value = self.portfolio.total_market_value
        
        return PositionSizer.fixed_fractional(
            portfolio_value,
            self.risk_profile.max_portfolio_risk_pct,
            entry_price,
            stop_loss_price
        )

    def run_backtest(
        self,
        strategy_name: str = "all",
        symbols: Optional[List[str]] = None,
        days: int = 252
    ) -> Dict:
        """Run a backtest on historical data"""
        if symbols is None:
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        # Generate sample data for testing
        price_data = generate_sample_price_data(symbols, days)
        
        config = BacktestConfig(
            initial_capital=100000,
            position_size_pct=10,
            max_positions=5
        )
        
        backtester = Backtester(config)
        
        if strategy_name == "all":
            result = backtester.run_multi_strategy(
                self.strategy_engine,
                price_data
            )
        else:
            # Find specific strategy
            strategy = None
            for s in self.strategy_engine.strategies:
                if s.name.lower() == strategy_name.lower():
                    strategy = s
                    break
            
            if not strategy:
                return {"error": f"Strategy '{strategy_name}' not found"}
            
            result = backtester.run(strategy, price_data)
        
        return result.to_dict()

    def set_price_alert(
        self,
        symbol: str,
        price: float,
        condition: str = "above"
    ) -> str:
        """Set a price alert"""
        cond_map = {
            "above": AlertCondition.ABOVE,
            "below": AlertCondition.BELOW,
            "crosses_above": AlertCondition.CROSSES_ABOVE,
            "crosses_below": AlertCondition.CROSSES_BELOW
        }
        
        alert = self.alert_manager.create_price_alert(
            symbol=symbol.upper(),
            condition=cond_map.get(condition, AlertCondition.ABOVE),
            threshold=price
        )
        
        return f"Alert set: {alert.name} (ID: {alert.id})"

    def get_market_overview(self) -> Dict:
        """Get market overview"""
        indices = self.market_data.get_market_indices()
        sectors = self.market_data.get_sector_performance()
        status = self.market_data.get_market_status()
        
        return {
            "market_status": status,
            "indices": {s: q.to_dict() for s, q in indices.items()},
            "sector_performance": sectors
        }

    def screen_stocks(
        self,
        symbols: List[str],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_volume: Optional[int] = None
    ) -> List[Dict]:
        """Screen stocks based on criteria"""
        return self.screener.screen(
            symbols,
            min_price=min_price,
            max_price=max_price,
            min_volume=min_volume
        )

    def chat(self, message: str) -> str:
        """
        Basic chat with the agent

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self.system_prompt + self.get_memory_context(),
            messages=self.conversation_history
        )

        # Extract assistant's response
        assistant_message = response.content[0].text

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat_with_tools(self, message: str) -> str:
        """
        Chat with tool integration for analysis

        Args:
            message: User's message

        Returns:
            Agent's response with analysis
        """
        # Define available tools
        tools = [
            {
                "name": "analyze_portfolio",
                "description": "Analyze the current portfolio including metrics, allocation, and risk",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_technical_analysis",
                "description": "Get technical analysis for a stock symbol",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_trading_signals",
                "description": "Get trading signals from multiple strategies",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_market_overview",
                "description": "Get market indices, sector performance, and status",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_stock_quote",
                "description": "Get current price quote for a stock",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "calculate_position_size",
                "description": "Calculate position size based on risk parameters",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "entry_price": {"type": "number"},
                        "stop_loss_price": {"type": "number"}
                    },
                    "required": ["symbol", "entry_price", "stop_loss_price"]
                }
            },
            {
                "name": "run_backtest",
                "description": "Run a backtest on trading strategies",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "strategy_name": {"type": "string", "description": "Strategy name or 'all'"},
                        "symbols": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": []
                }
            }
        ]

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response with tool use
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self.system_prompt + self.get_memory_context(),
            messages=self.conversation_history,
            tools=tools
        )

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    # Execute tool
                    result = self._execute_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            
            # Add assistant message and tool results
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt + self.get_memory_context(),
                messages=self.conversation_history,
                tools=tools
            )

        # Extract final response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, "text"):
                assistant_message += block.text

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # Extract and save preferences
        self._extract_and_save_preferences(message, assistant_message)

        return assistant_message

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool and return the result"""
        try:
            if tool_name == "analyze_portfolio":
                return self.analyze_portfolio()
            elif tool_name == "get_technical_analysis":
                return self.get_technical_analysis(tool_input["symbol"])
            elif tool_name == "get_trading_signals":
                return self.get_trading_signals(tool_input["symbol"])
            elif tool_name == "get_market_overview":
                return self.get_market_overview()
            elif tool_name == "get_stock_quote":
                quote = self.market_data.get_quote(tool_input["symbol"])
                return quote.to_dict()
            elif tool_name == "calculate_position_size":
                return self.calculate_position_size(
                    tool_input["symbol"],
                    tool_input["entry_price"],
                    tool_input["stop_loss_price"]
                )
            elif tool_name == "run_backtest":
                return self.run_backtest(
                    strategy_name=tool_input.get("strategy_name", "all"),
                    symbols=tool_input.get("symbols")
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def chat_with_memory(self, message: str) -> str:
        """
        Full-featured chat with memory

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        return self.chat_with_tools(message)

    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

    def get_history_length(self) -> int:
        """Get the number of messages in conversation history"""
        return len(self.conversation_history)

    def export_state(self, filepath: str):
        """Export agent state to file"""
        state = {
            "memory": self.memory,
            "risk_profile": self.risk_profile.to_dict(),
            "watchlists": self.watchlist_manager.to_dict(),
            "alerts": self.alert_manager.to_dict(),
            "portfolio": self.portfolio.to_dict() if self.portfolio else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"State exported to {filepath}")

    def import_state(self, filepath: str):
        """Import agent state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.memory = state.get("memory", self._create_empty_memory())
            
            if state.get("risk_profile"):
                rp = state["risk_profile"]
                self.risk_profile = RiskProfile(
                    risk_level=RiskLevel(rp.get("risk_level", "moderate")),
                    max_position_size_pct=rp.get("max_position_size_pct", 10),
                    max_portfolio_risk_pct=rp.get("max_portfolio_risk_pct", 2)
                )
            
            print(f"State imported from {filepath}")
        except Exception as e:
            print(f"Error importing state: {e}")
