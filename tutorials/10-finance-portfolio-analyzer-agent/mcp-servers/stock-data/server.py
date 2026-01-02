"""
MCP Server for Stock Data - Enhanced Finance Trading Agent

Provides comprehensive market data and trading tools:
- Real-time stock price data via Alpha Vantage API
- Technical analysis indicators
- Portfolio analysis
- Risk metrics
- Trading signals
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import pytz
from mcp.server import Server
from mcp.types import Tool, TextContent

# Add parent src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from technical_indicators import TechnicalIndicators, generate_technical_report
    from risk_management import VaRCalculator, RiskAdjustedMetrics
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False

# Initialize MCP server
server = Server("stock-data-enhanced")

# Alpha Vantage API configuration
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"

# Cache for price data
price_cache = {}
cache_ttl = 60  # seconds


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
    tools = [
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
        ),
        Tool(
            name="get_historical_data",
            description="Get historical daily price data for a stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "compact (100 data points) or full (all data)",
                        "enum": ["compact", "full"]
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_sector_performance",
            description="Get performance data for market sectors via sector ETFs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_market_indices",
            description="Get current values for major market indices (SPY, QQQ, DIA, IWM)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_symbol",
            description="Search for stock symbols by company name or keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "Company name or search keywords"
                    }
                },
                "required": ["keywords"]
            }
        ),
        Tool(
            name="get_company_overview",
            description="Get fundamental data and company overview for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]
    
    # Add advanced tools if modules are available
    if ADVANCED_FEATURES:
        tools.extend([
            Tool(
                name="get_technical_analysis",
                description="Get comprehensive technical analysis for a stock including RSI, MACD, Bollinger Bands, and trading signals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            Tool(
                name="calculate_position_size",
                description="Calculate optimal position size based on risk parameters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "portfolio_value": {
                            "type": "number",
                            "description": "Total portfolio value"
                        },
                        "risk_per_trade_pct": {
                            "type": "number",
                            "description": "Percentage of portfolio to risk per trade"
                        },
                        "entry_price": {
                            "type": "number",
                            "description": "Entry price for the trade"
                        },
                        "stop_loss_price": {
                            "type": "number",
                            "description": "Stop loss price"
                        }
                    },
                    "required": ["portfolio_value", "risk_per_trade_pct", "entry_price", "stop_loss_price"]
                }
            )
        ])
    
    return tools


def fetch_historical_data(symbol: str, outputsize: str = "compact") -> dict:
    """Fetch historical daily data"""
    try:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=15)
        data = response.json()
        
        if "Time Series (Daily)" not in data:
            return {"error": f"No historical data found for {symbol}", "symbol": symbol}
        
        time_series = data["Time Series (Daily)"]
        formatted_data = []
        
        for date, values in list(time_series.items())[:100]:
            formatted_data.append({
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"])
            })
        
        return {
            "symbol": symbol,
            "data_points": len(formatted_data),
            "data": formatted_data
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


def search_symbols(keywords: str) -> list:
    """Search for symbols"""
    try:
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if "bestMatches" not in data:
            return []
        
        return [
            {
                "symbol": match["1. symbol"],
                "name": match["2. name"],
                "type": match["3. type"],
                "region": match["4. region"]
            }
            for match in data["bestMatches"][:10]
        ]
    except Exception:
        return []


def get_company_overview(symbol: str) -> dict:
    """Get company fundamental data"""
    try:
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if not data or "Symbol" not in data:
            return {"error": f"No data found for {symbol}", "symbol": symbol}
        
        return {
            "symbol": data.get("Symbol"),
            "name": data.get("Name"),
            "description": data.get("Description", "")[:500],
            "sector": data.get("Sector"),
            "industry": data.get("Industry"),
            "market_cap": data.get("MarketCapitalization"),
            "pe_ratio": data.get("PERatio"),
            "peg_ratio": data.get("PEGRatio"),
            "dividend_yield": data.get("DividendYield"),
            "eps": data.get("EPS"),
            "revenue_ttm": data.get("RevenueTTM"),
            "profit_margin": data.get("ProfitMargin"),
            "52_week_high": data.get("52WeekHigh"),
            "52_week_low": data.get("52WeekLow"),
            "50_day_ma": data.get("50DayMovingAverage"),
            "200_day_ma": data.get("200DayMovingAverage"),
            "beta": data.get("Beta"),
            "analyst_target": data.get("AnalystTargetPrice")
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


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
    
    elif name == "get_historical_data":
        symbol = arguments.get("symbol", "").upper()
        outputsize = arguments.get("outputsize", "compact")
        
        if not symbol:
            return [TextContent(type="text", text=json.dumps({"error": "Symbol is required"}))]
        
        data = fetch_historical_data(symbol, outputsize)
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    
    elif name == "get_sector_performance":
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financial": "XLF",
            "Energy": "XLE",
            "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP",
            "Industrials": "XLI",
            "Materials": "XLB",
            "Real Estate": "XLRE",
            "Utilities": "XLU"
        }
        
        performance = {}
        for sector, etf in sector_etfs.items():
            quote = fetch_stock_quote(etf)
            performance[sector] = {
                "etf": etf,
                "price": quote.get("price", 0),
                "change_percent": quote.get("change_percent", "0")
            }
        
        return [TextContent(type="text", text=json.dumps(performance, indent=2))]
    
    elif name == "get_market_indices":
        indices = ["SPY", "QQQ", "DIA", "IWM", "VTI"]
        quotes = {symbol: fetch_stock_quote(symbol) for symbol in indices}
        return [TextContent(type="text", text=json.dumps(quotes, indent=2))]
    
    elif name == "search_symbol":
        keywords = arguments.get("keywords", "")
        if not keywords:
            return [TextContent(type="text", text=json.dumps({"error": "Keywords required"}))]
        
        results = search_symbols(keywords)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    elif name == "get_company_overview":
        symbol = arguments.get("symbol", "").upper()
        if not symbol:
            return [TextContent(type="text", text=json.dumps({"error": "Symbol is required"}))]
        
        overview = get_company_overview(symbol)
        return [TextContent(type="text", text=json.dumps(overview, indent=2))]
    
    elif name == "get_technical_analysis" and ADVANCED_FEATURES:
        symbol = arguments.get("symbol", "").upper()
        if not symbol:
            return [TextContent(type="text", text=json.dumps({"error": "Symbol is required"}))]
        
        # Get historical data
        hist_data = fetch_historical_data(symbol, "compact")
        if "error" in hist_data:
            return [TextContent(type="text", text=json.dumps(hist_data))]
        
        # Extract price arrays
        data = hist_data.get("data", [])
        if len(data) < 50:
            return [TextContent(type="text", text=json.dumps({"error": "Insufficient data for analysis"}))]
        
        # Reverse to chronological order
        data = list(reversed(data))
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        volumes = [d["volume"] for d in data]
        
        # Generate technical report
        report = generate_technical_report(closes, highs, lows, volumes)
        report["symbol"] = symbol
        
        return [TextContent(type="text", text=json.dumps(report, indent=2))]
    
    elif name == "calculate_position_size" and ADVANCED_FEATURES:
        from risk_management import PositionSizer
        
        portfolio_value = arguments.get("portfolio_value", 0)
        risk_pct = arguments.get("risk_per_trade_pct", 1.0)
        entry_price = arguments.get("entry_price", 0)
        stop_loss = arguments.get("stop_loss_price", 0)
        
        if not all([portfolio_value, entry_price, stop_loss]):
            return [TextContent(type="text", text=json.dumps({"error": "Missing required parameters"}))]
        
        result = PositionSizer.fixed_fractional(portfolio_value, risk_pct, entry_price, stop_loss)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

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
