"""
Portfolio Analysis Module

Provides comprehensive portfolio analysis including:
- Position management
- Performance metrics
- Asset allocation
- Diversification analysis
- Rebalancing recommendations
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class AssetClass(Enum):
    """Asset class categories"""
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    CASH = "cash"
    OTHER = "other"


class Sector(Enum):
    """Market sectors"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    CONSUMER_DISCRETIONARY = "consumer_discretionary"
    CONSUMER_STAPLES = "consumer_staples"
    ENERGY = "energy"
    UTILITIES = "utilities"
    INDUSTRIALS = "industrials"
    MATERIALS = "materials"
    REAL_ESTATE = "real_estate"
    COMMUNICATION = "communication"
    OTHER = "other"


@dataclass
class Position:
    """Represents a single portfolio position"""
    symbol: str
    shares: float
    purchase_price: float
    current_price: float
    purchase_date: Optional[datetime] = None
    asset_class: AssetClass = AssetClass.EQUITY
    sector: Optional[Sector] = None
    name: Optional[str] = None
    
    @property
    def market_value(self) -> float:
        """Calculate current market value"""
        return self.shares * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """Calculate total cost basis"""
        return self.shares * self.purchase_price
    
    @property
    def unrealized_gain(self) -> float:
        """Calculate unrealized gain/loss"""
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_gain_percent(self) -> float:
        """Calculate unrealized gain/loss percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_gain / self.cost_basis) * 100
    
    @property
    def holding_period_days(self) -> Optional[int]:
        """Calculate holding period in days"""
        if self.purchase_date:
            return (datetime.now() - self.purchase_date).days
        return None
    
    def to_dict(self) -> Dict:
        """Convert position to dictionary"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "shares": self.shares,
            "purchase_price": self.purchase_price,
            "current_price": self.current_price,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "asset_class": self.asset_class.value,
            "sector": self.sector.value if self.sector else None,
            "market_value": self.market_value,
            "cost_basis": self.cost_basis,
            "unrealized_gain": self.unrealized_gain,
            "unrealized_gain_percent": self.unrealized_gain_percent
        }


@dataclass
class Portfolio:
    """Portfolio management and analysis"""
    name: str
    positions: List[Position] = field(default_factory=list)
    cash_balance: float = 0.0
    benchmark_symbol: str = "SPY"
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_position(self, position: Position) -> None:
        """Add a new position to the portfolio"""
        # Check if position already exists
        existing = self.get_position(position.symbol)
        if existing:
            # Average into existing position
            total_shares = existing.shares + position.shares
            avg_price = (existing.cost_basis + position.cost_basis) / total_shares
            existing.shares = total_shares
            existing.purchase_price = avg_price
            existing.current_price = position.current_price
        else:
            self.positions.append(position)
    
    def remove_position(self, symbol: str) -> Optional[Position]:
        """Remove a position from the portfolio"""
        position = self.get_position(symbol)
        if position:
            self.positions.remove(position)
            return position
        return None
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol"""
        for position in self.positions:
            if position.symbol.upper() == symbol.upper():
                return position
        return None
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """Update current prices for all positions"""
        for position in self.positions:
            if position.symbol in prices:
                position.current_price = prices[position.symbol]
    
    @property
    def total_market_value(self) -> float:
        """Calculate total portfolio market value"""
        return sum(p.market_value for p in self.positions) + self.cash_balance
    
    @property
    def total_cost_basis(self) -> float:
        """Calculate total cost basis"""
        return sum(p.cost_basis for p in self.positions)
    
    @property
    def total_unrealized_gain(self) -> float:
        """Calculate total unrealized gain/loss"""
        return sum(p.unrealized_gain for p in self.positions)
    
    @property
    def total_unrealized_gain_percent(self) -> float:
        """Calculate total unrealized gain/loss percentage"""
        if self.total_cost_basis == 0:
            return 0.0
        return (self.total_unrealized_gain / self.total_cost_basis) * 100
    
    def get_allocation_by_asset_class(self) -> Dict[str, float]:
        """Calculate allocation by asset class"""
        allocation = {}
        total = self.total_market_value
        
        if total == 0:
            return allocation
        
        for position in self.positions:
            asset_class = position.asset_class.value
            if asset_class not in allocation:
                allocation[asset_class] = 0.0
            allocation[asset_class] += position.market_value
        
        # Add cash
        if self.cash_balance > 0:
            allocation["cash"] = self.cash_balance
        
        # Convert to percentages
        return {k: (v / total) * 100 for k, v in allocation.items()}
    
    def get_allocation_by_sector(self) -> Dict[str, float]:
        """Calculate allocation by sector"""
        allocation = {}
        total = self.total_market_value
        
        if total == 0:
            return allocation
        
        for position in self.positions:
            sector = position.sector.value if position.sector else "other"
            if sector not in allocation:
                allocation[sector] = 0.0
            allocation[sector] += position.market_value
        
        return {k: (v / total) * 100 for k, v in allocation.items()}
    
    def get_position_weights(self) -> Dict[str, float]:
        """Calculate weight of each position"""
        total = self.total_market_value
        if total == 0:
            return {}
        
        weights = {}
        for position in self.positions:
            weights[position.symbol] = (position.market_value / total) * 100
        
        if self.cash_balance > 0:
            weights["CASH"] = (self.cash_balance / total) * 100
        
        return weights
    
    def calculate_concentration_risk(self) -> Dict[str, any]:
        """Calculate portfolio concentration risk metrics"""
        weights = self.get_position_weights()
        
        if not weights:
            return {"hhi": 0, "max_position": 0, "top_5_concentration": 0}
        
        # Herfindahl-Hirschman Index (HHI)
        hhi = sum((w ** 2) for w in weights.values())
        
        # Maximum single position weight
        max_weight = max(weights.values()) if weights else 0
        
        # Top 5 concentration
        sorted_weights = sorted(weights.values(), reverse=True)
        top_5 = sum(sorted_weights[:5])
        
        return {
            "hhi": round(hhi, 2),
            "hhi_interpretation": self._interpret_hhi(hhi),
            "max_position_weight": round(max_weight, 2),
            "top_5_concentration": round(top_5, 2),
            "number_of_positions": len(self.positions)
        }
    
    def _interpret_hhi(self, hhi: float) -> str:
        """Interpret HHI score"""
        if hhi < 1500:
            return "Low concentration - well diversified"
        elif hhi < 2500:
            return "Moderate concentration"
        else:
            return "High concentration - consider diversifying"
    
    def get_rebalancing_recommendations(
        self,
        target_allocation: Dict[str, float],
        threshold: float = 5.0
    ) -> List[Dict]:
        """
        Generate rebalancing recommendations
        
        Args:
            target_allocation: Target allocation by asset class (percentages)
            threshold: Rebalancing threshold percentage
        
        Returns:
            List of rebalancing recommendations
        """
        current = self.get_allocation_by_asset_class()
        recommendations = []
        total_value = self.total_market_value
        
        for asset_class, target_pct in target_allocation.items():
            current_pct = current.get(asset_class, 0)
            diff = target_pct - current_pct
            
            if abs(diff) >= threshold:
                target_value = (target_pct / 100) * total_value
                current_value = (current_pct / 100) * total_value
                change_amount = target_value - current_value
                
                recommendations.append({
                    "asset_class": asset_class,
                    "current_allocation": round(current_pct, 2),
                    "target_allocation": target_pct,
                    "difference": round(diff, 2),
                    "action": "buy" if diff > 0 else "sell",
                    "amount": round(abs(change_amount), 2)
                })
        
        return recommendations
    
    def calculate_portfolio_metrics(
        self,
        returns: Optional[List[float]] = None,
        risk_free_rate: float = 0.05
    ) -> Dict[str, float]:
        """
        Calculate key portfolio metrics
        
        Args:
            returns: Historical daily returns (if available)
            risk_free_rate: Annual risk-free rate (default 5%)
        
        Returns:
            Dictionary of portfolio metrics
        """
        metrics = {
            "total_value": round(self.total_market_value, 2),
            "total_cost": round(self.total_cost_basis, 2),
            "total_gain": round(self.total_unrealized_gain, 2),
            "total_return_pct": round(self.total_unrealized_gain_percent, 2),
            "num_positions": len(self.positions),
            "cash_balance": round(self.cash_balance, 2)
        }
        
        if returns and len(returns) > 1:
            # Calculate volatility (annualized)
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            daily_volatility = math.sqrt(variance)
            annual_volatility = daily_volatility * math.sqrt(252)
            
            # Calculate Sharpe Ratio
            annual_return = mean_return * 252
            sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
            
            # Calculate Maximum Drawdown
            peak = returns[0]
            max_drawdown = 0
            for r in returns:
                if r > peak:
                    peak = r
                drawdown = (peak - r) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
            
            metrics.update({
                "annual_volatility": round(annual_volatility * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "daily_var_95": round(mean_return - 1.645 * daily_volatility, 4)
            })
        
        return metrics
    
    def get_top_performers(self, n: int = 5) -> List[Dict]:
        """Get top N performing positions"""
        sorted_positions = sorted(
            self.positions,
            key=lambda p: p.unrealized_gain_percent,
            reverse=True
        )
        return [p.to_dict() for p in sorted_positions[:n]]
    
    def get_bottom_performers(self, n: int = 5) -> List[Dict]:
        """Get bottom N performing positions"""
        sorted_positions = sorted(
            self.positions,
            key=lambda p: p.unrealized_gain_percent
        )
        return [p.to_dict() for p in sorted_positions[:n]]
    
    def get_dividend_summary(self, dividend_yields: Dict[str, float]) -> Dict:
        """
        Calculate dividend income summary
        
        Args:
            dividend_yields: Dictionary of symbol -> annual dividend yield
        
        Returns:
            Dividend summary
        """
        total_annual_dividends = 0
        dividend_positions = []
        
        for position in self.positions:
            yield_rate = dividend_yields.get(position.symbol, 0)
            annual_dividend = position.market_value * (yield_rate / 100)
            
            if yield_rate > 0:
                dividend_positions.append({
                    "symbol": position.symbol,
                    "yield": yield_rate,
                    "annual_income": round(annual_dividend, 2)
                })
                total_annual_dividends += annual_dividend
        
        portfolio_yield = (
            (total_annual_dividends / self.total_market_value) * 100
            if self.total_market_value > 0 else 0
        )
        
        return {
            "total_annual_dividends": round(total_annual_dividends, 2),
            "monthly_income": round(total_annual_dividends / 12, 2),
            "portfolio_yield": round(portfolio_yield, 2),
            "dividend_positions": dividend_positions
        }
    
    def to_dict(self) -> Dict:
        """Convert portfolio to dictionary"""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "cash_balance": self.cash_balance,
            "total_value": self.total_market_value,
            "positions": [p.to_dict() for p in self.positions],
            "metrics": self.calculate_portfolio_metrics(),
            "allocation": self.get_allocation_by_asset_class(),
            "concentration": self.calculate_concentration_risk()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export portfolio as JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_csv(cls, filepath: str, name: str = "My Portfolio") -> "Portfolio":
        """
        Load portfolio from CSV file
        
        Expected columns: Symbol, Shares, Purchase_Price, Current_Price
        Optional columns: Purchase_Date, Asset_Class, Sector, Name
        """
        portfolio = cls(name=name)
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return portfolio
        
        # Parse header
        header = [h.strip().lower() for h in lines[0].split(',')]
        
        for line in lines[1:]:
            if not line.strip():
                continue
            
            values = [v.strip() for v in line.split(',')]
            row = dict(zip(header, values))
            
            position = Position(
                symbol=row.get('symbol', '').upper(),
                shares=float(row.get('shares', 0)),
                purchase_price=float(row.get('purchase_price', 0)),
                current_price=float(row.get('current_price', 0)),
                name=row.get('name')
            )
            
            if 'asset_class' in row:
                try:
                    position.asset_class = AssetClass(row['asset_class'])
                except ValueError:
                    pass
            
            if 'sector' in row:
                try:
                    position.sector = Sector(row['sector'])
                except ValueError:
                    pass
            
            if 'purchase_date' in row and row['purchase_date']:
                try:
                    position.purchase_date = datetime.fromisoformat(row['purchase_date'])
                except ValueError:
                    pass
            
            portfolio.add_position(position)
        
        return portfolio


def analyze_portfolio_comparison(
    portfolio: Portfolio,
    benchmark_returns: List[float],
    portfolio_returns: List[float]
) -> Dict:
    """
    Compare portfolio performance against benchmark
    
    Args:
        portfolio: Portfolio to analyze
        benchmark_returns: Daily benchmark returns
        portfolio_returns: Daily portfolio returns
    
    Returns:
        Comparison metrics
    """
    if len(benchmark_returns) != len(portfolio_returns):
        raise ValueError("Returns series must be same length")
    
    n = len(benchmark_returns)
    
    # Calculate beta
    benchmark_mean = sum(benchmark_returns) / n
    portfolio_mean = sum(portfolio_returns) / n
    
    covariance = sum(
        (br - benchmark_mean) * (pr - portfolio_mean)
        for br, pr in zip(benchmark_returns, portfolio_returns)
    ) / n
    
    benchmark_variance = sum(
        (br - benchmark_mean) ** 2 for br in benchmark_returns
    ) / n
    
    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
    
    # Calculate alpha (annualized)
    risk_free_rate = 0.05 / 252  # Daily risk-free rate
    alpha = (portfolio_mean - risk_free_rate) - beta * (benchmark_mean - risk_free_rate)
    annual_alpha = alpha * 252
    
    # Calculate tracking error
    tracking_diff = [
        pr - br for pr, br in zip(portfolio_returns, benchmark_returns)
    ]
    tracking_error = math.sqrt(
        sum((td - (sum(tracking_diff) / n)) ** 2 for td in tracking_diff) / n
    ) * math.sqrt(252)
    
    # Information ratio
    info_ratio = (
        annual_alpha / tracking_error if tracking_error > 0 else 0
    )
    
    return {
        "beta": round(beta, 3),
        "alpha_annual": round(annual_alpha * 100, 2),
        "tracking_error": round(tracking_error * 100, 2),
        "information_ratio": round(info_ratio, 2),
        "correlation": round(
            covariance / (
                math.sqrt(benchmark_variance) *
                math.sqrt(sum((pr - portfolio_mean) ** 2 for pr in portfolio_returns) / n)
            ) if benchmark_variance > 0 else 0,
            3
        )
    }
