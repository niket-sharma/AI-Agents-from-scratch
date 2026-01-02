"""
Trading Strategy Engine

Provides strategy development and signal generation:
- Pre-built trading strategies
- Strategy combination and voting
- Entry/exit signal generation
- Order management
- Trade execution simulation
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod

from technical_indicators import TechnicalIndicators, SignalGenerator, Signal
from risk_management import PositionSizer, StopLoss, TakeProfit


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order statuses"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Trade order representation"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "limit_price": self.limit_price,
            "status": self.status.value,
            "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "created_at": self.created_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit
        }


@dataclass
class Trade:
    """Completed trade"""
    id: str
    symbol: str
    side: OrderSide
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_percent: float = 0.0
    holding_period_days: int = 0
    strategy: str = ""
    notes: str = ""
    
    @property
    def is_closed(self) -> bool:
        return self.exit_price is not None
    
    def close(self, exit_price: float, exit_time: Optional[datetime] = None):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_time = exit_time or datetime.now()
        
        if self.side == OrderSide.BUY:
            self.pnl = (exit_price - self.entry_price) * self.quantity
        else:
            self.pnl = (self.entry_price - exit_price) * self.quantity
        
        self.pnl_percent = (self.pnl / (self.entry_price * self.quantity)) * 100
        self.holding_period_days = (self.exit_time - self.entry_time).days
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "pnl": round(self.pnl, 2),
            "pnl_percent": round(self.pnl_percent, 2),
            "holding_period_days": self.holding_period_days,
            "strategy": self.strategy,
            "is_closed": self.is_closed
        }


@dataclass
class StrategySignal:
    """Trading signal from a strategy"""
    symbol: str
    signal: Signal
    strategy_name: str
    confidence: float  # 0-1
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "signal": self.signal.value,
            "strategy_name": self.strategy_name,
            "confidence": round(self.confidence, 2),
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class TradingStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.parameters: Dict = {}
    
    @abstractmethod
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        """Generate trading signal"""
        pass
    
    def calculate_stops(
        self,
        entry_price: float,
        signal: Signal,
        atr: Optional[float] = None,
        risk_reward_ratio: float = 2.0
    ) -> Tuple[float, float]:
        """Calculate stop loss and take profit"""
        if atr:
            stop_distance = atr * 2
        else:
            stop_distance = entry_price * 0.02  # 2% default
        
        if signal in [Signal.BUY, Signal.STRONG_BUY]:
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + (stop_distance * risk_reward_ratio)
        else:
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - (stop_distance * risk_reward_ratio)
        
        return round(stop_loss, 2), round(take_profit, 2)


class MovingAverageCrossover(TradingStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 20,
        ma_type: str = "ema"
    ):
        super().__init__("MA Crossover")
        self.parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "ma_type": ma_type
        }
    
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        ti = TechnicalIndicators
        
        if self.parameters["ma_type"] == "ema":
            fast_ma = ti.ema(closes, self.parameters["fast_period"])
            slow_ma = ti.ema(closes, self.parameters["slow_period"])
        else:
            fast_ma = ti.sma(closes, self.parameters["fast_period"])
            slow_ma = ti.sma(closes, self.parameters["slow_period"])
        
        if fast_ma[-1] is None or slow_ma[-1] is None:
            return StrategySignal(
                symbol=symbol,
                signal=Signal.NEUTRAL,
                strategy_name=self.name,
                confidence=0
            )
        
        # Check for crossover
        current_above = fast_ma[-1] > slow_ma[-1]
        prev_above = fast_ma[-2] > slow_ma[-2] if len(fast_ma) > 1 and fast_ma[-2] else current_above
        
        if current_above and not prev_above:
            signal = Signal.BUY
            confidence = min(abs(fast_ma[-1] - slow_ma[-1]) / slow_ma[-1] * 100, 1.0)
        elif not current_above and prev_above:
            signal = Signal.SELL
            confidence = min(abs(fast_ma[-1] - slow_ma[-1]) / slow_ma[-1] * 100, 1.0)
        else:
            signal = Signal.NEUTRAL
            confidence = 0.3
        
        entry_price = closes[-1]
        atr = ti.atr(highs or closes, lows or closes, closes)
        atr_val = atr[-1] if atr[-1] else None
        stop_loss, take_profit = self.calculate_stops(entry_price, signal, atr_val)
        
        return StrategySignal(
            symbol=symbol,
            signal=signal,
            strategy_name=self.name,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={
                "fast_ma": round(fast_ma[-1], 2),
                "slow_ma": round(slow_ma[-1], 2)
            }
        )


class RSIMeanReversion(TradingStrategy):
    """RSI Mean Reversion Strategy"""
    
    def __init__(
        self,
        rsi_period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ):
        super().__init__("RSI Mean Reversion")
        self.parameters = {
            "rsi_period": rsi_period,
            "oversold": oversold,
            "overbought": overbought
        }
    
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        ti = TechnicalIndicators
        
        rsi = ti.rsi(closes, self.parameters["rsi_period"])
        
        if rsi[-1] is None:
            return StrategySignal(
                symbol=symbol,
                signal=Signal.NEUTRAL,
                strategy_name=self.name,
                confidence=0
            )
        
        rsi_val = rsi[-1]
        
        if rsi_val <= self.parameters["oversold"]:
            signal = Signal.STRONG_BUY if rsi_val <= 20 else Signal.BUY
            confidence = (self.parameters["oversold"] - rsi_val) / self.parameters["oversold"]
        elif rsi_val >= self.parameters["overbought"]:
            signal = Signal.STRONG_SELL if rsi_val >= 80 else Signal.SELL
            confidence = (rsi_val - self.parameters["overbought"]) / (100 - self.parameters["overbought"])
        else:
            signal = Signal.NEUTRAL
            confidence = 0.3
        
        entry_price = closes[-1]
        atr = ti.atr(highs or closes, lows or closes, closes)
        atr_val = atr[-1] if atr[-1] else None
        stop_loss, take_profit = self.calculate_stops(entry_price, signal, atr_val)
        
        return StrategySignal(
            symbol=symbol,
            signal=signal,
            strategy_name=self.name,
            confidence=min(confidence, 1.0),
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={"rsi": round(rsi_val, 2)}
        )


class BollingerBandBreakout(TradingStrategy):
    """Bollinger Band Breakout Strategy"""
    
    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0
    ):
        super().__init__("Bollinger Breakout")
        self.parameters = {
            "period": period,
            "std_dev": std_dev
        }
    
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        ti = TechnicalIndicators
        
        upper, middle, lower = ti.bollinger_bands(
            closes,
            self.parameters["period"],
            self.parameters["std_dev"]
        )
        
        if upper[-1] is None or lower[-1] is None:
            return StrategySignal(
                symbol=symbol,
                signal=Signal.NEUTRAL,
                strategy_name=self.name,
                confidence=0
            )
        
        current_price = closes[-1]
        prev_price = closes[-2] if len(closes) > 1 else current_price
        
        # Breakout signals
        if current_price > upper[-1] and prev_price <= upper[-2]:
            signal = Signal.SELL  # Overbought, potential reversal
            confidence = 0.7
        elif current_price < lower[-1] and prev_price >= lower[-2]:
            signal = Signal.BUY  # Oversold, potential reversal
            confidence = 0.7
        elif current_price > middle[-1]:
            signal = Signal.NEUTRAL
            confidence = 0.3
        else:
            signal = Signal.NEUTRAL
            confidence = 0.3
        
        entry_price = closes[-1]
        stop_loss, take_profit = self.calculate_stops(entry_price, signal)
        
        return StrategySignal(
            symbol=symbol,
            signal=signal,
            strategy_name=self.name,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={
                "upper_band": round(upper[-1], 2),
                "middle_band": round(middle[-1], 2),
                "lower_band": round(lower[-1], 2)
            }
        )


class MACDStrategy(TradingStrategy):
    """MACD Crossover Strategy"""
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ):
        super().__init__("MACD Strategy")
        self.parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
    
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        ti = TechnicalIndicators
        
        macd_line, signal_line, histogram = ti.macd(
            closes,
            self.parameters["fast_period"],
            self.parameters["slow_period"],
            self.parameters["signal_period"]
        )
        
        if macd_line[-1] is None or signal_line[-1] is None:
            return StrategySignal(
                symbol=symbol,
                signal=Signal.NEUTRAL,
                strategy_name=self.name,
                confidence=0
            )
        
        # Check for crossover
        current_above = macd_line[-1] > signal_line[-1]
        prev_above = macd_line[-2] > signal_line[-2] if macd_line[-2] and signal_line[-2] else current_above
        
        if current_above and not prev_above:
            signal = Signal.BUY
            confidence = 0.7
        elif not current_above and prev_above:
            signal = Signal.SELL
            confidence = 0.7
        elif histogram[-1] and histogram[-1] > 0:
            signal = Signal.NEUTRAL
            confidence = 0.4
        else:
            signal = Signal.NEUTRAL
            confidence = 0.3
        
        # Strengthen signal if histogram is diverging
        if histogram[-1] and histogram[-2]:
            if histogram[-1] > histogram[-2] > 0:
                if signal == Signal.BUY:
                    signal = Signal.STRONG_BUY
                    confidence = 0.85
            elif histogram[-1] < histogram[-2] < 0:
                if signal == Signal.SELL:
                    signal = Signal.STRONG_SELL
                    confidence = 0.85
        
        entry_price = closes[-1]
        atr = ti.atr(highs or closes, lows or closes, closes)
        atr_val = atr[-1] if atr[-1] else None
        stop_loss, take_profit = self.calculate_stops(entry_price, signal, atr_val)
        
        return StrategySignal(
            symbol=symbol,
            signal=signal,
            strategy_name=self.name,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={
                "macd": round(macd_line[-1], 4),
                "signal": round(signal_line[-1], 4),
                "histogram": round(histogram[-1], 4) if histogram[-1] else None
            }
        )


class TrendFollowing(TradingStrategy):
    """ADX-based Trend Following Strategy"""
    
    def __init__(
        self,
        adx_period: int = 14,
        adx_threshold: float = 25.0,
        ma_period: int = 50
    ):
        super().__init__("Trend Following")
        self.parameters = {
            "adx_period": adx_period,
            "adx_threshold": adx_threshold,
            "ma_period": ma_period
        }
    
    def generate_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> StrategySignal:
        ti = TechnicalIndicators
        
        if highs is None:
            highs = closes
        if lows is None:
            lows = closes
        
        adx, plus_di, minus_di = ti.adx(highs, lows, closes, self.parameters["adx_period"])
        ma = ti.sma(closes, self.parameters["ma_period"])
        
        if adx[-1] is None or ma[-1] is None:
            return StrategySignal(
                symbol=symbol,
                signal=Signal.NEUTRAL,
                strategy_name=self.name,
                confidence=0
            )
        
        current_price = closes[-1]
        adx_val = adx[-1]
        plus_di_val = plus_di[-1] if plus_di[-1] else 0
        minus_di_val = minus_di[-1] if minus_di[-1] else 0
        
        # Strong trend present
        if adx_val >= self.parameters["adx_threshold"]:
            if plus_di_val > minus_di_val and current_price > ma[-1]:
                signal = Signal.STRONG_BUY if adx_val >= 40 else Signal.BUY
                confidence = min(adx_val / 50, 1.0)
            elif minus_di_val > plus_di_val and current_price < ma[-1]:
                signal = Signal.STRONG_SELL if adx_val >= 40 else Signal.SELL
                confidence = min(adx_val / 50, 1.0)
            else:
                signal = Signal.NEUTRAL
                confidence = 0.4
        else:
            signal = Signal.NEUTRAL
            confidence = 0.2
        
        entry_price = closes[-1]
        atr = ti.atr(highs, lows, closes)
        atr_val = atr[-1] if atr[-1] else None
        stop_loss, take_profit = self.calculate_stops(entry_price, signal, atr_val, risk_reward_ratio=2.5)
        
        return StrategySignal(
            symbol=symbol,
            signal=signal,
            strategy_name=self.name,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={
                "adx": round(adx_val, 2),
                "plus_di": round(plus_di_val, 2),
                "minus_di": round(minus_di_val, 2),
                "ma": round(ma[-1], 2),
                "trend_strength": "strong" if adx_val >= 40 else "moderate" if adx_val >= 25 else "weak"
            }
        )


class StrategyEngine:
    """Engine for running multiple strategies and combining signals"""
    
    def __init__(self):
        self.strategies: List[TradingStrategy] = []
        self.strategy_weights: Dict[str, float] = {}
    
    def add_strategy(self, strategy: TradingStrategy, weight: float = 1.0):
        """Add a strategy to the engine"""
        self.strategies.append(strategy)
        self.strategy_weights[strategy.name] = weight
    
    def remove_strategy(self, strategy_name: str):
        """Remove a strategy"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        self.strategy_weights.pop(strategy_name, None)
    
    def generate_signals(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None
    ) -> List[StrategySignal]:
        """Generate signals from all strategies"""
        signals = []
        
        for strategy in self.strategies:
            signal = strategy.generate_signal(symbol, closes, highs, lows, volumes)
            signals.append(signal)
        
        return signals
    
    def get_consensus_signal(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None,
        min_consensus: float = 0.6
    ) -> Dict:
        """
        Get consensus signal from all strategies
        
        Args:
            symbol: Stock symbol
            Price data lists
            min_consensus: Minimum agreement ratio required
        
        Returns:
            Consensus analysis
        """
        signals = self.generate_signals(symbol, closes, highs, lows, volumes)
        
        if not signals:
            return {
                "symbol": symbol,
                "consensus": Signal.NEUTRAL.value,
                "confidence": 0,
                "agreement_ratio": 0,
                "signals": []
            }
        
        # Convert to numeric for weighted voting
        signal_values = {
            Signal.STRONG_BUY: 2,
            Signal.BUY: 1,
            Signal.NEUTRAL: 0,
            Signal.SELL: -1,
            Signal.STRONG_SELL: -2
        }
        
        weighted_sum = 0
        total_weight = 0
        buy_count = 0
        sell_count = 0
        neutral_count = 0
        
        for sig in signals:
            weight = self.strategy_weights.get(sig.strategy_name, 1.0)
            weighted_sum += signal_values[sig.signal] * weight * sig.confidence
            total_weight += weight
            
            if sig.signal in [Signal.BUY, Signal.STRONG_BUY]:
                buy_count += 1
            elif sig.signal in [Signal.SELL, Signal.STRONG_SELL]:
                sell_count += 1
            else:
                neutral_count += 1
        
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine consensus signal
        if avg_score >= 1.5:
            consensus = Signal.STRONG_BUY
        elif avg_score >= 0.5:
            consensus = Signal.BUY
        elif avg_score <= -1.5:
            consensus = Signal.STRONG_SELL
        elif avg_score <= -0.5:
            consensus = Signal.SELL
        else:
            consensus = Signal.NEUTRAL
        
        # Calculate agreement ratio
        if consensus in [Signal.BUY, Signal.STRONG_BUY]:
            agreement = buy_count / len(signals)
        elif consensus in [Signal.SELL, Signal.STRONG_SELL]:
            agreement = sell_count / len(signals)
        else:
            agreement = neutral_count / len(signals)
        
        # Average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Get stop loss and take profit from agreeing strategies
        stop_losses = [s.stop_loss for s in signals if s.stop_loss and s.signal == consensus]
        take_profits = [s.take_profit for s in signals if s.take_profit and s.signal == consensus]
        
        return {
            "symbol": symbol,
            "consensus": consensus.value,
            "confidence": round(avg_confidence * agreement, 2),
            "score": round(avg_score, 2),
            "agreement_ratio": round(agreement, 2),
            "meets_consensus_threshold": agreement >= min_consensus,
            "signal_breakdown": {
                "buy": buy_count,
                "sell": sell_count,
                "neutral": neutral_count
            },
            "recommended_stop_loss": round(sum(stop_losses) / len(stop_losses), 2) if stop_losses else None,
            "recommended_take_profit": round(sum(take_profits) / len(take_profits), 2) if take_profits else None,
            "individual_signals": [s.to_dict() for s in signals]
        }


class OrderManager:
    """Manage trading orders"""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.next_order_id = 1
        self.next_trade_id = 1
    
    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """Create a new order"""
        order_id = f"ORD{self.next_order_id:06d}"
        self.next_order_id += 1
        
        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.orders[order_id] = order
        return order
    
    def fill_order(
        self,
        order_id: str,
        fill_price: float,
        fill_quantity: Optional[float] = None
    ) -> Order:
        """Fill an order"""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        fill_qty = fill_quantity or order.quantity
        
        order.filled_quantity = fill_qty
        order.filled_price = fill_price
        order.filled_at = datetime.now()
        order.status = OrderStatus.FILLED if fill_qty >= order.quantity else OrderStatus.PARTIALLY_FILLED
        
        # Create trade record
        trade = Trade(
            id=f"TRD{self.next_trade_id:06d}",
            symbol=order.symbol,
            side=order.side,
            entry_price=fill_price,
            exit_price=None,
            quantity=fill_qty,
            entry_time=datetime.now()
        )
        self.next_trade_id += 1
        self.trades.append(trade)
        
        return order
    
    def cancel_order(self, order_id: str) -> Order:
        """Cancel an order"""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        order.status = OrderStatus.CANCELLED
        return order
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders"""
        return [o for o in self.orders.values() if o.status in [OrderStatus.PENDING, OrderStatus.OPEN]]
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        return [t for t in self.trades if not t.is_closed]
    
    def close_trade(self, trade_id: str, exit_price: float) -> Trade:
        """Close a trade"""
        trade = next((t for t in self.trades if t.id == trade_id), None)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        trade.close(exit_price)
        return trade
    
    def get_trade_statistics(self) -> Dict:
        """Calculate trading statistics"""
        closed_trades = [t for t in self.trades if t.is_closed]
        
        if not closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "average_pnl": 0,
                "largest_win": 0,
                "largest_loss": 0,
                "average_holding_days": 0
            }
        
        winning = [t for t in closed_trades if t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in closed_trades)
        
        return {
            "total_trades": len(closed_trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": round(len(winning) / len(closed_trades) * 100, 2),
            "total_pnl": round(total_pnl, 2),
            "average_pnl": round(total_pnl / len(closed_trades), 2),
            "largest_win": round(max(t.pnl for t in winning), 2) if winning else 0,
            "largest_loss": round(min(t.pnl for t in losing), 2) if losing else 0,
            "average_holding_days": round(
                sum(t.holding_period_days for t in closed_trades) / len(closed_trades), 1
            ),
            "profit_factor": round(
                sum(t.pnl for t in winning) / abs(sum(t.pnl for t in losing)), 2
            ) if losing and sum(t.pnl for t in losing) != 0 else 0
        }


def create_default_strategy_engine() -> StrategyEngine:
    """Create engine with default strategies"""
    engine = StrategyEngine()
    
    engine.add_strategy(MovingAverageCrossover(fast_period=10, slow_period=20), weight=1.0)
    engine.add_strategy(RSIMeanReversion(rsi_period=14, oversold=30, overbought=70), weight=1.2)
    engine.add_strategy(MACDStrategy(), weight=1.0)
    engine.add_strategy(BollingerBandBreakout(), weight=0.8)
    engine.add_strategy(TrendFollowing(adx_threshold=25), weight=1.1)
    
    return engine
