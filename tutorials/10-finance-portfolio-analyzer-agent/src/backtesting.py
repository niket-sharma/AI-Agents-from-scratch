"""
Backtesting Framework

Provides comprehensive strategy backtesting:
- Historical simulation
- Performance metrics
- Transaction costs
- Slippage modeling
- Monte Carlo simulation
- Walk-forward analysis
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum
import math
import json

from trading_strategy import (
    TradingStrategy, StrategyEngine, Signal, OrderSide,
    Trade, Order, OrderType
)
from risk_management import RiskAdjustedMetrics, DrawdownAnalyzer


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_capital: float = 100000.0
    commission_per_trade: float = 0.0  # Fixed commission
    commission_pct: float = 0.001  # 0.1% commission
    slippage_pct: float = 0.0005  # 0.05% slippage
    position_size_pct: float = 10.0  # % of portfolio per trade
    max_positions: int = 10  # Maximum concurrent positions
    risk_per_trade_pct: float = 1.0  # Risk % per trade
    use_stop_loss: bool = True
    use_take_profit: bool = True
    reinvest_profits: bool = True
    allow_shorting: bool = False
    margin_requirement: float = 1.0  # 1.0 = no margin


@dataclass
class BacktestPosition:
    """Position during backtest"""
    symbol: str
    side: OrderSide
    shares: float
    entry_price: float
    entry_date: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.shares * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        if self.side == OrderSide.BUY:
            return (self.current_price - self.entry_price) * self.shares
        else:
            return (self.entry_price - self.current_price) * self.shares
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100


@dataclass
class BacktestTrade:
    """Completed backtest trade"""
    symbol: str
    side: OrderSide
    shares: float
    entry_price: float
    exit_price: float
    entry_date: datetime
    exit_date: datetime
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    exit_reason: str  # signal, stop_loss, take_profit, end_of_test
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "shares": self.shares,
            "entry_price": round(self.entry_price, 2),
            "exit_price": round(self.exit_price, 2),
            "entry_date": self.entry_date.isoformat(),
            "exit_date": self.exit_date.isoformat(),
            "pnl": round(self.pnl, 2),
            "pnl_pct": round(self.pnl_pct, 2),
            "commission": round(self.commission, 2),
            "slippage": round(self.slippage, 2),
            "exit_reason": self.exit_reason,
            "holding_days": (self.exit_date - self.entry_date).days
        }


@dataclass
class BacktestResult:
    """Backtest results"""
    config: BacktestConfig
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    trades: List[BacktestTrade] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)
    
    @property
    def total_return(self) -> float:
        return ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
    
    @property
    def total_return_annualized(self) -> float:
        days = (self.end_date - self.start_date).days
        if days == 0:
            return 0.0
        years = days / 365.25
        if years == 0:
            return 0.0
        return ((self.final_capital / self.initial_capital) ** (1 / years) - 1) * 100
    
    @property
    def num_trades(self) -> int:
        return len(self.trades)
    
    @property
    def winning_trades(self) -> List[BacktestTrade]:
        return [t for t in self.trades if t.pnl > 0]
    
    @property
    def losing_trades(self) -> List[BacktestTrade]:
        return [t for t in self.trades if t.pnl < 0]
    
    @property
    def win_rate(self) -> float:
        if not self.trades:
            return 0.0
        return (len(self.winning_trades) / len(self.trades)) * 100
    
    @property
    def avg_win(self) -> float:
        if not self.winning_trades:
            return 0.0
        return sum(t.pnl for t in self.winning_trades) / len(self.winning_trades)
    
    @property
    def avg_loss(self) -> float:
        if not self.losing_trades:
            return 0.0
        return sum(t.pnl for t in self.losing_trades) / len(self.losing_trades)
    
    @property
    def profit_factor(self) -> float:
        gross_profit = sum(t.pnl for t in self.winning_trades)
        gross_loss = abs(sum(t.pnl for t in self.losing_trades))
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return gross_profit / gross_loss
    
    @property
    def max_drawdown(self) -> float:
        if not self.equity_curve:
            return 0.0
        
        peak = self.equity_curve[0][1]
        max_dd = 0.0
        
        for _, equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    @property
    def sharpe_ratio(self) -> float:
        if not self.daily_returns or len(self.daily_returns) < 2:
            return 0.0
        return RiskAdjustedMetrics.sharpe_ratio(self.daily_returns)
    
    @property
    def sortino_ratio(self) -> float:
        if not self.daily_returns or len(self.daily_returns) < 2:
            return 0.0
        return RiskAdjustedMetrics.sortino_ratio(self.daily_returns)
    
    @property
    def calmar_ratio(self) -> float:
        if self.max_drawdown == 0:
            return 0.0
        return self.total_return_annualized / self.max_drawdown
    
    def to_dict(self) -> Dict:
        return {
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat(),
                "trading_days": len(self.equity_curve)
            },
            "returns": {
                "initial_capital": round(self.initial_capital, 2),
                "final_capital": round(self.final_capital, 2),
                "total_return_pct": round(self.total_return, 2),
                "annualized_return_pct": round(self.total_return_annualized, 2)
            },
            "trades": {
                "total": self.num_trades,
                "winning": len(self.winning_trades),
                "losing": len(self.losing_trades),
                "win_rate": round(self.win_rate, 2),
                "avg_win": round(self.avg_win, 2),
                "avg_loss": round(self.avg_loss, 2),
                "profit_factor": round(self.profit_factor, 2),
                "largest_win": round(max((t.pnl for t in self.trades), default=0), 2),
                "largest_loss": round(min((t.pnl for t in self.trades), default=0), 2)
            },
            "risk": {
                "max_drawdown_pct": round(self.max_drawdown, 2),
                "sharpe_ratio": self.sharpe_ratio,
                "sortino_ratio": self.sortino_ratio,
                "calmar_ratio": round(self.calmar_ratio, 2)
            },
            "costs": {
                "total_commissions": round(sum(t.commission for t in self.trades), 2),
                "total_slippage": round(sum(t.slippage for t in self.trades), 2)
            }
        }
    
    def to_json(self, include_trades: bool = False) -> str:
        data = self.to_dict()
        if include_trades:
            data["trade_history"] = [t.to_dict() for t in self.trades]
        return json.dumps(data, indent=2)


class Backtester:
    """Strategy backtesting engine"""
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.positions: Dict[str, BacktestPosition] = {}
        self.cash: float = 0.0
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.daily_returns: List[float] = []
    
    def run(
        self,
        strategy: TradingStrategy,
        price_data: Dict[str, List[Dict]],  # symbol -> list of OHLCV dicts
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BacktestResult:
        """
        Run backtest for a single strategy
        
        Args:
            strategy: Trading strategy to test
            price_data: Historical price data by symbol
            start_date: Start date for backtest
            end_date: End date for backtest
        
        Returns:
            BacktestResult
        """
        # Initialize
        self.cash = self.config.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Get all unique dates
        all_dates = set()
        for symbol_data in price_data.values():
            for bar in symbol_data:
                if isinstance(bar.get("timestamp"), str):
                    bar["timestamp"] = datetime.fromisoformat(bar["timestamp"])
                all_dates.add(bar["timestamp"].date())
        
        sorted_dates = sorted(all_dates)
        
        if start_date:
            sorted_dates = [d for d in sorted_dates if d >= start_date.date()]
        if end_date:
            sorted_dates = [d for d in sorted_dates if d <= end_date.date()]
        
        if not sorted_dates:
            return BacktestResult(
                config=self.config,
                start_date=start_date or datetime.now(),
                end_date=end_date or datetime.now(),
                initial_capital=self.config.initial_capital,
                final_capital=self.config.initial_capital
            )
        
        prev_equity = self.config.initial_capital
        
        # Process each trading day
        for date in sorted_dates:
            current_datetime = datetime.combine(date, datetime.min.time())
            
            # Update positions with current prices
            for symbol, position in list(self.positions.items()):
                symbol_data = price_data.get(symbol, [])
                current_bar = self._get_bar_for_date(symbol_data, date)
                
                if current_bar:
                    position.current_price = current_bar["close"]
                    
                    # Check stop loss
                    if self.config.use_stop_loss and position.stop_loss:
                        if position.side == OrderSide.BUY and current_bar["low"] <= position.stop_loss:
                            self._close_position(symbol, position.stop_loss, current_datetime, "stop_loss")
                            continue
                        elif position.side == OrderSide.SELL and current_bar["high"] >= position.stop_loss:
                            self._close_position(symbol, position.stop_loss, current_datetime, "stop_loss")
                            continue
                    
                    # Check take profit
                    if self.config.use_take_profit and position.take_profit:
                        if position.side == OrderSide.BUY and current_bar["high"] >= position.take_profit:
                            self._close_position(symbol, position.take_profit, current_datetime, "take_profit")
                            continue
                        elif position.side == OrderSide.SELL and current_bar["low"] <= position.take_profit:
                            self._close_position(symbol, position.take_profit, current_datetime, "take_profit")
                            continue
            
            # Generate signals for each symbol
            for symbol, symbol_data in price_data.items():
                # Get historical data up to current date
                historical = [b for b in symbol_data if b["timestamp"].date() <= date]
                
                if len(historical) < 50:  # Need minimum history
                    continue
                
                closes = [b["close"] for b in historical]
                highs = [b["high"] for b in historical]
                lows = [b["low"] for b in historical]
                volumes = [b.get("volume", 0) for b in historical]
                
                # Generate signal
                signal = strategy.generate_signal(symbol, closes, highs, lows, volumes)
                current_price = closes[-1]
                
                # Process signal
                if symbol in self.positions:
                    position = self.positions[symbol]
                    
                    # Check for exit signal
                    if position.side == OrderSide.BUY and signal.signal in [Signal.SELL, Signal.STRONG_SELL]:
                        self._close_position(symbol, current_price, current_datetime, "signal")
                    elif position.side == OrderSide.SELL and signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
                        self._close_position(symbol, current_price, current_datetime, "signal")
                else:
                    # Check for entry signal
                    if len(self.positions) < self.config.max_positions:
                        if signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
                            self._open_position(
                                symbol, OrderSide.BUY, current_price,
                                current_datetime, signal.stop_loss, signal.take_profit
                            )
                        elif self.config.allow_shorting and signal.signal in [Signal.SELL, Signal.STRONG_SELL]:
                            self._open_position(
                                symbol, OrderSide.SELL, current_price,
                                current_datetime, signal.stop_loss, signal.take_profit
                            )
            
            # Calculate equity
            equity = self._calculate_equity()
            self.equity_curve.append((current_datetime, equity))
            
            # Calculate daily return
            daily_return = (equity - prev_equity) / prev_equity if prev_equity > 0 else 0
            self.daily_returns.append(daily_return)
            prev_equity = equity
        
        # Close remaining positions
        final_date = datetime.combine(sorted_dates[-1], datetime.min.time())
        for symbol in list(self.positions.keys()):
            position = self.positions[symbol]
            self._close_position(symbol, position.current_price, final_date, "end_of_test")
        
        return BacktestResult(
            config=self.config,
            start_date=datetime.combine(sorted_dates[0], datetime.min.time()),
            end_date=final_date,
            initial_capital=self.config.initial_capital,
            final_capital=self._calculate_equity(),
            trades=self.trades,
            equity_curve=self.equity_curve,
            daily_returns=self.daily_returns
        )
    
    def run_multi_strategy(
        self,
        engine: StrategyEngine,
        price_data: Dict[str, List[Dict]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_consensus: float = 0.6
    ) -> BacktestResult:
        """
        Run backtest with multiple strategies using consensus
        
        Args:
            engine: Strategy engine with multiple strategies
            price_data: Historical price data
            start_date: Start date
            end_date: End date
            min_consensus: Minimum consensus required for trades
        
        Returns:
            BacktestResult
        """
        # Initialize
        self.cash = self.config.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Get all unique dates
        all_dates = set()
        for symbol_data in price_data.values():
            for bar in symbol_data:
                if isinstance(bar.get("timestamp"), str):
                    bar["timestamp"] = datetime.fromisoformat(bar["timestamp"])
                all_dates.add(bar["timestamp"].date())
        
        sorted_dates = sorted(all_dates)
        
        if start_date:
            sorted_dates = [d for d in sorted_dates if d >= start_date.date()]
        if end_date:
            sorted_dates = [d for d in sorted_dates if d <= end_date.date()]
        
        if not sorted_dates:
            return BacktestResult(
                config=self.config,
                start_date=start_date or datetime.now(),
                end_date=end_date or datetime.now(),
                initial_capital=self.config.initial_capital,
                final_capital=self.config.initial_capital
            )
        
        prev_equity = self.config.initial_capital
        
        for date in sorted_dates:
            current_datetime = datetime.combine(date, datetime.min.time())
            
            # Update positions and check stops
            for symbol, position in list(self.positions.items()):
                symbol_data = price_data.get(symbol, [])
                current_bar = self._get_bar_for_date(symbol_data, date)
                
                if current_bar:
                    position.current_price = current_bar["close"]
                    
                    if self.config.use_stop_loss and position.stop_loss:
                        if position.side == OrderSide.BUY and current_bar["low"] <= position.stop_loss:
                            self._close_position(symbol, position.stop_loss, current_datetime, "stop_loss")
                            continue
                    
                    if self.config.use_take_profit and position.take_profit:
                        if position.side == OrderSide.BUY and current_bar["high"] >= position.take_profit:
                            self._close_position(symbol, position.take_profit, current_datetime, "take_profit")
                            continue
            
            # Generate consensus signals
            for symbol, symbol_data in price_data.items():
                historical = [b for b in symbol_data if b["timestamp"].date() <= date]
                
                if len(historical) < 50:
                    continue
                
                closes = [b["close"] for b in historical]
                highs = [b["high"] for b in historical]
                lows = [b["low"] for b in historical]
                volumes = [b.get("volume", 0) for b in historical]
                
                # Get consensus signal
                consensus = engine.get_consensus_signal(
                    symbol, closes, highs, lows, volumes, min_consensus
                )
                
                current_price = closes[-1]
                
                if not consensus["meets_consensus_threshold"]:
                    continue
                
                signal_str = consensus["consensus"]
                
                # Process signal
                if symbol in self.positions:
                    position = self.positions[symbol]
                    
                    if position.side == OrderSide.BUY and signal_str in ["sell", "strong_sell"]:
                        self._close_position(symbol, current_price, current_datetime, "signal")
                    elif position.side == OrderSide.SELL and signal_str in ["buy", "strong_buy"]:
                        self._close_position(symbol, current_price, current_datetime, "signal")
                else:
                    if len(self.positions) < self.config.max_positions:
                        if signal_str in ["buy", "strong_buy"]:
                            self._open_position(
                                symbol, OrderSide.BUY, current_price,
                                current_datetime,
                                consensus.get("recommended_stop_loss"),
                                consensus.get("recommended_take_profit")
                            )
            
            equity = self._calculate_equity()
            self.equity_curve.append((current_datetime, equity))
            
            daily_return = (equity - prev_equity) / prev_equity if prev_equity > 0 else 0
            self.daily_returns.append(daily_return)
            prev_equity = equity
        
        # Close remaining positions
        final_date = datetime.combine(sorted_dates[-1], datetime.min.time())
        for symbol in list(self.positions.keys()):
            position = self.positions[symbol]
            self._close_position(symbol, position.current_price, final_date, "end_of_test")
        
        return BacktestResult(
            config=self.config,
            start_date=datetime.combine(sorted_dates[0], datetime.min.time()),
            end_date=final_date,
            initial_capital=self.config.initial_capital,
            final_capital=self._calculate_equity(),
            trades=self.trades,
            equity_curve=self.equity_curve,
            daily_returns=self.daily_returns
        )
    
    def _get_bar_for_date(self, data: List[Dict], date) -> Optional[Dict]:
        """Get price bar for a specific date"""
        for bar in data:
            if bar["timestamp"].date() == date:
                return bar
        return None
    
    def _calculate_equity(self) -> float:
        """Calculate total portfolio equity"""
        position_value = sum(p.market_value for p in self.positions.values())
        return self.cash + position_value
    
    def _open_position(
        self,
        symbol: str,
        side: OrderSide,
        price: float,
        date: datetime,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ):
        """Open a new position"""
        equity = self._calculate_equity()
        
        if self.config.reinvest_profits:
            position_value = equity * (self.config.position_size_pct / 100)
        else:
            position_value = self.config.initial_capital * (self.config.position_size_pct / 100)
        
        # Apply slippage
        slippage = price * self.config.slippage_pct
        entry_price = price + slippage if side == OrderSide.BUY else price - slippage
        
        # Calculate shares
        shares = position_value / entry_price
        
        # Check if we have enough cash
        required_cash = shares * entry_price * self.config.margin_requirement
        if required_cash > self.cash:
            shares = (self.cash / self.config.margin_requirement) / entry_price
        
        if shares <= 0:
            return
        
        # Deduct cash and commission
        commission = self.config.commission_per_trade + (shares * entry_price * self.config.commission_pct)
        self.cash -= (shares * entry_price) + commission
        
        self.positions[symbol] = BacktestPosition(
            symbol=symbol,
            side=side,
            shares=shares,
            entry_price=entry_price,
            entry_date=date,
            stop_loss=stop_loss,
            take_profit=take_profit,
            current_price=price
        )
    
    def _close_position(
        self,
        symbol: str,
        price: float,
        date: datetime,
        reason: str
    ):
        """Close a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Apply slippage
        slippage = price * self.config.slippage_pct
        exit_price = price - slippage if position.side == OrderSide.BUY else price + slippage
        
        # Calculate P&L
        if position.side == OrderSide.BUY:
            pnl = (exit_price - position.entry_price) * position.shares
        else:
            pnl = (position.entry_price - exit_price) * position.shares
        
        # Commission
        commission = self.config.commission_per_trade + (position.shares * exit_price * self.config.commission_pct)
        pnl -= commission
        
        # Add cash back
        self.cash += position.shares * exit_price - commission
        
        # Record trade
        self.trades.append(BacktestTrade(
            symbol=symbol,
            side=position.side,
            shares=position.shares,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_date=position.entry_date,
            exit_date=date,
            pnl=pnl,
            pnl_pct=(pnl / (position.entry_price * position.shares)) * 100,
            commission=commission,
            slippage=abs(price - exit_price) * position.shares,
            exit_reason=reason
        ))
        
        del self.positions[symbol]


class WalkForwardAnalyzer:
    """Walk-forward optimization and analysis"""
    
    def __init__(
        self,
        in_sample_pct: float = 0.7,
        num_folds: int = 5
    ):
        self.in_sample_pct = in_sample_pct
        self.num_folds = num_folds
    
    def analyze(
        self,
        strategy: TradingStrategy,
        price_data: Dict[str, List[Dict]],
        config: Optional[BacktestConfig] = None
    ) -> Dict:
        """
        Perform walk-forward analysis
        
        Args:
            strategy: Strategy to analyze
            price_data: Historical price data
            config: Backtest configuration
        
        Returns:
            Walk-forward analysis results
        """
        config = config or BacktestConfig()
        
        # Get date range
        all_dates = set()
        for symbol_data in price_data.values():
            for bar in symbol_data:
                if isinstance(bar.get("timestamp"), str):
                    bar["timestamp"] = datetime.fromisoformat(bar["timestamp"])
                all_dates.add(bar["timestamp"].date())
        
        sorted_dates = sorted(all_dates)
        
        if len(sorted_dates) < 100:
            return {"error": "Insufficient data for walk-forward analysis"}
        
        fold_size = len(sorted_dates) // self.num_folds
        results = []
        
        for i in range(self.num_folds):
            fold_start = i * fold_size
            fold_end = (i + 1) * fold_size if i < self.num_folds - 1 else len(sorted_dates)
            
            fold_dates = sorted_dates[fold_start:fold_end]
            in_sample_size = int(len(fold_dates) * self.in_sample_pct)
            
            in_sample_dates = fold_dates[:in_sample_size]
            out_sample_dates = fold_dates[in_sample_size:]
            
            if not out_sample_dates:
                continue
            
            # Run backtests
            backtester = Backtester(config)
            
            in_sample_result = backtester.run(
                strategy, price_data,
                start_date=datetime.combine(in_sample_dates[0], datetime.min.time()),
                end_date=datetime.combine(in_sample_dates[-1], datetime.min.time())
            )
            
            out_sample_result = backtester.run(
                strategy, price_data,
                start_date=datetime.combine(out_sample_dates[0], datetime.min.time()),
                end_date=datetime.combine(out_sample_dates[-1], datetime.min.time())
            )
            
            results.append({
                "fold": i + 1,
                "in_sample": {
                    "return": in_sample_result.total_return,
                    "sharpe": in_sample_result.sharpe_ratio,
                    "max_drawdown": in_sample_result.max_drawdown,
                    "win_rate": in_sample_result.win_rate,
                    "num_trades": in_sample_result.num_trades
                },
                "out_sample": {
                    "return": out_sample_result.total_return,
                    "sharpe": out_sample_result.sharpe_ratio,
                    "max_drawdown": out_sample_result.max_drawdown,
                    "win_rate": out_sample_result.win_rate,
                    "num_trades": out_sample_result.num_trades
                }
            })
        
        # Calculate summary statistics
        in_sample_returns = [r["in_sample"]["return"] for r in results]
        out_sample_returns = [r["out_sample"]["return"] for r in results]
        
        return {
            "num_folds": len(results),
            "in_sample_pct": self.in_sample_pct,
            "fold_results": results,
            "summary": {
                "in_sample": {
                    "avg_return": round(sum(in_sample_returns) / len(in_sample_returns), 2) if in_sample_returns else 0,
                    "avg_sharpe": round(sum(r["in_sample"]["sharpe"] for r in results) / len(results), 2) if results else 0
                },
                "out_sample": {
                    "avg_return": round(sum(out_sample_returns) / len(out_sample_returns), 2) if out_sample_returns else 0,
                    "avg_sharpe": round(sum(r["out_sample"]["sharpe"] for r in results) / len(results), 2) if results else 0
                },
                "robustness_ratio": round(
                    (sum(out_sample_returns) / len(out_sample_returns)) /
                    (sum(in_sample_returns) / len(in_sample_returns)), 2
                ) if in_sample_returns and sum(in_sample_returns) != 0 else 0
            }
        }


def generate_sample_price_data(
    symbols: List[str],
    days: int = 252,
    start_price: float = 100.0
) -> Dict[str, List[Dict]]:
    """Generate sample price data for testing"""
    import random
    
    data = {}
    
    for symbol in symbols:
        bars = []
        price = start_price * (1 + random.uniform(-0.3, 0.3))
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            # Random walk with trend
            change = random.gauss(0.0002, 0.015)  # Slight positive drift
            price *= (1 + change)
            
            high = price * (1 + random.uniform(0, 0.02))
            low = price * (1 - random.uniform(0, 0.02))
            open_price = price * (1 + random.uniform(-0.01, 0.01))
            
            bars.append({
                "timestamp": date,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(price, 2),
                "volume": random.randint(1000000, 10000000)
            })
        
        data[symbol] = bars
    
    return data
