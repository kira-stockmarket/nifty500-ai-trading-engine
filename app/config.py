import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration"""

    # API
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE: str = os.getenv(
        "DEEPSEEK_API_BASE", "https://api.deepseek.com"
    )
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # Data
    NIFTY500_DATA_SOURCE: str = os.getenv("NIFTY500_DATA_SOURCE", "csv")
    NIFTY500_UNIVERSE_PATH: str = os.getenv(
        "NIFTY500_UNIVERSE_PATH", str(BASE_DIR / "data" / "universe" / "nifty500.csv")
    )

    # Market
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    MARKET_OPEN: str = os.getenv("MARKET_OPEN", "09:15")
    MARKET_CLOSE: str = os.getenv("MARKET_CLOSE", "15:30")

    # Database
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH", str(BASE_DIR / "storage" / "nifty500.db")
    )
    MEMORY_PATH: str = os.getenv(
        "MEMORY_PATH", str(BASE_DIR / "storage" / "memory.json")
    )
    RULES_PATH: str = os.getenv("RULES_PATH", str(BASE_DIR / "storage" / "rules.json"))

    # Portfolio
    PORTFOLIO_INITIAL_CAPITAL: float = float(
        os.getenv("PORTFOLIO_INITIAL_CAPITAL", "1000000")
    )
    PORTFOLIO_RISK_PER_TRADE: float = float(
        os.getenv("PORTFOLIO_RISK_PER_TRADE", "0.5")
    )
    MAX_PORTFOLIO_RISK: float = float(os.getenv("MAX_PORTFOLIO_RISK", "5.0"))

    # Indicators
    EMA_FAST: int = int(os.getenv("EMA_FAST", "20"))
    EMA_MEDIUM: int = int(os.getenv("EMA_MEDIUM", "50"))
    EMA_SLOW: int = int(os.getenv("EMA_SLOW", "200"))

    RSI_PERIOD: int = int(os.getenv("RSI_PERIOD", "14"))
    ATR_PERIOD: int = int(os.getenv("ATR_PERIOD", "14"))
    VOLUME_MA_PERIOD: int = int(os.getenv("VOLUME_MA_PERIOD", "20"))

    # Strategy
    BREAKOUT_LOOKBACK: int = int(os.getenv("BREAKOUT_LOOKBACK", "20"))
    MIN_RELATIVE_VOLUME: float = float(os.getenv("MIN_RELATIVE_VOLUME", "1.5"))

    MIN_RR: float = float(os.getenv("MIN_RR", "1.5"))
    TARGET_RR: float = float(os.getenv("TARGET_RR", "2.0"))

    # Scanning
    MAX_AI_CANDIDATES: int = int(os.getenv("MAX_AI_CANDIDATES", "15"))
    AI_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("AI_CONFIDENCE_THRESHOLD", "65")
    )

    MIN_AVG_VOLUME: float = float(os.getenv("MIN_AVG_VOLUME", "100000"))
    MIN_AVG_TRADED_VALUE: float = float(
        os.getenv("MIN_AVG_TRADED_VALUE", "2500000")
    )

    SIGNAL_EXPIRY_MINUTES: int = int(os.getenv("SIGNAL_EXPIRY_MINUTES", "240"))

    # Costs
    BROKERAGE_PCT: float = float(os.getenv("BROKERAGE_PCT", "0.01"))
    STT_PCT: float = float(os.getenv("STT_PCT", "0.01"))
    SLIPPAGE_TICKS: int = int(os.getenv("SLIPPAGE_TICKS", "2"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
