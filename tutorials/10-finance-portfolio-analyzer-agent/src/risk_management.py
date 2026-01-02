"""
Risk Management Module

Provides comprehensive risk analysis and management:
- Position sizing (Kelly Criterion, Fixed Fractional, ATR-based)
- Value at Risk (VaR) calculations
- Portfolio risk metrics
- Stop loss and take profit management
- Risk-adjusted performance metrics
- Drawdown analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class RiskLevel(Enum):
    """Risk tolerance levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class RiskProfile:
    """User's risk profile configuration"""
    risk_level: RiskLevel = RiskLevel.MODERATE
    max_position_size_pct: float = 10.0  # Max % of portfolio in single position
    max_portfolio_risk_pct: float = 2.0  # Max % portfolio to risk per trade
    max_drawdown_pct: float = 20.0  # Maximum acceptable drawdown
    stop_loss_pct: float = 5.0  # Default stop loss percentage
    take_profit_pct: float = 15.0  # Default take profit percentage
    max_correlation: float = 0.7  # Max correlation between positions
    min_liquidity_ratio: float = 0.1  # Min liquidity (avg volume vs position)
    
    def to_dict(self) -> Dict:
        return {
            "risk_level": self.risk_level.value,
            "max_position_size_pct": self.max_position_size_pct,
            "max_portfolio_risk_pct": self.max_portfolio_risk_pct,
            "max_drawdown_pct": self.max_drawdown_pct,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct
        }


@dataclass
class StopLoss:
    """Stop loss order representation"""
    symbol: str
    entry_price: float
    stop_price: float
    stop_type: str = "fixed"  # fixed, trailing, atr-based
    trailing_pct: Optional[float] = None
    atr_multiplier: Optional[float] = None
    current_price: Optional[float] = None
    
    @property
    def risk_pct(self) -> float:
        """Calculate risk percentage from entry"""
        return ((self.entry_price - self.stop_price) / self.entry_price) * 100
    
    @property
    def is_triggered(self) -> bool:
        """Check if stop loss is triggered"""
        if self.current_price is None:
            return False
        return self.current_price <= self.stop_price
    
    def update_trailing(self, current_price: float) -> None:
        """Update trailing stop loss"""
        if self.stop_type != "trailing" or self.trailing_pct is None:
            return
        
        self.current_price = current_price
        new_stop = current_price * (1 - self.trailing_pct / 100)
        
        # Only move stop up, never down
        if new_stop > self.stop_price:
            self.stop_price = new_stop


@dataclass
class TakeProfit:
    """Take profit order representation"""
    symbol: str
    entry_price: float
    target_prices: List[float] = field(default_factory=list)  # Multiple targets
    target_percentages: List[float] = field(default_factory=list)  # % to sell at each
    current_price: Optional[float] = None
    
    @property
    def reward_risk_ratios(self) -> List[float]:
        """Calculate R:R for each target"""
        return [
            (target - self.entry_price) / self.entry_price * 100
            for target in self.target_prices
        ]


class PositionSizer:
    """Position sizing calculations"""
    
    @staticmethod
    def fixed_fractional(
        portfolio_value: float,
        risk_per_trade_pct: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Dict[str, float]:
        """
        Fixed fractional position sizing
        
        Args:
            portfolio_value: Total portfolio value
            risk_per_trade_pct: % of portfolio to risk per trade
            entry_price: Entry price
            stop_loss_price: Stop loss price
        
        Returns:
            Position sizing details
        """
        risk_amount = portfolio_value * (risk_per_trade_pct / 100)
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return {"error": "Stop loss cannot equal entry price"}
        
        shares = risk_amount / risk_per_share
        position_value = shares * entry_price
        position_pct = (position_value / portfolio_value) * 100
        
        return {
            "shares": round(shares, 2),
            "position_value": round(position_value, 2),
            "position_pct": round(position_pct, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_per_share": round(risk_per_share, 2)
        }
    
    @staticmethod
    def kelly_criterion(
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> Dict[str, float]:
        """
        Kelly Criterion for optimal position size
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade return
            avg_loss: Average losing trade return (positive number)
        
        Returns:
            Kelly fraction and recommendations
        """
        if avg_loss == 0:
            return {"error": "Average loss cannot be zero"}
        
        win_loss_ratio = avg_win / avg_loss
        
        # Kelly formula: f* = (bp - q) / b
        # where b = win/loss ratio, p = win rate, q = loss rate
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Half-Kelly is more conservative
        half_kelly = kelly_pct / 2
        
        # Quarter-Kelly for very conservative
        quarter_kelly = kelly_pct / 4
        
        return {
            "full_kelly_pct": round(kelly_pct * 100, 2),
            "half_kelly_pct": round(half_kelly * 100, 2),
            "quarter_kelly_pct": round(quarter_kelly * 100, 2),
            "win_rate": round(win_rate * 100, 2),
            "win_loss_ratio": round(win_loss_ratio, 2),
            "recommendation": "Use half-Kelly or less for safety"
        }
    
    @staticmethod
    def atr_based(
        portfolio_value: float,
        risk_per_trade_pct: float,
        entry_price: float,
        atr: float,
        atr_multiplier: float = 2.0
    ) -> Dict[str, float]:
        """
        ATR-based position sizing
        
        Args:
            portfolio_value: Total portfolio value
            risk_per_trade_pct: % of portfolio to risk
            entry_price: Entry price
            atr: Current ATR value
            atr_multiplier: Multiplier for ATR (default 2x)
        
        Returns:
            Position sizing with ATR-based stop
        """
        stop_distance = atr * atr_multiplier
        stop_price = entry_price - stop_distance
        
        return {
            **PositionSizer.fixed_fractional(
                portfolio_value, risk_per_trade_pct,
                entry_price, stop_price
            ),
            "atr": round(atr, 2),
            "atr_multiplier": atr_multiplier,
            "stop_distance": round(stop_distance, 2),
            "stop_price": round(stop_price, 2)
        }
    
    @staticmethod
    def volatility_adjusted(
        portfolio_value: float,
        target_volatility_pct: float,
        asset_volatility_pct: float,
        entry_price: float
    ) -> Dict[str, float]:
        """
        Volatility-adjusted position sizing
        
        Args:
            portfolio_value: Total portfolio value
            target_volatility_pct: Target portfolio volatility
            asset_volatility_pct: Asset's annualized volatility
            entry_price: Entry price
        
        Returns:
            Position sizing to achieve target volatility
        """
        if asset_volatility_pct == 0:
            return {"error": "Asset volatility cannot be zero"}
        
        # Position size = (Target Vol / Asset Vol) * Portfolio Value
        position_value = (target_volatility_pct / asset_volatility_pct) * portfolio_value
        shares = position_value / entry_price
        position_pct = (position_value / portfolio_value) * 100
        
        return {
            "shares": round(shares, 2),
            "position_value": round(position_value, 2),
            "position_pct": round(position_pct, 2),
            "target_volatility": target_volatility_pct,
            "asset_volatility": asset_volatility_pct,
            "volatility_ratio": round(target_volatility_pct / asset_volatility_pct, 2)
        }


class VaRCalculator:
    """Value at Risk calculations"""
    
    @staticmethod
    def historical_var(
        returns: List[float],
        confidence_level: float = 0.95,
        portfolio_value: float = 100000
    ) -> Dict[str, float]:
        """
        Historical VaR calculation
        
        Args:
            returns: Historical daily returns
            confidence_level: Confidence level (default 95%)
            portfolio_value: Portfolio value
        
        Returns:
            VaR metrics
        """
        if not returns:
            return {"error": "No returns data provided"}
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        var_pct = abs(sorted_returns[index])
        var_amount = portfolio_value * var_pct
        
        # Expected Shortfall (CVaR)
        cvar_returns = sorted_returns[:index + 1]
        cvar_pct = abs(sum(cvar_returns) / len(cvar_returns)) if cvar_returns else 0
        cvar_amount = portfolio_value * cvar_pct
        
        return {
            "var_pct": round(var_pct * 100, 2),
            "var_amount": round(var_amount, 2),
            "cvar_pct": round(cvar_pct * 100, 2),
            "cvar_amount": round(cvar_amount, 2),
            "confidence_level": confidence_level * 100,
            "observation_count": len(returns)
        }
    
    @staticmethod
    def parametric_var(
        mean_return: float,
        std_return: float,
        confidence_level: float = 0.95,
        portfolio_value: float = 100000,
        holding_period_days: int = 1
    ) -> Dict[str, float]:
        """
        Parametric (Variance-Covariance) VaR
        
        Args:
            mean_return: Mean daily return
            std_return: Standard deviation of daily returns
            confidence_level: Confidence level
            portfolio_value: Portfolio value
            holding_period_days: Holding period
        
        Returns:
            VaR metrics
        """
        # Z-scores for common confidence levels
        z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
        z_score = z_scores.get(confidence_level, 1.645)
        
        # Adjust for holding period
        adjusted_std = std_return * math.sqrt(holding_period_days)
        adjusted_mean = mean_return * holding_period_days
        
        var_pct = z_score * adjusted_std - adjusted_mean
        var_amount = portfolio_value * var_pct
        
        return {
            "var_pct": round(var_pct * 100, 2),
            "var_amount": round(var_amount, 2),
            "confidence_level": confidence_level * 100,
            "holding_period_days": holding_period_days,
            "z_score": z_score
        }
    
    @staticmethod
    def monte_carlo_var(
        mean_return: float,
        std_return: float,
        simulations: int = 10000,
        confidence_level: float = 0.95,
        portfolio_value: float = 100000,
        holding_period_days: int = 1
    ) -> Dict[str, float]:
        """
        Monte Carlo VaR simulation
        
        Args:
            mean_return: Mean daily return
            std_return: Standard deviation
            simulations: Number of simulations
            confidence_level: Confidence level
            portfolio_value: Portfolio value
            holding_period_days: Holding period
        
        Returns:
            VaR metrics from simulation
        """
        import random
        
        # Simulate returns
        simulated_returns = []
        for _ in range(simulations):
            period_return = 0
            for _ in range(holding_period_days):
                # Simple normal distribution simulation
                u1, u2 = random.random(), random.random()
                z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
                daily_return = mean_return + std_return * z
                period_return = (1 + period_return) * (1 + daily_return) - 1
            simulated_returns.append(period_return)
        
        # Calculate VaR from simulated distribution
        sorted_returns = sorted(simulated_returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        var_pct = abs(sorted_returns[index])
        var_amount = portfolio_value * var_pct
        
        # CVaR
        cvar_returns = sorted_returns[:index + 1]
        cvar_pct = abs(sum(cvar_returns) / len(cvar_returns))
        
        return {
            "var_pct": round(var_pct * 100, 2),
            "var_amount": round(var_amount, 2),
            "cvar_pct": round(cvar_pct * 100, 2),
            "cvar_amount": round(portfolio_value * cvar_pct, 2),
            "confidence_level": confidence_level * 100,
            "simulations": simulations,
            "holding_period_days": holding_period_days
        }


class DrawdownAnalyzer:
    """Drawdown analysis and tracking"""
    
    @staticmethod
    def calculate_drawdowns(portfolio_values: List[float]) -> Dict:
        """
        Calculate drawdown statistics
        
        Args:
            portfolio_values: Historical portfolio values
        
        Returns:
            Drawdown metrics
        """
        if not portfolio_values:
            return {"error": "No data provided"}
        
        peak = portfolio_values[0]
        max_drawdown = 0
        max_drawdown_start = 0
        max_drawdown_end = 0
        current_drawdown_start = 0
        drawdowns = []
        
        for i, value in enumerate(portfolio_values):
            if value > peak:
                # New peak, record any drawdown that was in progress
                if peak > portfolio_values[current_drawdown_start]:
                    drawdowns.append({
                        "start_idx": current_drawdown_start,
                        "end_idx": i - 1,
                        "drawdown_pct": (peak - min(portfolio_values[current_drawdown_start:i])) / peak * 100
                    })
                peak = value
                current_drawdown_start = i
            else:
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_start = current_drawdown_start
                    max_drawdown_end = i
        
        # Calculate average drawdown
        avg_drawdown = sum(d["drawdown_pct"] for d in drawdowns) / len(drawdowns) if drawdowns else 0
        
        # Calculate recovery time for max drawdown
        recovery_idx = None
        for i in range(max_drawdown_end, len(portfolio_values)):
            if portfolio_values[i] >= portfolio_values[max_drawdown_start]:
                recovery_idx = i
                break
        
        return {
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "max_drawdown_start_idx": max_drawdown_start,
            "max_drawdown_end_idx": max_drawdown_end,
            "max_drawdown_recovery_idx": recovery_idx,
            "recovery_periods": recovery_idx - max_drawdown_end if recovery_idx else None,
            "avg_drawdown_pct": round(avg_drawdown, 2),
            "total_drawdowns": len(drawdowns),
            "current_drawdown_pct": round((peak - portfolio_values[-1]) / peak * 100, 2) if peak > portfolio_values[-1] else 0
        }
    
    @staticmethod
    def calmar_ratio(
        annual_return: float,
        max_drawdown: float
    ) -> float:
        """
        Calculate Calmar Ratio
        
        Args:
            annual_return: Annualized return
            max_drawdown: Maximum drawdown (as decimal)
        
        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return 0
        return round(annual_return / max_drawdown, 2)
    
    @staticmethod
    def ulcer_index(portfolio_values: List[float]) -> float:
        """
        Calculate Ulcer Index (measures downside risk)
        
        Args:
            portfolio_values: Historical values
        
        Returns:
            Ulcer Index
        """
        if not portfolio_values:
            return 0
        
        peak = portfolio_values[0]
        squared_drawdowns = []
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = ((peak - value) / peak) * 100
            squared_drawdowns.append(drawdown ** 2)
        
        avg_squared = sum(squared_drawdowns) / len(squared_drawdowns)
        return round(math.sqrt(avg_squared), 2)


class RiskAdjustedMetrics:
    """Risk-adjusted performance metrics"""
    
    @staticmethod
    def sharpe_ratio(
        returns: List[float],
        risk_free_rate: float = 0.05
    ) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) < 2:
            return 0
        
        daily_rf = risk_free_rate / 252
        excess_returns = [r - daily_rf for r in returns]
        
        mean_excess = sum(excess_returns) / len(excess_returns)
        variance = sum((r - mean_excess) ** 2 for r in excess_returns) / len(excess_returns)
        std_excess = math.sqrt(variance)
        
        if std_excess == 0:
            return 0
        
        daily_sharpe = mean_excess / std_excess
        annual_sharpe = daily_sharpe * math.sqrt(252)
        
        return round(annual_sharpe, 2)
    
    @staticmethod
    def sortino_ratio(
        returns: List[float],
        risk_free_rate: float = 0.05,
        target_return: float = 0
    ) -> float:
        """
        Calculate Sortino Ratio (downside risk only)
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
            target_return: Target return (default 0)
        
        Returns:
            Annualized Sortino ratio
        """
        if len(returns) < 2:
            return 0
        
        daily_rf = risk_free_rate / 252
        excess_returns = [r - daily_rf for r in returns]
        mean_excess = sum(excess_returns) / len(excess_returns)
        
        # Calculate downside deviation
        downside_returns = [min(0, r - target_return) for r in returns]
        downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
        downside_std = math.sqrt(downside_variance)
        
        if downside_std == 0:
            return 0
        
        daily_sortino = mean_excess / downside_std
        annual_sortino = daily_sortino * math.sqrt(252)
        
        return round(annual_sortino, 2)
    
    @staticmethod
    def treynor_ratio(
        returns: List[float],
        benchmark_returns: List[float],
        risk_free_rate: float = 0.05
    ) -> float:
        """
        Calculate Treynor Ratio
        
        Args:
            returns: Portfolio daily returns
            benchmark_returns: Benchmark daily returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Treynor ratio
        """
        if len(returns) != len(benchmark_returns) or len(returns) < 2:
            return 0
        
        # Calculate beta
        n = len(returns)
        mean_r = sum(returns) / n
        mean_b = sum(benchmark_returns) / n
        
        covariance = sum((r - mean_r) * (b - mean_b) for r, b in zip(returns, benchmark_returns)) / n
        benchmark_variance = sum((b - mean_b) ** 2 for b in benchmark_returns) / n
        
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        if beta == 0:
            return 0
        
        # Annualize returns
        annual_return = (1 + mean_r) ** 252 - 1
        
        treynor = (annual_return - risk_free_rate) / beta
        
        return round(treynor, 4)
    
    @staticmethod
    def information_ratio(
        returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """
        Calculate Information Ratio
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
        
        Returns:
            Information ratio
        """
        if len(returns) != len(benchmark_returns) or len(returns) < 2:
            return 0
        
        excess_returns = [r - b for r, b in zip(returns, benchmark_returns)]
        mean_excess = sum(excess_returns) / len(excess_returns)
        
        variance = sum((r - mean_excess) ** 2 for r in excess_returns) / len(excess_returns)
        tracking_error = math.sqrt(variance)
        
        if tracking_error == 0:
            return 0
        
        daily_ir = mean_excess / tracking_error
        annual_ir = daily_ir * math.sqrt(252)
        
        return round(annual_ir, 2)


def generate_risk_report(
    portfolio_value: float,
    returns: List[float],
    portfolio_values: List[float],
    risk_profile: RiskProfile,
    benchmark_returns: Optional[List[float]] = None
) -> Dict:
    """
    Generate comprehensive risk report
    
    Args:
        portfolio_value: Current portfolio value
        returns: Historical daily returns
        portfolio_values: Historical portfolio values
        risk_profile: User's risk profile
        benchmark_returns: Optional benchmark returns
    
    Returns:
        Comprehensive risk report
    """
    if benchmark_returns is None:
        benchmark_returns = [0] * len(returns)
    
    # Calculate mean and std
    if returns:
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_return = math.sqrt(variance)
    else:
        mean_return = std_return = 0
    
    # VaR calculations
    var_hist = VaRCalculator.historical_var(returns, portfolio_value=portfolio_value)
    var_param = VaRCalculator.parametric_var(mean_return, std_return, portfolio_value=portfolio_value)
    
    # Drawdown analysis
    drawdown = DrawdownAnalyzer.calculate_drawdowns(portfolio_values)
    ulcer = DrawdownAnalyzer.ulcer_index(portfolio_values)
    
    # Risk-adjusted metrics
    sharpe = RiskAdjustedMetrics.sharpe_ratio(returns)
    sortino = RiskAdjustedMetrics.sortino_ratio(returns)
    treynor = RiskAdjustedMetrics.treynor_ratio(returns, benchmark_returns)
    info_ratio = RiskAdjustedMetrics.information_ratio(returns, benchmark_returns)
    
    # Calmar ratio
    if portfolio_values:
        annual_return = mean_return * 252
        calmar = DrawdownAnalyzer.calmar_ratio(
            annual_return,
            drawdown.get("max_drawdown_pct", 0) / 100
        )
    else:
        calmar = 0
    
    # Risk assessment
    risk_score = 0
    risk_warnings = []
    
    if drawdown.get("max_drawdown_pct", 0) > risk_profile.max_drawdown_pct:
        risk_warnings.append(f"Max drawdown ({drawdown['max_drawdown_pct']}%) exceeds limit ({risk_profile.max_drawdown_pct}%)")
        risk_score += 20
    
    if var_hist.get("var_pct", 0) > 5:
        risk_warnings.append(f"Daily VaR ({var_hist['var_pct']}%) is high")
        risk_score += 15
    
    if std_return * math.sqrt(252) * 100 > 30:
        risk_warnings.append("Portfolio volatility exceeds 30% annualized")
        risk_score += 15
    
    if sharpe < 1:
        risk_warnings.append(f"Sharpe ratio ({sharpe}) is below 1")
        risk_score += 10
    
    return {
        "portfolio_value": round(portfolio_value, 2),
        "risk_profile": risk_profile.to_dict(),
        "value_at_risk": {
            "historical": var_hist,
            "parametric": var_param
        },
        "drawdown_analysis": drawdown,
        "ulcer_index": ulcer,
        "risk_adjusted_metrics": {
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "treynor_ratio": treynor,
            "information_ratio": info_ratio,
            "calmar_ratio": calmar
        },
        "volatility": {
            "daily": round(std_return * 100, 2),
            "annual": round(std_return * math.sqrt(252) * 100, 2)
        },
        "risk_assessment": {
            "risk_score": min(risk_score, 100),
            "risk_level": "high" if risk_score > 50 else "moderate" if risk_score > 25 else "low",
            "warnings": risk_warnings
        }
    }
