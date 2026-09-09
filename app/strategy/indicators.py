import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from app.logging_config import StructuredLogger
from app.config import settings

logger = StructuredLogger(__name__)


class TechnicalIndicators:
    """Technical indicator calculations"""

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = df["high"] - df["low"]
        high_close = abs(df["high"] - df["close"].shift())
        low_close = abs(df["low"] - df["close"].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def bollinger_bands(
        data: pd.Series, period: int = 20, std_dev: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def volume_sma(data: pd.Series, period: int = 20) -> pd.Series:
        """Volume SMA"""
        return data.rolling(window=period).mean()

    @staticmethod
    def relative_volume(
        current_volume: float, volume_sma: float
    ) -> float:
        """Relative Volume ratio"""
        if volume_sma <= 0:
            return 0
        return current_volume / volume_sma


class BreakoutAnalysis:
    """Breakout detection and analysis"""

    @staticmethod
    def find_resistance(
        data: pd.DataFrame, lookback: int = 20
    ) -> Tuple[float, int]:
        """Find recent resistance level"""
        recent = data.tail(lookback)
        resistance = recent["high"].max()
        resistance_bar = recent["high"].idxmax()
        return resistance, resistance_bar

    @staticmethod
    def find_support(
        data: pd.DataFrame, lookback: int = 20
    ) -> Tuple[float, int]:
        """Find recent support level"""
        recent = data.tail(lookback)
        support = recent["low"].min()
        support_bar = recent["low"].idxmin()
        return support, support_bar

    @staticmethod
    def is_above_resistance(
        current_high: float, resistance: float, breakout_threshold: float = 0.002
    ) -> bool:
        """Check if price breaks above resistance"""
        return current_high > resistance * (1 + breakout_threshold)

    @staticmethod
    def is_below_support(
        current_low: float, support: float, breakdown_threshold: float = 0.002
    ) -> bool:
        """Check if price breaks below support"""
        return current_low < support * (1 - breakdown_threshold)


class TrendAnalysis:
    """Trend analysis"""

    @staticmethod
    def is_above_ema(price: float, ema: float) -> bool:
        """Check if price is above EMA"""
        if pd.isna(ema):
            return False
        return price > ema

    @staticmethod
    def is_below_ema(price: float, ema: float) -> bool:
        """Check if price is below EMA"""
        if pd.isna(ema):
            return False
        return price < ema

    @staticmethod
    def get_trend(ema_fast: float, ema_medium: float, ema_slow: float) -> str:
        """Determine trend from EMAs"""
        if pd.isna(ema_fast) or pd.isna(ema_medium) or pd.isna(ema_slow):
            return "UNKNOWN"

        if ema_fast > ema_medium > ema_slow:
            return "STRONG_BULL"
        elif ema_fast > ema_medium:
            return "BULL"
        elif ema_fast < ema_medium < ema_slow:
            return "STRONG_BEAR"
        elif ema_fast < ema_medium:
            return "BEAR"
        else:
            return "SIDEWAYS"

    @staticmethod
    def distance_from_ema(price: float, ema: float) -> float:
        """Distance from EMA as percentage"""
        if pd.isna(ema) or ema == 0:
            return 0
        return ((price - ema) / ema) * 100


class StrategyCalculator:
    """Calculate strategy signals and scores"""

    @staticmethod
    def calculate_indicators(
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Calculate all indicators"""
        df = data.copy()

        # EMAs
        df["ema_fast"] = TechnicalIndicators.ema(df["close"], settings.EMA_FAST)
        df["ema_medium"] = TechnicalIndicators.ema(df["close"], settings.EMA_MEDIUM)
        df["ema_slow"] = TechnicalIndicators.ema(df["close"], settings.EMA_SLOW)

        # RSI
        df["rsi"] = TechnicalIndicators.rsi(df["close"], settings.RSI_PERIOD)

        # ATR
        df["atr"] = TechnicalIndicators.atr(df, settings.ATR_PERIOD)
        df["atr_pct"] = (df["atr"] / df["close"]) * 100

        # Volume
        df["volume_sma"] = TechnicalIndicators.volume_sma(
            df["volume"], settings.VOLUME_MA_PERIOD
        )
        df["rel_volume"] = df["volume"] / df["volume_sma"]

        # Bollinger Bands
        df["bb_upper"], df["bb_middle"], df["bb_lower"] = TechnicalIndicators.bollinger_bands(
            df["close"]
        )

        return df

    @staticmethod
    def detect_breakout(data: pd.DataFrame) -> Dict:
        """Detect breakout setup"""
        if data is None or len(data) < settings.BREAKOUT_LOOKBACK + 1:
            return None

        latest = data.iloc[-1]
        prev = data.iloc[-2]

        # Find resistance
        resistance, _ = BreakoutAnalysis.find_resistance(
            data, settings.BREAKOUT_LOOKBACK
        )

        # Check breakout conditions
        breakout_detected = False
        if BreakoutAnalysis.is_above_resistance(latest["high"], resistance):
            breakout_detected = True

        return {
            "breakout_detected": breakout_detected,
            "resistance": resistance,
            "current_high": latest["high"],
            "breakout_confirmation": latest["close"] > resistance,
        }

    @staticmethod
    def calculate_breakout_score(
        data: pd.DataFrame, weights: Dict = None
    ) -> float:
        """Calculate breakout quality score (0-100)"""
        if data is None or len(data) < settings.BREAKOUT_LOOKBACK:
            return 0

        if weights is None:
            weights = {
                "trend": 0.20,
                "breakout": 0.20,
                "volume": 0.20,
                "momentum": 0.10,
                "higher_tf": 0.10,
                "risk_reward": 0.10,
                "liquidity": 0.05,
                "extension": 0.05,
            }

        latest = data.iloc[-1]

        score = 0

        # Trend score (20)
        trend = TrendAnalysis.get_trend(
            latest["ema_fast"], latest["ema_medium"], latest["ema_slow"]
        )
        trend_score = 0
        if trend == "STRONG_BULL":
            trend_score = 20
        elif trend == "BULL":
            trend_score = 15
        score += trend_score * weights["trend"] / 20

        # Breakout score (20)
        breakout = StrategyCalculator.detect_breakout(data)
        if breakout and breakout["breakout_detected"]:
            score += 20 * weights["breakout"]
        else:
            score += 10 * weights["breakout"]

        # Volume score (20)
        if latest["rel_volume"] > settings.MIN_RELATIVE_VOLUME:
            score += 20 * weights["volume"]
        else:
            score += 5 * weights["volume"]

        # Momentum score (10)
        rsi = latest["rsi"]
        if 40 < rsi < 70:
            score += 10 * weights["momentum"]
        elif rsi > 30:
            score += 5 * weights["momentum"]

        # Extension check (5)
        dist_from_ema = TrendAnalysis.distance_from_ema(
            latest["close"], latest["ema_slow"]
        )
        if dist_from_ema < 10:
            score += 5 * weights["extension"]
        else:
            score += 2 * weights["extension"]

        return min(100, max(0, score))
