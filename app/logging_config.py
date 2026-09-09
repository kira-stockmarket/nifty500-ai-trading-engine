import logging
import json
from datetime import datetime
from pathlib import Path

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup structured logging"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler("logs/nifty500.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


class StructuredLogger:
    """Structured logging with prefixes"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def system(self, message: str):
        self.logger.info(f"[SYSTEM] {message}")

    def data(self, message: str):
        self.logger.info(f"[DATA] {message}")

    def scan(self, message: str):
        self.logger.info(f"[SCAN] {message}")

    def signal(self, message: str):
        self.logger.info(f"[SIGNAL] {message}")

    def ai(self, message: str):
        self.logger.info(f"[AI] {message}")

    def risk(self, message: str):
        self.logger.info(f"[RISK] {message}")

    def duplicate_prevented(self, message: str):
        self.logger.info(f"[DUPLICATE PREVENTED] {message}")

    def reversal(self, message: str):
        self.logger.warning(f"[REVERSAL] {message}")

    def learning(self, message: str):
        self.logger.info(f"[LEARNING] {message}")

    def auditor(self, message: str):
        self.logger.info(f"[AUDITOR] {message}")

    def backtest(self, message: str):
        self.logger.info(f"[BACKTEST] {message}")

    def error(self, message: str):
        self.logger.error(f"[ERROR] {message}")


# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

logger = StructuredLogger(__name__)
