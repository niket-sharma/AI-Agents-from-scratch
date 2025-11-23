"""
MCP Server for Stock Data

Provides real-time stock price data via Alpha Vantage API
"""

import os
import json
import requests
from datetime import datetime
import pytz
from mcp.server import Server
from mcp.types import Tool, TextContent


# Initialize MCP server
server = Server("stock-data")

# Alpha Vantage API configuration
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"


def get_market_status() -> dict:
    """
    Check if the US stock market is currently open

    Returns:
        dict with status and message
    """
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)

    # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    if now.weekday() >= 5:  # Saturday or Sunday
        return {
            "is_open": False,
            "message": "Market is closed (weekend)",
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
        }

    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)

    if market_open <= now <= market_close:
        return {
            "is_open": True,
            "message": "Market is currently open",
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
    else:
        return {
            "is_open": False,
            "message": "Market is closed (outside trading hours)",
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
        }


def fetch_stock_quote(symbol: str) -> dict:
    """
    Fetch real-time quote for a single stock

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict with quote data or error
    """
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY
        }

        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()

        if "Global Quote" not in data or not data["Global Quote"]:
            return {
                "error": f"No data found for symbol {symbol}. Please check the symbol.",
                "symbol": symbol
            }

        quote = data["Global Quote"]

        return {
            "symbol": quote.get("01. symbol", symbol),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "0%").rstrip('%'),
            "volume": int(quote.get("06. volume", 0)),
            "latest_trading_day": quote.get("07. latest trading day", "N/A")
        }

    except requests.RequestException as e:
        return {
            "error": f"Network error: {str(e)}",
            "symbol": symbol
        }
    except Exception as e:
        return {
            "error": f"Error fetching quote: {str(e)}",
            "symbol": symbol
        }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_stock_price",
            description="Get current price and trading data for a single stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_multiple_quotes",
            description="Get current prices for multiple stock symbols",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols"
                    }
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="get_market_status",
            description="Check if the US stock market is currently open for trading",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    if name == "get_market_status":
        status = get_market_status()
        return [
            TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )
        ]

    elif name == "get_stock_price":
        symbol = arguments.get("symbol", "").upper()
        if not symbol:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "Symbol is required"})
                )
            ]

        quote = fetch_stock_quote(symbol)
        return [
            TextContent(
                type="text",
                text=json.dumps(quote, indent=2)
            )
        ]

    elif name == "get_multiple_quotes":
        symbols = arguments.get("symbols", [])
        if not symbols:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "At least one symbol is required"})
                )
            ]

        quotes = {}
        for symbol in symbols:
            symbol = symbol.upper()
            quotes[symbol] = fetch_stock_quote(symbol)

        return [
            TextContent(
                type="text",
                text=json.dumps(quotes, indent=2)
            )
        ]

    else:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )
        ]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
