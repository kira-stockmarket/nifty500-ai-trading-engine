import sqlite3
from datetime import datetime
from pathlib import Path
from app.config import settings
from app.logging_config import StructuredLogger

logger = StructuredLogger(__name__)


class Database:
    """SQLite database management"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()

    def connect(self):
        """Connect to database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        """Initialize database tables"""
        conn = self.connect()
        cursor = conn.cursor()

        # Symbols table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                company_name TEXT,
                sector TEXT,
                industry TEXT,
                exchange TEXT DEFAULT 'NSE',
                active INTEGER DEFAULT 1,
                effective_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Market data metadata
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_data_metadata (
                id INTEGER PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                last_update TEXT,
                data_points INTEGER,
                date_range_start TEXT,
                date_range_end TEXT,
                data_status TEXT,
                error_message TEXT,
                FOREIGN KEY (symbol) REFERENCES symbols(symbol)
            )
        """
        )

        # Signals table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY,
                signal_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                strategy TEXT,
                direction TEXT,
                entry REAL,
                stop_loss REAL,
                target REAL,
                risk_reward REAL,
                quantity INTEGER,
                risk_percent REAL,
                technical_score REAL,
                ai_score REAL,
                final_score REAL,
                market_regime TEXT,
                sector TEXT,
                status TEXT DEFAULT 'NEW',
                reason TEXT,
                warnings TEXT,
                invalidation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                FOREIGN KEY (symbol) REFERENCES symbols(symbol)
            )
        """
        )

        # AI decisions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY,
                signal_id TEXT NOT NULL,
                decision TEXT,
                confidence_score REAL,
                setup_quality REAL,
                risk_level TEXT,
                ai_reasoning TEXT,
                ai_warnings TEXT,
                invalidate_if TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """
        )

        # Trade records
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                strategy TEXT,
                setup TEXT,
                direction TEXT,
                entry REAL,
                stop_loss REAL,
                target REAL,
                quantity INTEGER,
                exit_price REAL,
                result TEXT,
                r_multiple REAL,
                holding_minutes INTEGER,
                volume REAL,
                atr REAL,
                rsi REAL,
                trend TEXT,
                breakout_score REAL,
                ai_confidence REAL,
                market_regime TEXT,
                sector TEXT,
                reason_entry TEXT,
                reason_exit TEXT,
                gross_pnl REAL,
                costs REAL,
                net_pnl REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Audit rules
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_rules (
                id INTEGER PRIMARY KEY,
                rule_id TEXT UNIQUE NOT NULL,
                affected_setup TEXT,
                penalty_points REAL,
                sample_size INTEGER,
                win_rate REAL,
                avg_r REAL,
                evidence TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        """
        )

        # Scan runs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_runs (
                id INTEGER PRIMARY KEY,
                scan_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                universe_size INTEGER,
                data_ok INTEGER,
                data_failed INTEGER,
                candidates INTEGER,
                ai_validated INTEGER,
                final_signals INTEGER,
                scan_duration_seconds REAL,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Audit runs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_runs (
                id INTEGER PRIMARY KEY,
                audit_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                trades_analyzed INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                patterns_found INTEGER,
                new_rules INTEGER,
                rules_updated INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Portfolio snapshots
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                cash REAL,
                equity REAL,
                total_value REAL,
                open_positions INTEGER,
                realized_pnl REAL,
                unrealized_pnl REAL,
                max_drawdown REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(date)")

        conn.commit()
        logger.system("Database initialized")

    def execute(self, query: str, params: tuple = ()):
        """Execute query"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

    def fetchone(self, query: str, params: tuple = ()):
        """Fetch single row"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


# Global database instance
db = Database()
