"""
Alerts and Notifications Module

Provides alerting and monitoring capabilities:
- Price alerts
- Technical indicator alerts
- Portfolio alerts
- Risk alerts
- News/event alerts
- Notification delivery
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json


class AlertType(Enum):
    """Types of alerts"""
    PRICE = "price"
    TECHNICAL = "technical"
    PORTFOLIO = "portfolio"
    RISK = "risk"
    NEWS = "news"
    EARNINGS = "earnings"
    DIVIDEND = "dividend"
    CUSTOM = "custom"


class AlertCondition(Enum):
    """Alert trigger conditions"""
    ABOVE = "above"
    BELOW = "below"
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    EQUALS = "equals"
    PERCENT_CHANGE = "percent_change"
    BETWEEN = "between"
    OUTSIDE = "outside"


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    alert_type: AlertType
    symbol: Optional[str] = None
    condition: AlertCondition = AlertCondition.ABOVE
    threshold: float = 0.0
    threshold_upper: Optional[float] = None  # For BETWEEN/OUTSIDE
    current_value: float = 0.0
    previous_value: float = 0.0
    priority: AlertPriority = AlertPriority.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    repeat: bool = False
    repeat_interval_minutes: int = 60
    last_triggered: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def check_condition(self, value: float) -> bool:
        """Check if alert condition is met"""
        self.previous_value = self.current_value
        self.current_value = value
        
        # Check cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        
        # Check expiration
        if self.expires_at and datetime.now() > self.expires_at:
            self.status = AlertStatus.EXPIRED
            return False
        
        if self.condition == AlertCondition.ABOVE:
            return value > self.threshold
        elif self.condition == AlertCondition.BELOW:
            return value < self.threshold
        elif self.condition == AlertCondition.CROSSES_ABOVE:
            return self.previous_value <= self.threshold < value
        elif self.condition == AlertCondition.CROSSES_BELOW:
            return self.previous_value >= self.threshold > value
        elif self.condition == AlertCondition.EQUALS:
            return abs(value - self.threshold) < 0.0001
        elif self.condition == AlertCondition.PERCENT_CHANGE:
            if self.previous_value == 0:
                return False
            pct_change = abs((value - self.previous_value) / self.previous_value * 100)
            return pct_change >= self.threshold
        elif self.condition == AlertCondition.BETWEEN:
            if self.threshold_upper is None:
                return False
            return self.threshold <= value <= self.threshold_upper
        elif self.condition == AlertCondition.OUTSIDE:
            if self.threshold_upper is None:
                return False
            return value < self.threshold or value > self.threshold_upper
        
        return False
    
    def trigger(self):
        """Trigger the alert"""
        self.triggered_at = datetime.now()
        self.last_triggered = datetime.now()
        
        if self.repeat:
            self.cooldown_until = datetime.now() + timedelta(minutes=self.repeat_interval_minutes)
        else:
            self.status = AlertStatus.TRIGGERED
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.alert_type.value,
            "symbol": self.symbol,
            "condition": self.condition.value,
            "threshold": self.threshold,
            "threshold_upper": self.threshold_upper,
            "current_value": self.current_value,
            "priority": self.priority.value,
            "status": self.status.value,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "repeat": self.repeat
        }


@dataclass
class Notification:
    """Notification to be delivered"""
    id: str
    alert_id: str
    title: str
    message: str
    priority: AlertPriority
    timestamp: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    delivery_channel: str = "console"
    data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "delivered": self.delivered,
            "channel": self.delivery_channel
        }


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.notifications: List[Notification] = []
        self.next_alert_id = 1
        self.next_notification_id = 1
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Register default console handler
        self.register_handler("console", self._console_handler)
    
    def register_handler(self, channel: str, handler: Callable):
        """Register a notification delivery handler"""
        self.notification_handlers[channel] = handler
    
    def _console_handler(self, notification: Notification):
        """Default console notification handler"""
        priority_icons = {
            AlertPriority.LOW: "ℹ️",
            AlertPriority.MEDIUM: "⚠️",
            AlertPriority.HIGH: "🔔",
            AlertPriority.CRITICAL: "🚨"
        }
        
        icon = priority_icons.get(notification.priority, "📢")
        print(f"\n{icon} ALERT: {notification.title}")
        print(f"   {notification.message}")
        print(f"   Time: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def create_price_alert(
        self,
        symbol: str,
        condition: AlertCondition,
        threshold: float,
        name: Optional[str] = None,
        priority: AlertPriority = AlertPriority.MEDIUM,
        expires_in_hours: Optional[int] = None,
        repeat: bool = False
    ) -> Alert:
        """Create a price alert"""
        alert_id = f"PRC{self.next_alert_id:06d}"
        self.next_alert_id += 1
        
        alert = Alert(
            id=alert_id,
            name=name or f"{symbol} Price Alert",
            alert_type=AlertType.PRICE,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            priority=priority,
            repeat=repeat,
            expires_at=datetime.now() + timedelta(hours=expires_in_hours) if expires_in_hours else None,
            message=f"{symbol} price {condition.value} ${threshold}"
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def create_technical_alert(
        self,
        symbol: str,
        indicator: str,
        condition: AlertCondition,
        threshold: float,
        name: Optional[str] = None,
        priority: AlertPriority = AlertPriority.MEDIUM
    ) -> Alert:
        """Create a technical indicator alert"""
        alert_id = f"TEC{self.next_alert_id:06d}"
        self.next_alert_id += 1
        
        alert = Alert(
            id=alert_id,
            name=name or f"{symbol} {indicator} Alert",
            alert_type=AlertType.TECHNICAL,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            priority=priority,
            message=f"{symbol} {indicator} {condition.value} {threshold}",
            metadata={"indicator": indicator}
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def create_portfolio_alert(
        self,
        condition: AlertCondition,
        threshold: float,
        metric: str = "total_value",
        name: Optional[str] = None,
        priority: AlertPriority = AlertPriority.HIGH
    ) -> Alert:
        """Create a portfolio alert"""
        alert_id = f"PRT{self.next_alert_id:06d}"
        self.next_alert_id += 1
        
        alert = Alert(
            id=alert_id,
            name=name or f"Portfolio {metric} Alert",
            alert_type=AlertType.PORTFOLIO,
            condition=condition,
            threshold=threshold,
            priority=priority,
            message=f"Portfolio {metric} {condition.value} {threshold}",
            metadata={"metric": metric}
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def create_risk_alert(
        self,
        risk_metric: str,
        condition: AlertCondition,
        threshold: float,
        name: Optional[str] = None,
        priority: AlertPriority = AlertPriority.HIGH
    ) -> Alert:
        """Create a risk alert"""
        alert_id = f"RSK{self.next_alert_id:06d}"
        self.next_alert_id += 1
        
        alert = Alert(
            id=alert_id,
            name=name or f"Risk Alert: {risk_metric}",
            alert_type=AlertType.RISK,
            condition=condition,
            threshold=threshold,
            priority=priority,
            message=f"{risk_metric} {condition.value} {threshold}",
            metadata={"risk_metric": risk_metric}
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def check_alert(self, alert_id: str, value: float) -> Optional[Notification]:
        """Check an alert against a value"""
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        
        if alert.status not in [AlertStatus.ACTIVE]:
            return None
        
        if alert.check_condition(value):
            alert.trigger()
            notification = self._create_notification(alert, value)
            self._deliver_notification(notification)
            return notification
        
        return None
    
    def check_all_price_alerts(self, prices: Dict[str, float]) -> List[Notification]:
        """Check all price alerts against current prices"""
        notifications = []
        
        for alert in self.alerts.values():
            if alert.alert_type == AlertType.PRICE and alert.status == AlertStatus.ACTIVE:
                if alert.symbol in prices:
                    notification = self.check_alert(alert.id, prices[alert.symbol])
                    if notification:
                        notifications.append(notification)
        
        return notifications
    
    def _create_notification(self, alert: Alert, value: float) -> Notification:
        """Create a notification from an alert"""
        notification_id = f"NTF{self.next_notification_id:06d}"
        self.next_notification_id += 1
        
        # Build detailed message
        if alert.alert_type == AlertType.PRICE:
            message = f"{alert.symbol} price is now ${value:.2f} ({alert.condition.value} ${alert.threshold})"
        elif alert.alert_type == AlertType.TECHNICAL:
            indicator = alert.metadata.get("indicator", "indicator")
            message = f"{alert.symbol} {indicator} is now {value:.2f} ({alert.condition.value} {alert.threshold})"
        elif alert.alert_type == AlertType.PORTFOLIO:
            metric = alert.metadata.get("metric", "value")
            message = f"Portfolio {metric} is now {value:.2f} ({alert.condition.value} {alert.threshold})"
        elif alert.alert_type == AlertType.RISK:
            metric = alert.metadata.get("risk_metric", "metric")
            message = f"{metric} is now {value:.2f} ({alert.condition.value} {alert.threshold})"
        else:
            message = alert.message
        
        notification = Notification(
            id=notification_id,
            alert_id=alert.id,
            title=alert.name,
            message=message,
            priority=alert.priority,
            data={"value": value, "threshold": alert.threshold}
        )
        
        self.notifications.append(notification)
        return notification
    
    def _deliver_notification(self, notification: Notification):
        """Deliver a notification"""
        handler = self.notification_handlers.get(notification.delivery_channel)
        if handler:
            handler(notification)
            notification.delivered = True
    
    def cancel_alert(self, alert_id: str):
        """Cancel an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.CANCELLED
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
    
    def get_triggered_alerts(self) -> List[Alert]:
        """Get all triggered alerts"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.TRIGGERED]
    
    def get_notifications(
        self,
        limit: int = 50,
        undelivered_only: bool = False
    ) -> List[Notification]:
        """Get recent notifications"""
        notifications = self.notifications
        
        if undelivered_only:
            notifications = [n for n in notifications if not n.delivered]
        
        return sorted(notifications, key=lambda n: n.timestamp, reverse=True)[:limit]
    
    def clear_old_notifications(self, days: int = 7):
        """Clear notifications older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.notifications = [n for n in self.notifications if n.timestamp > cutoff]
    
    def to_dict(self) -> Dict:
        """Export alert manager state"""
        return {
            "alerts": {aid: a.to_dict() for aid, a in self.alerts.items()},
            "recent_notifications": [n.to_dict() for n in self.get_notifications(20)]
        }
    
    def save_to_file(self, filepath: str):
        """Save alerts to file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load alerts from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore alerts (simplified - full implementation would recreate objects)
            for alert_id, alert_data in data.get("alerts", {}).items():
                self.alerts[alert_id] = Alert(
                    id=alert_data["id"],
                    name=alert_data["name"],
                    alert_type=AlertType(alert_data["type"]),
                    symbol=alert_data.get("symbol"),
                    condition=AlertCondition(alert_data["condition"]),
                    threshold=alert_data["threshold"],
                    priority=AlertPriority(alert_data["priority"]),
                    status=AlertStatus(alert_data["status"]),
                    message=alert_data.get("message", "")
                )
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading alerts: {e}")


class WatchlistManager:
    """Manage stock watchlists"""
    
    def __init__(self):
        self.watchlists: Dict[str, List[str]] = {"default": []}
    
    def create_watchlist(self, name: str) -> List[str]:
        """Create a new watchlist"""
        if name not in self.watchlists:
            self.watchlists[name] = []
        return self.watchlists[name]
    
    def add_symbol(self, symbol: str, watchlist: str = "default"):
        """Add symbol to watchlist"""
        if watchlist not in self.watchlists:
            self.create_watchlist(watchlist)
        
        if symbol.upper() not in self.watchlists[watchlist]:
            self.watchlists[watchlist].append(symbol.upper())
    
    def remove_symbol(self, symbol: str, watchlist: str = "default"):
        """Remove symbol from watchlist"""
        if watchlist in self.watchlists:
            self.watchlists[watchlist] = [
                s for s in self.watchlists[watchlist] if s != symbol.upper()
            ]
    
    def get_watchlist(self, name: str = "default") -> List[str]:
        """Get watchlist symbols"""
        return self.watchlists.get(name, [])
    
    def delete_watchlist(self, name: str):
        """Delete a watchlist"""
        if name in self.watchlists and name != "default":
            del self.watchlists[name]
    
    def to_dict(self) -> Dict:
        return {"watchlists": self.watchlists}


class PortfolioMonitor:
    """Monitor portfolio for alerts"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.thresholds = {
            "daily_loss_pct": 3.0,
            "position_loss_pct": 10.0,
            "max_drawdown_pct": 15.0,
            "volatility_spike_pct": 50.0
        }
    
    def setup_default_alerts(self, portfolio_value: float):
        """Setup default portfolio monitoring alerts"""
        # Daily loss alert
        self.alert_manager.create_portfolio_alert(
            condition=AlertCondition.BELOW,
            threshold=portfolio_value * 0.97,  # 3% loss
            metric="daily_value",
            name="Daily Loss Alert",
            priority=AlertPriority.HIGH
        )
        
        # Significant drawdown alert
        self.alert_manager.create_risk_alert(
            risk_metric="max_drawdown",
            condition=AlertCondition.ABOVE,
            threshold=self.thresholds["max_drawdown_pct"],
            name="Drawdown Alert",
            priority=AlertPriority.CRITICAL
        )
        
        # Volatility spike alert
        self.alert_manager.create_risk_alert(
            risk_metric="volatility_change",
            condition=AlertCondition.ABOVE,
            threshold=self.thresholds["volatility_spike_pct"],
            name="Volatility Spike Alert",
            priority=AlertPriority.HIGH
        )
    
    def check_portfolio(
        self,
        current_value: float,
        previous_value: float,
        positions: List[Dict],
        drawdown_pct: float,
        volatility_pct: float,
        prev_volatility_pct: float
    ) -> List[Notification]:
        """Check portfolio for alert conditions"""
        notifications = []
        
        # Check daily P&L
        daily_change_pct = ((current_value - previous_value) / previous_value) * 100
        
        for alert in self.alert_manager.get_active_alerts():
            if alert.alert_type == AlertType.PORTFOLIO:
                metric = alert.metadata.get("metric")
                
                if metric == "daily_value":
                    notification = self.alert_manager.check_alert(alert.id, current_value)
                    if notification:
                        notifications.append(notification)
                
                elif metric == "daily_change_pct":
                    notification = self.alert_manager.check_alert(alert.id, daily_change_pct)
                    if notification:
                        notifications.append(notification)
            
            elif alert.alert_type == AlertType.RISK:
                risk_metric = alert.metadata.get("risk_metric")
                
                if risk_metric == "max_drawdown":
                    notification = self.alert_manager.check_alert(alert.id, drawdown_pct)
                    if notification:
                        notifications.append(notification)
                
                elif risk_metric == "volatility_change":
                    if prev_volatility_pct > 0:
                        vol_change = ((volatility_pct - prev_volatility_pct) / prev_volatility_pct) * 100
                        notification = self.alert_manager.check_alert(alert.id, vol_change)
                        if notification:
                            notifications.append(notification)
        
        # Check individual positions
        for position in positions:
            if position.get("unrealized_pnl_pct", 0) <= -self.thresholds["position_loss_pct"]:
                # Create ad-hoc notification for position loss
                notification_id = f"NTF{self.alert_manager.next_notification_id:06d}"
                self.alert_manager.next_notification_id += 1
                
                notification = Notification(
                    id=notification_id,
                    alert_id="POSITION_LOSS",
                    title=f"Position Loss Alert: {position['symbol']}",
                    message=f"{position['symbol']} is down {abs(position['unrealized_pnl_pct']):.1f}%",
                    priority=AlertPriority.HIGH,
                    data=position
                )
                
                self.alert_manager.notifications.append(notification)
                self.alert_manager._deliver_notification(notification)
                notifications.append(notification)
        
        return notifications
