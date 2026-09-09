import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pytz
from app.config import settings
from app.logging_config import StructuredLogger

logger = StructuredLogger(__name__)


class UniverseManager:
    """Manages NIFTY 500 universe"""

    def __init__(self, universe_path: str = None):
        self.universe_path = universe_path or settings.NIFTY500_UNIVERSE_PATH
        self.universe = None
        self.load_universe()

    def load_universe(self):
        """Load NIFTY 500 universe from CSV"""
        try:
            if Path(self.universe_path).exists():
                self.universe = pd.read_csv(self.universe_path)
                logger.data(
                    f"Loaded {len(self.universe)} symbols from {self.universe_path}"
                )
            else:
                logger.error(f"Universe file not found: {self.universe_path}")
                self.create_sample_universe()
        except Exception as e:
            logger.error(f"Failed to load universe: {str(e)}")
            self.create_sample_universe()

    def create_sample_universe(self):
        """Create sample NIFTY 500 universe for testing"""
        sample_stocks = [
            {
                "symbol": "RELIANCE",
                "company_name": "Reliance Industries",
                "sector": "ENERGY",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "TCS",
                "company_name": "Tata Consultancy Services",
                "sector": "IT",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "INFY",
                "company_name": "Infosys",
                "sector": "IT",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "HDFCBANK",
                "company_name": "HDFC Bank",
                "sector": "BANKING",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "ICICIBANK",
                "company_name": "ICICI Bank",
                "sector": "BANKING",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "SBIN",
                "company_name": "State Bank of India",
                "sector": "BANKING",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "ITC",
                "company_name": "ITC Limited",
                "sector": "FMCG",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "LT",
                "company_name": "Larsen & Toubro",
                "sector": "CONSTRUCTION",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "MARUTI",
                "company_name": "Maruti Suzuki",
                "sector": "AUTO",
                "exchange": "NSE",
                "active": 1,
            },
            {
                "symbol": "WIPRO",
                "company_name": "Wipro",
                "sector": "IT",
                "exchange": "NSE",
                "active": 1,
            },
        ]

        self.universe = pd.DataFrame(sample_stocks)
        logger.system(f"Created sample universe with {len(self.universe)} stocks")

    def get_symbols(self) -> List[str]:
        """Get list of active symbols"""
        if self.universe is None:
            return []
        active = self.universe[self.universe["active"] == 1]
        return active["symbol"].tolist()

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if self.universe is None:
            return None
        row = self.universe[self.universe["symbol"] == symbol]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def refresh(self):
        """Refresh universe data"""
        self.load_universe()

    @property
    def size(self) -> int:
        """Get universe size"""
        if self.universe is None:
            return 0
        return len(self.universe[self.universe["active"] == 1])


class MarketCalendar:
    """Indian market calendar"""

    def __init__(self, timezone: str = None):
        self.tz = pytz.timezone(timezone or settings.TIMEZONE)
        self.market_open = settings.MARKET_OPEN
        self.market_close = settings.MARKET_CLOSE

    def get_market_open_time(self, date: datetime) -> datetime:
        """Get market open time for date"""
        hour, minute = map(int, self.market_open.split(":"))
        return self.tz.localize(datetime(date.year, date.month, date.day, hour, minute))

    def get_market_close_time(self, date: datetime) -> datetime:
        """Get market close time for date"""
        hour, minute = map(int, self.market_close.split(":"))
        return self.tz.localize(datetime(date.year, date.month, date.day, hour, minute))

    def is_market_open(self, dt: datetime = None) -> bool:
        """Check if market is open at given datetime"""
        if dt is None:
            dt = datetime.now(self.tz)

        # Convert to IST if needed
        if dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        # Check weekend
        if dt.weekday() >= 5:  # Saturday=5, Sunday=6
            return False

        # Check holidays (simplified - can be expanded)
        market_open = self.get_market_open_time(dt)
        market_close = self.get_market_close_time(dt)

        return market_open <= dt <= market_close

    def is_trading_day(self, date: datetime) -> bool:
        """Check if day is a trading day"""
        return date.weekday() < 5  # Monday to Friday


class DataValidator:
    """Validates market data quality"""

    @staticmethod
    def validate_ohlcv(data: pd.DataFrame) -> tuple:
        """
        Validate OHLCV data
        Returns: (is_valid, error_message)
        """
        if data is None or data.empty:
            return False, "Empty dataset"

        required_cols = ["open", "high", "low", "close", "volume"]
        if not all(col in data.columns for col in required_cols):
            return False, "Missing required columns"

        # Check for NaN
        if data[required_cols].isnull().any().any():
            return False, "Contains NaN values"

        # Check for negative values
        if (data[["open", "high", "low", "close", "volume"]] < 0).any().any():
            return False, "Contains negative values"

        # Check for zero prices
        if (data[["open", "high", "low", "close"]] == 0).any().any():
            return False, "Contains zero prices"

        # Check OHLC relationship
        invalid_ohlc = (data["high"] < data["low"]) | (data["high"] < data["open"]) | (
            data["high"] < data["close"]
        )
        if invalid_ohlc.any():
            return False, "Invalid OHLC relationships"

        # Check for duplicate timestamps
        if data.index.duplicated().any():
            return False, "Duplicate timestamps"

        return True, "Valid"

    @staticmethod
    def check_missing_candles(data: pd.DataFrame, expected_freq: str = "D") -> bool:
        """Check for missing candles"""
        if data.empty:
            return False

        if not isinstance(data.index, pd.DatetimeIndex):
            return False

        expected_periods = pd.date_range(
            start=data.index.min(), end=data.index.max(), freq=expected_freq
        )

        # Filter for market days only (simplified)
        expected_periods = [p for p in expected_periods if p.weekday() < 5]

        missing = len(expected_periods) - len(data)
        return missing == 0


# Global instances
universe = UniverseManager()
market_calendar = MarketCalendar()
