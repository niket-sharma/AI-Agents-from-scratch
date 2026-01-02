#!/usr/bin/env python3
"""
Finance Portfolio Analyzer - Enhanced CLI Interface

A comprehensive AI-powered trading and finance assistant with:
- Portfolio management and analysis
- Technical analysis with 15+ indicators
- Trading signal generation from multiple strategies
- Risk management and position sizing
- Backtesting framework
- Alerts and notifications
- Real-time market data via MCP
- Memory for persistent preferences
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import the enhanced agent, fall back to basic if dependencies missing
try:
    from finance_agent import FinanceAgent
    ENHANCED_MODE = True
except ImportError:
    from agent import FinanceAgent
    ENHANCED_MODE = False


def print_welcome():
    """Print welcome message with agent capabilities"""
    print("=" * 70)
    print(" " * 12 + "FINANCE PORTFOLIO ANALYZER & TRADING AGENT")
    print("=" * 70)
    print("\nWelcome! I'm your AI-powered financial advisor and trading assistant.")
    
    if ENHANCED_MODE:
        print("\n🚀 ENHANCED MODE - Full trading capabilities enabled")
    else:
        print("\n⚠️  BASIC MODE - Some features may be limited")
    
    print("\n📊 Portfolio Management:")
    print("  - Analyze holdings, diversification, and performance")
    print("  - Asset allocation and rebalancing recommendations")
    print("  - Risk metrics and concentration analysis")
    
    print("\n📈 Technical Analysis:")
    print("  - 15+ technical indicators (RSI, MACD, Bollinger, etc.)")
    print("  - Support/resistance levels and trend detection")
    print("  - Trading signals with confidence scores")
    
    print("\n🎯 Trading Strategies:")
    print("  - Multiple built-in strategies (trend, momentum, mean reversion)")
    print("  - Multi-strategy consensus signals")
    print("  - Backtesting framework with performance metrics")
    
    print("\n⚠️  Risk Management:")
    print("  - Position sizing (Kelly, fixed fractional, volatility-based)")
    print("  - Value at Risk (VaR) calculations")
    print("  - Sharpe, Sortino, and Calmar ratios")
    
    print("\n🔔 Alerts & Monitoring:")
    print("  - Price alerts and technical alerts")
    print("  - Portfolio monitoring")
    print("  - Watchlist management")
    
    print("\n💡 Commands:")
    print("  quit              - Exit the application")
    print("  reset             - Clear conversation history")
    print("  memory            - View saved preferences")
    print("  clear memory      - Erase all preferences")
    print("  portfolio         - View current portfolio")
    print("  analyze [symbol]  - Quick technical analysis")
    print("  signals [symbol]  - Get trading signals")
    print("  market            - Market overview")
    print("  backtest          - Run strategy backtest")
    print("  export            - Export agent state")
    
    print("\n📝 Example queries:")
    print("  - Analyze my portfolio in data/sample_portfolio.csv")
    print("  - Give me technical analysis for AAPL")
    print("  - What are the trading signals for MSFT?")
    print("  - Calculate position size for GOOGL entry at $180, stop at $175")
    print("  - Backtest the trend following strategy")
    print("  - Set an alert when NVDA goes above $150")
    print("=" * 70)
    print()


def handle_quick_commands(agent, user_input: str) -> bool:
    """
    Handle quick commands that don't need AI processing
    
    Returns:
        True if command was handled, False otherwise
    """
    parts = user_input.lower().split()
    cmd = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd == "portfolio":
        if not ENHANCED_MODE:
            print("Portfolio analysis requires enhanced mode.")
            return True
        result = agent.analyze_portfolio()
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n📊 Portfolio Analysis:")
            metrics = result.get("metrics", {})
            print(f"  Total Value: ${metrics.get('total_market_value', 0):,.2f}")
            print(f"  Total Gain/Loss: ${metrics.get('total_gain_loss', 0):,.2f}")
            print(f"  Return: {metrics.get('total_return_pct', 0):.2f}%")
            print(f"  Positions: {metrics.get('position_count', 0)}")
            
            allocation = result.get("allocation", {})
            if allocation:
                print("\n  Asset Allocation:")
                for asset_class, pct in allocation.items():
                    print(f"    {asset_class}: {pct:.1f}%")
        return True
    
    elif cmd == "analyze" and args:
        if not ENHANCED_MODE:
            print("Technical analysis requires enhanced mode.")
            return True
        symbol = args[0].upper()
        print(f"\n📈 Technical Analysis for {symbol}:")
        result = agent.get_technical_analysis(symbol)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            # Print key metrics
            if "trend" in result:
                print(f"  Trend: {result['trend'].get('direction', 'N/A')}")
            if "momentum" in result:
                print(f"  RSI: {result['momentum'].get('rsi', 'N/A'):.1f}")
            if "overall_signal" in result:
                print(f"  Signal: {result['overall_signal']}")
        return True
    
    elif cmd == "signals" and args:
        if not ENHANCED_MODE:
            print("Trading signals require enhanced mode.")
            return True
        symbol = args[0].upper()
        print(f"\n🎯 Trading Signals for {symbol}:")
        result = agent.get_trading_signals(symbol)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            consensus = result.get("consensus", {})
            print(f"  Signal: {consensus.get('signal', 'N/A')}")
            print(f"  Confidence: {consensus.get('confidence', 0):.1%}")
            print(f"  Agreeing Strategies: {consensus.get('agreeing_strategies', 0)}/{consensus.get('total_strategies', 0)}")
        return True
    
    elif cmd == "market":
        if not ENHANCED_MODE:
            print("Market overview requires enhanced mode.")
            return True
        print("\n🌍 Market Overview:")
        result = agent.get_market_overview()
        status = result.get("market_status", {})
        print(f"  Market: {status.get('status', 'Unknown')}")
        print(f"  Current Time: {status.get('current_time', 'N/A')}")
        
        sectors = result.get("sector_performance", {})
        if sectors:
            print("\n  Sector Performance:")
            for sector, perf in list(sectors.items())[:5]:
                print(f"    {sector}: {perf:+.2f}%")
        return True
    
    elif cmd == "backtest":
        if not ENHANCED_MODE:
            print("Backtesting requires enhanced mode.")
            return True
        strategy = args[0] if args else "all"
        print(f"\n🔬 Running Backtest ({strategy})...")
        result = agent.run_backtest(strategy_name=strategy)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"  Total Return: {result.get('total_return_pct', 0):.2f}%")
            print(f"  Win Rate: {result.get('win_rate', 0):.1%}")
            print(f"  Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
            print(f"  Max Drawdown: {result.get('max_drawdown_pct', 0):.2f}%")
            print(f"  Total Trades: {result.get('total_trades', 0)}")
        return True
    
    elif cmd == "export":
        if not ENHANCED_MODE:
            print("Export requires enhanced mode.")
            return True
        filepath = args[0] if args else "agent_state.json"
        agent.export_state(filepath)
        return True
    
    return False


def main():
    """Main CLI loop"""
    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return

    # Initialize agent
    try:
        agent = FinanceAgent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # Print welcome message
    print_welcome()

    # Try to load default portfolio
    if ENHANCED_MODE:
        default_portfolio = "data/sample_portfolio.csv"
        if os.path.exists(default_portfolio):
            result = agent.load_portfolio(default_portfolio)
            print(f"📂 {result}\n")

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle quit command
            if user_input.lower() == "quit":
                print("\nThank you for using Finance Portfolio Analyzer. Goodbye!")
                # Save state on exit if enhanced mode
                if ENHANCED_MODE:
                    agent.export_state("agent_state_autosave.json")
                    print("💾 State auto-saved to agent_state_autosave.json")
                break

            # Handle reset command
            elif user_input.lower() == "reset":
                agent.reset()
                continue

            # Handle memory command
            elif user_input.lower() == "memory":
                print("\n" + agent.view_memory())
                continue

            # Handle clear memory command
            elif user_input.lower() == "clear memory":
                agent.clear_memory()
                continue
            
            # Handle help command
            elif user_input.lower() == "help":
                print_welcome()
                continue

            # Try quick commands first
            if ENHANCED_MODE and handle_quick_commands(agent, user_input):
                continue

            # Regular conversation with full capabilities
            print("\nAgent: ", end="", flush=True)
            try:
                response = agent.chat_with_memory(user_input)
                print(response)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                print("Please try again or type 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit or continue chatting.")
            continue
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
