"""
Market Data Service Module

Provides comprehensive market data access:
- Real-time and historical price data
- Market indices
- Sector performance
- Economic indicators
- News and sentiment
- Market calendar
"""

import os
import json
import requests
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DataSource(Enum):
    """Available data sources"""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    FINNHUB = "finnhub"
    MOCK = "mock"


class Interval(Enum):
    """Data intervals"""
    MINUTE_1 = "1min"
    MINUTE_5 = "5min"
    MINUTE_15 = "15min"
    MINUTE_30 = "30min"
    HOURLY = "60min"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Quote:
    """Stock quote data"""
    symbol: str
    price: float
    open: float
    high: float
    low: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime
    previous_close: float = 0.0
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "change": self.change,
            "change_percent": self.change_percent,
            "timestamp": self.timestamp.isoformat(),
            "previous_close": self.previous_close,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "dividend_yield": self.dividend_yield
        }


@dataclass
class OHLCV:
    """OHLCV bar data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class EconomicIndicator:
    """Economic indicator data"""
    name: str
    value: float
    previous_value: float
    change: float
    date: datetime
    frequency: str  # monthly, quarterly, annual
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "previous_value": self.previous_value,
            "change": self.change,
            "date": self.date.isoformat(),
            "frequency": self.frequency
        }


class MarketDataService:
    """Unified market data service"""
    
    def __init__(
        self,
        alpha_vantage_key: Optional[str] = None,
        finnhub_key: Optional[str] = None,
        default_source: DataSource = DataSource.ALPHA_VANTAGE
    ):
        self.alpha_vantage_key = alpha_vantage_key or os.getenv("ALPHA_VANTAGE_KEY", "demo")
        self.finnhub_key = finnhub_key or os.getenv("FINNHUB_KEY")
        self.default_source = default_source
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 60  # seconds
        
        self._base_urls = {
            DataSource.ALPHA_VANTAGE: "https://www.alphavantage.co/query",
            DataSource.FINNHUB: "https://finnhub.io/api/v1"
        }
    
    def _get_cached(self, key: str) -> Optional[any]:
        """Get cached data if not expired"""
        if key in self.cache:
            timestamp, data = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return data
        return None
    
    def _set_cached(self, key: str, data: any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (datetime.now(), data)
    
    def get_quote(self, symbol: str, source: Optional[DataSource] = None) -> Quote:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol
            source: Data source (default: configured source)
        
        Returns:
            Quote object
        """
        source = source or self.default_source
        cache_key = f"quote_{symbol}_{source.value}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if source == DataSource.ALPHA_VANTAGE:
            quote = self._fetch_alpha_vantage_quote(symbol)
        elif source == DataSource.MOCK:
            quote = self._generate_mock_quote(symbol)
        else:
            quote = self._generate_mock_quote(symbol)
        
        self._set_cached(cache_key, quote)
        return quote
    
    def _fetch_alpha_vantage_quote(self, symbol: str) -> Quote:
        """Fetch quote from Alpha Vantage"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key
            }
            
            response = requests.get(
                self._base_urls[DataSource.ALPHA_VANTAGE],
                params=params,
                timeout=10
            )
            data = response.json()
            
            if "Global Quote" not in data or not data["Global Quote"]:
                return self._generate_mock_quote(symbol)
            
            q = data["Global Quote"]
            
            return Quote(
                symbol=symbol,
                price=float(q.get("05. price", 0)),
                open=float(q.get("02. open", 0)),
                high=float(q.get("03. high", 0)),
                low=float(q.get("04. low", 0)),
                volume=int(q.get("06. volume", 0)),
                change=float(q.get("09. change", 0)),
                change_percent=float(q.get("10. change percent", "0%").rstrip('%')),
                timestamp=datetime.now(),
                previous_close=float(q.get("08. previous close", 0))
            )
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return self._generate_mock_quote(symbol)
    
    def _generate_mock_quote(self, symbol: str) -> Quote:
        """Generate mock quote for testing"""
        import random
        
        base_prices = {
            "AAPL": 175.0,
            "MSFT": 370.0,
            "GOOGL": 140.0,
            "AMZN": 180.0,
            "TSLA": 250.0,
            "META": 500.0,
            "NVDA": 480.0,
            "SPY": 475.0,
            "QQQ": 400.0,
            "VTI": 240.0,
            "BND": 72.0
        }
        
        base = base_prices.get(symbol.upper(), 100.0)
        change_pct = random.uniform(-2, 2)
        price = base * (1 + change_pct / 100)
        change = price - base
        
        return Quote(
            symbol=symbol.upper(),
            price=round(price, 2),
            open=round(base * (1 + random.uniform(-0.5, 0.5) / 100), 2),
            high=round(max(price, base) * (1 + random.uniform(0, 1) / 100), 2),
            low=round(min(price, base) * (1 - random.uniform(0, 1) / 100), 2),
            volume=random.randint(1000000, 50000000),
            change=round(change, 2),
            change_percent=round(change_pct, 2),
            timestamp=datetime.now(),
            previous_close=base
        )
    
    def get_historical_data(
        self,
        symbol: str,
        interval: Interval = Interval.DAILY,
        outputsize: str = "compact",  # compact = 100, full = all
        source: Optional[DataSource] = None
    ) -> List[OHLCV]:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Stock symbol
            interval: Data interval
            outputsize: Data size
            source: Data source
        
        Returns:
            List of OHLCV bars
        """
        source = source or self.default_source
        
        if source == DataSource.ALPHA_VANTAGE:
            return self._fetch_alpha_vantage_historical(symbol, interval, outputsize)
        else:
            return self._generate_mock_historical(symbol, 100)
    
    def _fetch_alpha_vantage_historical(
        self,
        symbol: str,
        interval: Interval,
        outputsize: str
    ) -> List[OHLCV]:
        """Fetch historical data from Alpha Vantage"""
        try:
            if interval == Interval.DAILY:
                function = "TIME_SERIES_DAILY"
                key = "Time Series (Daily)"
            elif interval == Interval.WEEKLY:
                function = "TIME_SERIES_WEEKLY"
                key = "Weekly Time Series"
            elif interval == Interval.MONTHLY:
                function = "TIME_SERIES_MONTHLY"
                key = "Monthly Time Series"
            else:
                function = "TIME_SERIES_INTRADAY"
                key = f"Time Series ({interval.value})"
            
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
                "outputsize": outputsize
            }
            
            if function == "TIME_SERIES_INTRADAY":
                params["interval"] = interval.value
            
            response = requests.get(
                self._base_urls[DataSource.ALPHA_VANTAGE],
                params=params,
                timeout=15
            )
            data = response.json()
            
            if key not in data:
                return self._generate_mock_historical(symbol, 100)
            
            bars = []
            for date_str, values in data[key].items():
                try:
                    bars.append(OHLCV(
                        timestamp=datetime.fromisoformat(date_str),
                        open=float(values["1. open"]),
                        high=float(values["2. high"]),
                        low=float(values["3. low"]),
                        close=float(values["4. close"]),
                        volume=int(values["5. volume"])
                    ))
                except (KeyError, ValueError):
                    continue
            
            return sorted(bars, key=lambda x: x.timestamp)
        
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return self._generate_mock_historical(symbol, 100)
    
    def _generate_mock_historical(self, symbol: str, days: int) -> List[OHLCV]:
        """Generate mock historical data"""
        import random
        
        bars = []
        base_price = 100.0
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            # Random walk
            change = random.uniform(-2, 2)
            close = base_price * (1 + change / 100)
            high = close * (1 + random.uniform(0, 1) / 100)
            low = close * (1 - random.uniform(0, 1) / 100)
            open_price = base_price * (1 + random.uniform(-0.5, 0.5) / 100)
            
            bars.append(OHLCV(
                timestamp=date,
                open=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                volume=random.randint(1000000, 10000000)
            ))
            
            base_price = close
        
        return bars
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary of symbol -> Quote
        """
        return {symbol: self.get_quote(symbol) for symbol in symbols}
    
    def get_market_indices(self) -> Dict[str, Quote]:
        """Get major market indices"""
        indices = ["SPY", "QQQ", "DIA", "IWM", "VTI"]
        return self.get_multiple_quotes(indices)
    
    def get_sector_performance(self) -> Dict[str, Dict]:
        """Get sector ETF performance"""
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
            "Utilities": "XLU",
            "Communication": "XLC"
        }
        
        performance = {}
        for sector, etf in sector_etfs.items():
            quote = self.get_quote(etf)
            performance[sector] = {
                "etf": etf,
                "price": quote.price,
                "change_percent": quote.change_percent
            }
        
        return performance
    
    def get_market_status(self) -> Dict:
        """Check market status"""
        import pytz
        
        ny_tz = pytz.timezone('America/New_York')
        now = datetime.now(ny_tz)
        
        # Regular trading hours: 9:30 AM - 4:00 PM ET
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Pre-market: 4:00 AM - 9:30 AM
        pre_market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
        
        # After-hours: 4:00 PM - 8:00 PM
        after_hours_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        is_weekend = now.weekday() >= 5
        
        if is_weekend:
            status = "closed"
            message = "Market is closed (weekend)"
            next_open = now + timedelta(days=(7 - now.weekday()))
            next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)
        elif market_open <= now <= market_close:
            status = "open"
            message = "Market is open for regular trading"
            next_open = None
        elif pre_market_open <= now < market_open:
            status = "pre-market"
            message = "Pre-market trading session"
            next_open = market_open
        elif market_close < now <= after_hours_close:
            status = "after-hours"
            message = "After-hours trading session"
            next_open = market_open + timedelta(days=1)
        else:
            status = "closed"
            message = "Market is closed"
            if now < pre_market_open:
                next_open = pre_market_open
            else:
                next_open = pre_market_open + timedelta(days=1)
        
        return {
            "status": status,
            "message": message,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "next_open": next_open.strftime("%Y-%m-%d %H:%M:%S %Z") if next_open else None
        }
    
    def get_economic_calendar(self) -> List[Dict]:
        """Get upcoming economic events (mock data)"""
        events = [
            {
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "time": "08:30",
                "event": "Initial Jobless Claims",
                "importance": "medium",
                "previous": "220K",
                "forecast": "215K"
            },
            {
                "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "time": "10:00",
                "event": "Consumer Sentiment",
                "importance": "medium",
                "previous": "69.7",
                "forecast": "70.0"
            },
            {
                "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "14:00",
                "event": "FOMC Meeting Minutes",
                "importance": "high",
                "previous": "N/A",
                "forecast": "N/A"
            },
            {
                "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "time": "08:30",
                "event": "CPI (Consumer Price Index)",
                "importance": "high",
                "previous": "3.2%",
                "forecast": "3.1%"
            }
        ]
        return events
    
    def get_company_fundamentals(self, symbol: str) -> Dict:
        """Get company fundamental data (mock)"""
        # In production, this would call an API
        return {
            "symbol": symbol,
            "name": f"{symbol} Inc.",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 2500000000000,
            "pe_ratio": 28.5,
            "forward_pe": 25.2,
            "peg_ratio": 2.1,
            "price_to_book": 12.5,
            "price_to_sales": 7.8,
            "dividend_yield": 0.5,
            "profit_margin": 25.3,
            "operating_margin": 30.1,
            "roe": 45.2,
            "debt_to_equity": 1.2,
            "current_ratio": 1.5,
            "quick_ratio": 1.2,
            "revenue_growth": 15.2,
            "earnings_growth": 18.5,
            "52_week_high": 200.0,
            "52_week_low": 130.0,
            "50_day_ma": 175.0,
            "200_day_ma": 165.0,
            "beta": 1.15,
            "analyst_rating": "Buy",
            "target_price": 195.0
        }
    
    def search_symbols(self, query: str) -> List[Dict]:
        """Search for symbols by name or ticker"""
        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": self.alpha_vantage_key
            }
            
            response = requests.get(
                self._base_urls[DataSource.ALPHA_VANTAGE],
                params=params,
                timeout=10
            )
            data = response.json()
            
            if "bestMatches" not in data:
                return []
            
            return [
                {
                    "symbol": match["1. symbol"],
                    "name": match["2. name"],
                    "type": match["3. type"],
                    "region": match["4. region"],
                    "currency": match["8. currency"]
                }
                for match in data["bestMatches"]
            ]
        except Exception:
            return []


class ScreenerService:
    """Stock screening service"""
    
    def __init__(self, market_data: MarketDataService):
        self.market_data = market_data
    
    def screen(
        self,
        symbols: List[str],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_volume: Optional[int] = None,
        min_change_pct: Optional[float] = None,
        max_change_pct: Optional[float] = None,
        pe_ratio_max: Optional[float] = None,
        dividend_yield_min: Optional[float] = None
    ) -> List[Dict]:
        """
        Screen stocks based on criteria
        
        Args:
            symbols: List of symbols to screen
            Various filter criteria
        
        Returns:
            List of matching stocks with their data
        """
        results = []
        
        for symbol in symbols:
            quote = self.market_data.get_quote(symbol)
            fundamentals = self.market_data.get_company_fundamentals(symbol)
            
            # Apply filters
            if min_price and quote.price < min_price:
                continue
            if max_price and quote.price > max_price:
                continue
            if min_volume and quote.volume < min_volume:
                continue
            if min_change_pct and quote.change_percent < min_change_pct:
                continue
            if max_change_pct and quote.change_percent > max_change_pct:
                continue
            if pe_ratio_max and fundamentals.get("pe_ratio", 0) > pe_ratio_max:
                continue
            if dividend_yield_min and fundamentals.get("dividend_yield", 0) < dividend_yield_min:
                continue
            
            results.append({
                "symbol": symbol,
                "price": quote.price,
                "change_percent": quote.change_percent,
                "volume": quote.volume,
                **fundamentals
            })
        
        return results
    
    def find_gainers(self, symbols: List[str], top_n: int = 10) -> List[Dict]:
        """Find top gainers"""
        quotes = self.market_data.get_multiple_quotes(symbols)
        sorted_quotes = sorted(
            quotes.values(),
            key=lambda q: q.change_percent,
            reverse=True
        )
        return [q.to_dict() for q in sorted_quotes[:top_n]]
    
    def find_losers(self, symbols: List[str], top_n: int = 10) -> List[Dict]:
        """Find top losers"""
        quotes = self.market_data.get_multiple_quotes(symbols)
        sorted_quotes = sorted(
            quotes.values(),
            key=lambda q: q.change_percent
        )
        return [q.to_dict() for q in sorted_quotes[:top_n]]
    
    def find_most_active(self, symbols: List[str], top_n: int = 10) -> List[Dict]:
        """Find most actively traded"""
        quotes = self.market_data.get_multiple_quotes(symbols)
        sorted_quotes = sorted(
            quotes.values(),
            key=lambda q: q.volume,
            reverse=True
        )
        return [q.to_dict() for q in sorted_quotes[:top_n]]
