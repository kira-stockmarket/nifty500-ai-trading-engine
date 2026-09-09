import pandas as pd
import numpy as np
from typing import Optional, Dict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from app.logging_config import StructuredLogger
from app.data.universe import DataValidator

logger = StructuredLogger(__name__)


class DataProvider(ABC):
    """Base data provider interface"""

    @abstractmethod
    def get_daily_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get daily OHLCV data"""
        pass

    @abstractmethod
    def get_intraday_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get intraday OHLCV data"""
        pass


class CSVDataProvider(DataProvider):
    """CSV-based data provider for local development"""

    def __init__(self, data_dir: str = "data/market"):
        self.data_dir = data_dir

    def get_daily_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load daily data from CSV"""
        try:
            file_path = f"{self.data_dir}/{symbol}_daily.csv"
            df = pd.read_csv(file_path, parse_dates=["timestamp"], index_col="timestamp")
            df.columns = df.columns.str.lower()

            # Ensure required columns
            required = ["open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required):
                logger.error(f"{symbol}: Missing columns")
                return None

            # Validate
            is_valid, msg = DataValidator.validate_ohlcv(df)
            if not is_valid:
                logger.error(f"{symbol}: {msg}")
                return None

            return df
        except FileNotFoundError:
            logger.error(f"{symbol}: Data file not found")
            return None
        except Exception as e:
            logger.error(f"{symbol}: Error loading data - {str(e)}")
            return None

    def get_intraday_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Load intraday data from CSV"""
        try:
            file_path = f"{self.data_dir}/{symbol}_{timeframe}.csv"
            df = pd.read_csv(file_path, parse_dates=["timestamp"], index_col="timestamp")
            df.columns = df.columns.str.lower()

            is_valid, msg = DataValidator.validate_ohlcv(df)
            if not is_valid:
                return None

            return df
        except Exception as e:
            logger.error(f"{symbol} {timeframe}: {str(e)}")
            return None


class MarketDataManager:
    """Manages market data retrieval and caching"""

    def __init__(self, provider: DataProvider = None):
        self.provider = provider or CSVDataProvider()
        self.cache = {}

    def get_daily_ohlcv(self, symbol: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Get daily OHLCV data with caching"""
        cache_key = f"{symbol}_daily"

        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        data = self.provider.get_daily_data(symbol)
        if data is not None and use_cache:
            self.cache[cache_key] = data

        return data

    def get_intraday_ohlcv(
        self, symbol: str, timeframe: str, use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """Get intraday OHLCV data with caching"""
        cache_key = f"{symbol}_{timeframe}"

        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        data = self.provider.get_intraday_data(symbol, timeframe)
        if data is not None and use_cache:
            self.cache[cache_key] = data

        return data

    def clear_cache(self):
        """Clear cache"""
        self.cache.clear()

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest closing price"""
        data = self.get_daily_ohlcv(symbol)
        if data is None or data.empty:
            return None
        return float(data["close"].iloc[-1])

    def get_volume_sma(
        self, symbol: str, period: int = 20
    ) -> Optional[float]:
        """Get volume SMA"""
        data = self.get_daily_ohlcv(symbol)
        if data is None or len(data) < period:
            return None
        return float(data["volume"].tail(period).mean())

    def get_latest_atr(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate ATR"""
        data = self.get_daily_ohlcv(symbol)
        if data is None or len(data) < period:
            return None

        high_low = data["high"] - data["low"]
        high_close = abs(data["high"] - data["close"].shift())
        low_close = abs(data["low"] - data["close"].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.tail(period).mean()

        return float(atr)


# Global instance
market_data = MarketDataManager()
