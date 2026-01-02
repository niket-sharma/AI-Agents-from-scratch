"""
Technical Analysis Module

Provides comprehensive technical indicators for trading analysis:
- Moving Averages (SMA, EMA, WMA)
- Momentum Indicators (RSI, MACD, Stochastic)
- Volatility Indicators (Bollinger Bands, ATR)
- Volume Indicators (OBV, VWAP)
- Trend Indicators (ADX, Parabolic SAR)
- Pattern Recognition
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class Signal(Enum):
    """Trading signal types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class OHLCV:
    """Price data point"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float


class TechnicalIndicators:
    """Technical analysis indicator calculations"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[Optional[float]]:
        """
        Simple Moving Average
        
        Args:
            prices: List of closing prices
            period: Number of periods
        
        Returns:
            List of SMA values (None for insufficient data)
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        result = [None] * (period - 1)
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            result.append(sum(window) / period)
        
        return result
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[Optional[float]]:
        """
        Exponential Moving Average
        
        Args:
            prices: List of closing prices
            period: Number of periods
        
        Returns:
            List of EMA values
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        multiplier = 2 / (period + 1)
        result = [None] * (period - 1)
        
        # First EMA is SMA
        first_ema = sum(prices[:period]) / period
        result.append(first_ema)
        
        for i in range(period, len(prices)):
            ema_value = (prices[i] - result[-1]) * multiplier + result[-1]
            result.append(ema_value)
        
        return result
    
    @staticmethod
    def wma(prices: List[float], period: int) -> List[Optional[float]]:
        """
        Weighted Moving Average
        
        Args:
            prices: List of closing prices
            period: Number of periods
        
        Returns:
            List of WMA values
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        result = [None] * (period - 1)
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            weighted_sum = sum(p * w for p, w in zip(window, weights))
            result.append(weighted_sum / weight_sum)
        
        return result
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
        """
        Relative Strength Index
        
        Args:
            prices: List of closing prices
            period: RSI period (default 14)
        
        Returns:
            List of RSI values (0-100)
        """
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(0, c) for c in changes]
        losses = [max(0, -c) for c in changes]
        
        result = [None] * period
        
        # First average
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - (100 / (1 + rs)))
        
        # Subsequent values using smoothed averages
        for i in range(period, len(changes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(100 - (100 / (1 + rs)))
        
        return result
    
    @staticmethod
    def macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """
        Moving Average Convergence Divergence
        
        Args:
            prices: List of closing prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = TechnicalIndicators.ema(prices, fast_period)
        slow_ema = TechnicalIndicators.ema(prices, slow_period)
        
        # Calculate MACD line
        macd_line = []
        for f, s in zip(fast_ema, slow_ema):
            if f is not None and s is not None:
                macd_line.append(f - s)
            else:
                macd_line.append(None)
        
        # Calculate signal line (EMA of MACD)
        valid_macd = [m for m in macd_line if m is not None]
        if len(valid_macd) < signal_period:
            signal_line = [None] * len(prices)
            histogram = [None] * len(prices)
        else:
            signal_ema = TechnicalIndicators.ema(valid_macd, signal_period)
            
            # Align signal line with original data
            signal_line = [None] * (len(prices) - len(valid_macd))
            signal_line.extend(signal_ema)
            
            # Calculate histogram
            histogram = []
            for m, s in zip(macd_line, signal_line):
                if m is not None and s is not None:
                    histogram.append(m - s)
                else:
                    histogram.append(None)
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def stochastic(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[List[Optional[float]], List[Optional[float]]]:
        """
        Stochastic Oscillator
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            k_period: %K period
            d_period: %D period (SMA of %K)
        
        Returns:
            Tuple of (%K, %D)
        """
        if len(closes) < k_period:
            return [None] * len(closes), [None] * len(closes)
        
        k_values = [None] * (k_period - 1)
        
        for i in range(k_period - 1, len(closes)):
            highest_high = max(highs[i - k_period + 1:i + 1])
            lowest_low = min(lows[i - k_period + 1:i + 1])
            
            if highest_high == lowest_low:
                k_values.append(50.0)
            else:
                k = ((closes[i] - lowest_low) / (highest_high - lowest_low)) * 100
                k_values.append(k)
        
        # %D is SMA of %K
        valid_k = [k for k in k_values if k is not None]
        d_sma = TechnicalIndicators.sma(valid_k, d_period)
        
        d_values = [None] * (len(k_values) - len(d_sma))
        d_values.extend(d_sma)
        
        return k_values, d_values
    
    @staticmethod
    def bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """
        Bollinger Bands
        
        Args:
            prices: List of closing prices
            period: Moving average period
            std_dev: Number of standard deviations
        
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle = TechnicalIndicators.sma(prices, period)
        
        upper = []
        lower = []
        
        for i, m in enumerate(middle):
            if m is None:
                upper.append(None)
                lower.append(None)
            else:
                window = prices[max(0, i - period + 1):i + 1]
                variance = sum((p - m) ** 2 for p in window) / len(window)
                std = math.sqrt(variance)
                
                upper.append(m + std_dev * std)
                lower.append(m - std_dev * std)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[Optional[float]]:
        """
        Average True Range
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ATR period
        
        Returns:
            List of ATR values
        """
        if len(closes) < 2:
            return [None] * len(closes)
        
        # Calculate True Range
        true_ranges = [highs[0] - lows[0]]
        
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1])
            )
            true_ranges.append(tr)
        
        # Calculate ATR (smoothed average of TR)
        if len(true_ranges) < period:
            return [None] * len(closes)
        
        atr_values = [None] * (period - 1)
        
        # First ATR is simple average
        first_atr = sum(true_ranges[:period]) / period
        atr_values.append(first_atr)
        
        # Subsequent ATRs use smoothing
        for i in range(period, len(true_ranges)):
            atr = (atr_values[-1] * (period - 1) + true_ranges[i]) / period
            atr_values.append(atr)
        
        return atr_values
    
    @staticmethod
    def obv(closes: List[float], volumes: List[float]) -> List[float]:
        """
        On-Balance Volume
        
        Args:
            closes: List of closing prices
            volumes: List of volumes
        
        Returns:
            List of OBV values
        """
        if len(closes) < 2:
            return [0] * len(closes)
        
        obv_values = [0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1]:
                obv_values.append(obv_values[-1] + volumes[i])
            elif closes[i] < closes[i - 1]:
                obv_values.append(obv_values[-1] - volumes[i])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values
    
    @staticmethod
    def vwap(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float]
    ) -> List[float]:
        """
        Volume Weighted Average Price
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            volumes: List of volumes
        
        Returns:
            List of VWAP values
        """
        vwap_values = []
        cumulative_tp_vol = 0
        cumulative_vol = 0
        
        for h, l, c, v in zip(highs, lows, closes, volumes):
            typical_price = (h + l + c) / 3
            cumulative_tp_vol += typical_price * v
            cumulative_vol += v
            
            vwap = cumulative_tp_vol / cumulative_vol if cumulative_vol > 0 else 0
            vwap_values.append(vwap)
        
        return vwap_values
    
    @staticmethod
    def adx(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """
        Average Directional Index
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ADX period
        
        Returns:
            Tuple of (ADX, +DI, -DI)
        """
        if len(closes) < period + 1:
            n = len(closes)
            return [None] * n, [None] * n, [None] * n
        
        # Calculate +DM and -DM
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(closes)):
            up_move = highs[i] - highs[i - 1]
            down_move = lows[i - 1] - lows[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
            else:
                plus_dm.append(0)
            
            if down_move > up_move and down_move > 0:
                minus_dm.append(down_move)
            else:
                minus_dm.append(0)
        
        # Calculate ATR
        atr_values = TechnicalIndicators.atr(highs, lows, closes, period)
        
        # Smooth DM values
        plus_di = []
        minus_di = []
        
        for i in range(period - 1, len(plus_dm)):
            if i == period - 1:
                smoothed_plus = sum(plus_dm[:period])
                smoothed_minus = sum(minus_dm[:period])
            else:
                smoothed_plus = smoothed_plus - (smoothed_plus / period) + plus_dm[i]
                smoothed_minus = smoothed_minus - (smoothed_minus / period) + minus_dm[i]
            
            atr = atr_values[i + 1] if atr_values[i + 1] else 1
            
            plus_di.append((smoothed_plus / atr) * 100 if atr > 0 else 0)
            minus_di.append((smoothed_minus / atr) * 100 if atr > 0 else 0)
        
        # Calculate DX
        dx_values = []
        for pdi, mdi in zip(plus_di, minus_di):
            di_sum = pdi + mdi
            if di_sum == 0:
                dx_values.append(0)
            else:
                dx_values.append(abs(pdi - mdi) / di_sum * 100)
        
        # Calculate ADX (smoothed DX)
        adx_values = [None] * (2 * period - 1)
        if len(dx_values) >= period:
            first_adx = sum(dx_values[:period]) / period
            adx_values.append(first_adx)
            
            for i in range(period, len(dx_values)):
                adx = (adx_values[-1] * (period - 1) + dx_values[i]) / period
                adx_values.append(adx)
        
        # Pad results
        plus_di_full = [None] * period + plus_di
        minus_di_full = [None] * period + minus_di
        
        # Ensure all lists are same length
        while len(adx_values) < len(closes):
            adx_values.append(adx_values[-1] if adx_values else None)
        while len(plus_di_full) < len(closes):
            plus_di_full.append(plus_di_full[-1] if plus_di_full else None)
        while len(minus_di_full) < len(closes):
            minus_di_full.append(minus_di_full[-1] if minus_di_full else None)
        
        return adx_values, plus_di_full, minus_di_full
    
    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        """
        Calculate pivot points
        
        Args:
            high: Previous period high
            low: Previous period low
            close: Previous period close
        
        Returns:
            Dictionary with pivot point levels
        """
        pivot = (high + low + close) / 3
        
        return {
            "pivot": round(pivot, 4),
            "r1": round(2 * pivot - low, 4),
            "r2": round(pivot + (high - low), 4),
            "r3": round(high + 2 * (pivot - low), 4),
            "s1": round(2 * pivot - high, 4),
            "s2": round(pivot - (high - low), 4),
            "s3": round(low - 2 * (high - pivot), 4)
        }
    
    @staticmethod
    def fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            high: Swing high
            low: Swing low
        
        Returns:
            Dictionary with Fibonacci levels
        """
        diff = high - low
        
        return {
            "0.0%": round(low, 4),
            "23.6%": round(low + 0.236 * diff, 4),
            "38.2%": round(low + 0.382 * diff, 4),
            "50.0%": round(low + 0.5 * diff, 4),
            "61.8%": round(low + 0.618 * diff, 4),
            "78.6%": round(low + 0.786 * diff, 4),
            "100.0%": round(high, 4)
        }


class SignalGenerator:
    """Generate trading signals from technical indicators"""
    
    @staticmethod
    def rsi_signal(rsi: float) -> Signal:
        """Generate signal from RSI value"""
        if rsi is None:
            return Signal.NEUTRAL
        
        if rsi <= 20:
            return Signal.STRONG_BUY
        elif rsi <= 30:
            return Signal.BUY
        elif rsi >= 80:
            return Signal.STRONG_SELL
        elif rsi >= 70:
            return Signal.SELL
        else:
            return Signal.NEUTRAL
    
    @staticmethod
    def macd_signal(
        macd: float,
        signal: float,
        prev_macd: Optional[float] = None,
        prev_signal: Optional[float] = None
    ) -> Signal:
        """Generate signal from MACD crossover"""
        if macd is None or signal is None:
            return Signal.NEUTRAL
        
        # Current position
        is_above = macd > signal
        
        # Check for crossover
        if prev_macd is not None and prev_signal is not None:
            was_above = prev_macd > prev_signal
            
            if is_above and not was_above:
                return Signal.BUY  # Bullish crossover
            elif not is_above and was_above:
                return Signal.SELL  # Bearish crossover
        
        return Signal.NEUTRAL
    
    @staticmethod
    def bollinger_signal(
        price: float,
        upper: float,
        lower: float,
        middle: float
    ) -> Signal:
        """Generate signal from Bollinger Bands position"""
        if None in (price, upper, lower, middle):
            return Signal.NEUTRAL
        
        # Calculate position as percentage
        band_width = upper - lower
        if band_width == 0:
            return Signal.NEUTRAL
        
        position = (price - lower) / band_width
        
        if position >= 1.0:  # Above upper band
            return Signal.SELL
        elif position <= 0.0:  # Below lower band
            return Signal.BUY
        elif position >= 0.8:  # Near upper band
            return Signal.SELL
        elif position <= 0.2:  # Near lower band
            return Signal.BUY
        else:
            return Signal.NEUTRAL
    
    @staticmethod
    def stochastic_signal(k: float, d: float) -> Signal:
        """Generate signal from Stochastic Oscillator"""
        if k is None or d is None:
            return Signal.NEUTRAL
        
        if k <= 20 and d <= 20:
            return Signal.BUY if k > d else Signal.STRONG_BUY
        elif k >= 80 and d >= 80:
            return Signal.SELL if k < d else Signal.STRONG_SELL
        elif k > d and k <= 30:
            return Signal.BUY
        elif k < d and k >= 70:
            return Signal.SELL
        else:
            return Signal.NEUTRAL
    
    @staticmethod
    def moving_average_signal(
        price: float,
        short_ma: float,
        long_ma: float
    ) -> Signal:
        """Generate signal from moving average crossover"""
        if None in (price, short_ma, long_ma):
            return Signal.NEUTRAL
        
        # Price above both MAs and short above long = bullish
        if price > short_ma > long_ma:
            return Signal.BUY
        # Price below both MAs and short below long = bearish
        elif price < short_ma < long_ma:
            return Signal.SELL
        # Mixed signals
        else:
            return Signal.NEUTRAL
    
    @staticmethod
    def adx_trend_strength(adx: float) -> str:
        """Interpret ADX trend strength"""
        if adx is None:
            return "unknown"
        
        if adx < 20:
            return "weak/no trend"
        elif adx < 40:
            return "developing trend"
        elif adx < 60:
            return "strong trend"
        else:
            return "very strong trend"
    
    @staticmethod
    def combine_signals(signals: List[Signal], weights: Optional[List[float]] = None) -> Signal:
        """
        Combine multiple signals into a single signal
        
        Args:
            signals: List of individual signals
            weights: Optional weights for each signal
        
        Returns:
            Combined signal
        """
        if not signals:
            return Signal.NEUTRAL
        
        if weights is None:
            weights = [1.0] * len(signals)
        
        # Convert signals to numeric values
        signal_values = {
            Signal.STRONG_BUY: 2,
            Signal.BUY: 1,
            Signal.NEUTRAL: 0,
            Signal.SELL: -1,
            Signal.STRONG_SELL: -2
        }
        
        weighted_sum = sum(
            signal_values[s] * w
            for s, w in zip(signals, weights)
        )
        
        total_weight = sum(weights)
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        if avg_score >= 1.5:
            return Signal.STRONG_BUY
        elif avg_score >= 0.5:
            return Signal.BUY
        elif avg_score <= -1.5:
            return Signal.STRONG_SELL
        elif avg_score <= -0.5:
            return Signal.SELL
        else:
            return Signal.NEUTRAL


def generate_technical_report(
    closes: List[float],
    highs: Optional[List[float]] = None,
    lows: Optional[List[float]] = None,
    volumes: Optional[List[float]] = None
) -> Dict:
    """
    Generate comprehensive technical analysis report
    
    Args:
        closes: List of closing prices
        highs: Optional list of high prices
        lows: Optional list of low prices
        volumes: Optional list of volumes
    
    Returns:
        Technical analysis report
    """
    if highs is None:
        highs = closes
    if lows is None:
        lows = closes
    if volumes is None:
        volumes = [1.0] * len(closes)
    
    ti = TechnicalIndicators
    sg = SignalGenerator
    
    # Calculate indicators
    rsi = ti.rsi(closes)
    macd_line, signal_line, histogram = ti.macd(closes)
    k, d = ti.stochastic(highs, lows, closes)
    upper_bb, middle_bb, lower_bb = ti.bollinger_bands(closes)
    atr = ti.atr(highs, lows, closes)
    adx, plus_di, minus_di = ti.adx(highs, lows, closes)
    sma_20 = ti.sma(closes, 20)
    sma_50 = ti.sma(closes, 50)
    ema_12 = ti.ema(closes, 12)
    ema_26 = ti.ema(closes, 26)
    
    # Get latest values
    current_price = closes[-1]
    
    # Generate signals
    signals = []
    
    rsi_val = rsi[-1]
    if rsi_val is not None:
        signals.append(sg.rsi_signal(rsi_val))
    
    macd_sig = sg.macd_signal(
        macd_line[-1], signal_line[-1],
        macd_line[-2] if len(macd_line) > 1 else None,
        signal_line[-2] if len(signal_line) > 1 else None
    )
    signals.append(macd_sig)
    
    bb_sig = sg.bollinger_signal(current_price, upper_bb[-1], lower_bb[-1], middle_bb[-1])
    signals.append(bb_sig)
    
    stoch_sig = sg.stochastic_signal(k[-1], d[-1])
    signals.append(stoch_sig)
    
    ma_sig = sg.moving_average_signal(current_price, sma_20[-1], sma_50[-1])
    signals.append(ma_sig)
    
    # Calculate support/resistance
    pivots = ti.pivot_points(max(highs[-20:]), min(lows[-20:]), closes[-1])
    fibs = ti.fibonacci_retracement(max(highs[-50:]), min(lows[-50:]))
    
    overall_signal = sg.combine_signals(signals)
    
    return {
        "current_price": round(current_price, 2),
        "indicators": {
            "rsi": round(rsi[-1], 2) if rsi[-1] else None,
            "macd": {
                "macd_line": round(macd_line[-1], 4) if macd_line[-1] else None,
                "signal_line": round(signal_line[-1], 4) if signal_line[-1] else None,
                "histogram": round(histogram[-1], 4) if histogram[-1] else None
            },
            "stochastic": {
                "k": round(k[-1], 2) if k[-1] else None,
                "d": round(d[-1], 2) if d[-1] else None
            },
            "bollinger_bands": {
                "upper": round(upper_bb[-1], 2) if upper_bb[-1] else None,
                "middle": round(middle_bb[-1], 2) if middle_bb[-1] else None,
                "lower": round(lower_bb[-1], 2) if lower_bb[-1] else None
            },
            "atr": round(atr[-1], 2) if atr[-1] else None,
            "adx": {
                "adx": round(adx[-1], 2) if adx[-1] else None,
                "plus_di": round(plus_di[-1], 2) if plus_di[-1] else None,
                "minus_di": round(minus_di[-1], 2) if minus_di[-1] else None,
                "trend_strength": sg.adx_trend_strength(adx[-1])
            },
            "moving_averages": {
                "sma_20": round(sma_20[-1], 2) if sma_20[-1] else None,
                "sma_50": round(sma_50[-1], 2) if sma_50[-1] else None,
                "ema_12": round(ema_12[-1], 2) if ema_12[-1] else None,
                "ema_26": round(ema_26[-1], 2) if ema_26[-1] else None
            }
        },
        "signals": {
            "rsi": sg.rsi_signal(rsi[-1]).value,
            "macd": macd_sig.value,
            "bollinger": bb_sig.value,
            "stochastic": stoch_sig.value,
            "moving_average": ma_sig.value
        },
        "overall_signal": overall_signal.value,
        "support_resistance": {
            "pivot_points": pivots,
            "fibonacci_levels": fibs
        }
    }
