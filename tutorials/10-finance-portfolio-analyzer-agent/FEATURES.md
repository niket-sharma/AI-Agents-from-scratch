# Enhanced Trading Features Guide

This document details all the advanced trading and analysis features added to the Finance Portfolio Analyzer Agent.

## Table of Contents

1. [Portfolio Management](#portfolio-management)
2. [Technical Analysis](#technical-analysis)
3. [Trading Strategies](#trading-strategies)
4. [Risk Management](#risk-management)
5. [Backtesting](#backtesting)
6. [Alerts & Monitoring](#alerts--monitoring)
7. [Market Data](#market-data)
8. [Usage Examples](#usage-examples)

---

## Portfolio Management

**Module**: `src/portfolio.py`

### Features

#### Portfolio Class
- Track multiple positions with full P&L
- Calculate total market value and gain/loss
- Asset allocation by sector and asset class
- Concentration risk analysis (HHI index)
- Rebalancing recommendations
- Import from CSV files

#### Position Class
- Symbol, shares, purchase price, current price
- Cost basis and market value calculations
- Return percentage and gain/loss
- Asset class and sector classification

### Usage

```python
from portfolio import Portfolio, Position, AssetClass, Sector

# Create portfolio
portfolio = Portfolio(name="My Portfolio")

# Add positions
portfolio.add_position(Position(
    symbol="AAPL",
    shares=100,
    purchase_price=150.0,
    current_price=180.0,
    asset_class=AssetClass.EQUITY,
    sector=Sector.TECHNOLOGY
))

# Analyze
metrics = portfolio.calculate_portfolio_metrics()
allocation = portfolio.get_allocation_by_sector()
concentration = portfolio.calculate_concentration_risk()
rebalance = portfolio.calculate_rebalancing(target_allocation)
```

---

## Technical Analysis

**Module**: `src/technical_indicators.py`

### Available Indicators

| Indicator | Description | Parameters |
|-----------|-------------|------------|
| SMA | Simple Moving Average | period |
| EMA | Exponential Moving Average | period |
| WMA | Weighted Moving Average | period |
| RSI | Relative Strength Index | period (default 14) |
| MACD | Moving Average Convergence Divergence | fast, slow, signal |
| Stochastic | Stochastic Oscillator | k_period, d_period |
| Bollinger Bands | Volatility bands | period, std_dev |
| ATR | Average True Range | period (default 14) |
| ADX | Average Directional Index | period (default 14) |
| OBV | On-Balance Volume | - |
| VWAP | Volume Weighted Average Price | - |
| Pivot Points | Support/resistance levels | - |
| Fibonacci | Retracement levels | - |
| CCI | Commodity Channel Index | period |
| Williams %R | Williams Percent Range | period |

### Signal Generation

```python
from technical_indicators import SignalGenerator, generate_technical_report

# Full analysis
report = generate_technical_report(
    closes, highs, lows, volumes
)

# Individual signals
signals = SignalGenerator.generate_signals(
    closes, highs, lows, volumes
)
```

### Report Output

The technical report includes:
- **Trend Analysis**: Direction, strength, ADX value
- **Momentum**: RSI, MACD, Stochastic readings
- **Volatility**: ATR, Bollinger Band width
- **Volume**: OBV trend, volume momentum
- **Support/Resistance**: Pivot points, Fibonacci levels
- **Overall Signal**: BUY/SELL/HOLD with confidence

---

## Trading Strategies

**Module**: `src/trading_strategy.py`

### Built-in Strategies

#### 1. Moving Average Crossover
- Uses fast EMA (12) and slow EMA (26)
- BUY when fast crosses above slow
- SELL when fast crosses below slow

#### 2. RSI Mean Reversion
- BUY when RSI < 30 (oversold)
- SELL when RSI > 70 (overbought)
- Neutral between 45-55

#### 3. Bollinger Band Breakout
- BUY on lower band touch with high volume
- SELL on upper band touch with high volume
- Uses ATR for volatility confirmation

#### 4. MACD Strategy
- BUY on bullish MACD crossover
- SELL on bearish MACD crossover
- Uses histogram for momentum

#### 5. Trend Following
- Uses ADX for trend strength
- Only trades when ADX > 20
- Follows +DI/-DI direction

### Strategy Engine

```python
from trading_strategy import create_default_strategy_engine

engine = create_default_strategy_engine()

# Get consensus from all strategies
result = engine.get_consensus_signal(
    symbol, closes, highs, lows, volumes
)

print(f"Signal: {result['consensus']['signal']}")
print(f"Confidence: {result['consensus']['confidence']:.1%}")
```

### Order Management

```python
from trading_strategy import OrderManager, OrderSide, OrderType

manager = OrderManager()

# Create order
order = manager.create_order(
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=100,
    order_type=OrderType.LIMIT,
    price=175.00,
    stop_loss=170.00,
    take_profit=190.00
)
```

---

## Risk Management

**Module**: `src/risk_management.py`

### Position Sizing Methods

| Method | Description | Best For |
|--------|-------------|----------|
| Fixed Fractional | Risk fixed % per trade | Consistent risk |
| Kelly Criterion | Optimal growth sizing | High win rate strategies |
| ATR-Based | Size based on volatility | Volatile assets |
| Volatility-Adjusted | Normalize risk by volatility | Multi-asset portfolios |

```python
from risk_management import PositionSizer

# Fixed fractional (2% risk per trade)
result = PositionSizer.fixed_fractional(
    portfolio_value=100000,
    risk_pct=2.0,
    entry_price=180,
    stop_loss_price=175
)
# Returns: shares, position_value, risk_amount

# Kelly sizing
result = PositionSizer.kelly_criterion(
    portfolio_value=100000,
    win_rate=0.60,
    avg_win=200,
    avg_loss=100,
    entry_price=180
)
```

### Value at Risk (VaR)

```python
from risk_management import VaRCalculator

# Historical VaR
var_95 = VaRCalculator.historical(returns, confidence=0.95)

# Parametric VaR
var_99 = VaRCalculator.parametric(
    returns, confidence=0.99, 
    portfolio_value=100000
)

# Monte Carlo VaR
var_mc = VaRCalculator.monte_carlo(
    returns, confidence=0.95,
    simulations=10000,
    portfolio_value=100000
)
```

### Risk Metrics

```python
from risk_management import RiskAdjustedMetrics

# Calculate all ratios
sharpe = RiskAdjustedMetrics.sharpe_ratio(returns)
sortino = RiskAdjustedMetrics.sortino_ratio(returns)
calmar = RiskAdjustedMetrics.calmar_ratio(returns, max_drawdown)
treynor = RiskAdjustedMetrics.treynor_ratio(returns, beta, rf)
info = RiskAdjustedMetrics.information_ratio(returns, benchmark)
```

### Drawdown Analysis

```python
from risk_management import DrawdownAnalyzer

analysis = DrawdownAnalyzer.analyze(equity_values)
# Returns: max_drawdown, max_drawdown_duration, 
#          current_drawdown, recovery_percentage
```

---

## Backtesting

**Module**: `src/backtesting.py`

### Basic Backtest

```python
from backtesting import Backtester, BacktestConfig
from trading_strategy import create_default_strategy_engine

# Configure
config = BacktestConfig(
    initial_capital=100000,
    commission_pct=0.1,
    slippage_pct=0.05,
    position_size_pct=10,
    max_positions=5
)

# Run
backtester = Backtester(config)
engine = create_default_strategy_engine()

result = backtester.run_multi_strategy(engine, price_data)

print(f"Return: {result.total_return_pct:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Win Rate: {result.win_rate:.1%}")
```

### Walk-Forward Analysis

```python
from backtesting import WalkForwardAnalyzer

analyzer = WalkForwardAnalyzer(strategy, window_size=60)
results = analyzer.analyze(price_data, step_size=20)
```

### Performance Metrics

The backtest result includes:
- Total return and CAGR
- Sharpe, Sortino, Calmar ratios
- Win rate and profit factor
- Maximum drawdown
- Total trades and trade list
- Equity curve data

---

## Alerts & Monitoring

**Module**: `src/alerts.py`

### Alert Types

| Type | Description |
|------|-------------|
| PRICE | Trigger on price level |
| TECHNICAL | RSI overbought/oversold, MACD cross |
| PORTFOLIO | Drawdown warning, rebalancing |
| RISK | Position limit breach, VaR threshold |

### Create Alerts

```python
from alerts import AlertManager, AlertCondition, AlertPriority

manager = AlertManager()

# Price alert
alert = manager.create_price_alert(
    symbol="AAPL",
    condition=AlertCondition.ABOVE,
    threshold=200.00,
    priority=AlertPriority.HIGH
)

# Technical alert
alert = manager.create_technical_alert(
    symbol="TSLA",
    indicator="RSI",
    condition=AlertCondition.BELOW,
    threshold=30
)
```

### Watchlist Management

```python
from alerts import WatchlistManager

watchlists = WatchlistManager()
watchlists.create_watchlist("Tech Giants", ["AAPL", "MSFT", "GOOGL"])
watchlists.add_symbol("Tech Giants", "META")
symbols = watchlists.get_symbols("Tech Giants")
```

### Portfolio Monitor

```python
from alerts import PortfolioMonitor

monitor = PortfolioMonitor(portfolio, alert_manager)
triggered = monitor.check_all()
```

---

## Market Data

**Module**: `src/market_data.py`

### MarketDataService

```python
from market_data import MarketDataService

service = MarketDataService(api_key="your_key")

# Single quote
quote = service.get_quote("AAPL")
print(f"{quote.symbol}: ${quote.price}")

# Multiple quotes
quotes = service.get_multiple_quotes(["AAPL", "MSFT", "GOOGL"])

# Historical data
bars = service.get_historical_data("AAPL", outputsize="full")

# Company info
overview = service.get_company_overview("AAPL")

# Sector performance
sectors = service.get_sector_performance()

# Market status
status = service.get_market_status()
```

### Stock Screener

```python
from market_data import ScreenerService

screener = ScreenerService(market_data_service)

# Screen by criteria
results = screener.screen(
    symbols=["AAPL", "MSFT", "GOOGL", "META"],
    min_price=100,
    max_price=300,
    min_volume=1000000
)

# Get movers
gainers = screener.get_top_gainers(symbols, n=5)
losers = screener.get_top_losers(symbols, n=5)
```

---

## Usage Examples

### Complete Trading Analysis Workflow

```python
from finance_agent import FinanceAgent

# Initialize
agent = FinanceAgent()

# Load portfolio
agent.load_portfolio("data/sample_portfolio.csv")

# Analyze portfolio
analysis = agent.analyze_portfolio()

# Technical analysis on top holding
ta = agent.get_technical_analysis("AAPL")

# Get trading signals
signals = agent.get_trading_signals("AAPL")

# Calculate position size for new trade
sizing = agent.calculate_position_size(
    symbol="NVDA",
    entry_price=130,
    stop_loss_price=125
)

# Run backtest
backtest = agent.run_backtest(
    strategy_name="trend_following",
    symbols=["AAPL", "MSFT", "GOOGL"],
    days=252
)

# Set price alert
agent.set_price_alert("TSLA", 200, "above")

# Get market overview
market = agent.get_market_overview()
```

### Using the CLI

```bash
# Start the agent
python main.py

# Quick commands
> portfolio          # View portfolio
> analyze AAPL       # Technical analysis
> signals MSFT       # Trading signals
> market             # Market overview
> backtest           # Run backtest

# Natural language
> What are the best opportunities in my portfolio?
> Should I add to my NVDA position?
> Calculate position size for buying GOOGL at $175 with stop at $170
```

---

## Best Practices

### Risk Management
1. Never risk more than 2% per trade
2. Use stop losses on all positions
3. Diversify across sectors and asset classes
4. Monitor portfolio drawdown regularly

### Technical Analysis
1. Confirm signals with multiple indicators
2. Consider the broader trend before trading
3. Use appropriate timeframes for your strategy
4. Volume confirms price movements

### Backtesting
1. Use out-of-sample data for validation
2. Account for transaction costs and slippage
3. Be wary of overfitting
4. Walk-forward test before live trading

### Alerts
1. Set alerts for key support/resistance levels
2. Monitor portfolio risk metrics
3. Track sector rotation
4. Regular rebalancing checks

---

## Disclaimer

**For Educational Purposes Only**

This software is designed for learning about trading systems and financial analysis. It does not constitute financial advice. Always:

- Consult qualified financial advisors
- Understand the risks of trading
- Paper trade before using real money
- Never invest more than you can afford to lose

Past performance does not guarantee future results.
