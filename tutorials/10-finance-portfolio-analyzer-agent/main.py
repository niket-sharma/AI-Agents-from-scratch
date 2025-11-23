#!/usr/bin/env python3
"""
Finance Portfolio Analyzer - CLI Interface

Interactive command-line interface for the finance agent with full capabilities:
- Skills for portfolio analysis and Excel reporting
- Computer use for file operations
- MCP integration for real-time stock data
- Memory for persistent user preferences
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import FinanceAgent


def print_welcome():
    """Print welcome message with agent capabilities"""
    print("=" * 70)
    print(" " * 15 + "FINANCE PORTFOLIO ANALYZER")
    print("=" * 70)
    print("\nWelcome! I'm your AI-powered financial advisor assistant.")
    print("\nCapabilities:")
    print("  - Portfolio Analysis: Analyze your investment holdings and calculate metrics")
    print("  - Excel Reports: Generate professional formatted reports")
    print("  - Real-time Data: Fetch current stock prices via MCP")
    print("  - Memory: Remember your preferences across sessions")
    print("\nCommands:")
    print("  quit          - Exit the application")
    print("  reset         - Clear conversation history")
    print("  memory        - View current memory")
    print("  clear memory  - Erase all preferences")
    print("\nExample queries:")
    print("  - I'm a conservative investor focused on retirement")
    print("  - Analyze the portfolio in data/sample_portfolio.csv")
    print("  - What's the current price of AAPL?")
    print("  - Generate an Excel report for my portfolio")
    print("=" * 70)
    print()


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
        return

    # Print welcome message
    print_welcome()

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "quit":
                print("\nThank you for using Finance Portfolio Analyzer. Goodbye!")
                break

            elif user_input.lower() == "reset":
                agent.reset()
                continue

            elif user_input.lower() == "memory":
                print("\n" + agent.view_memory())
                continue

            elif user_input.lower() == "clear memory":
                agent.clear_memory()
                continue

            # Regular conversation with full capabilities
            print("\nAgent: ", end="", flush=True)
            try:
                response = agent.chat_with_memory(user_input)
                print(response)
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit or continue chatting.")
            continue
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
