"""Database management module for Nifty 100 Financial Intelligence Platform.

Handles SQLite connection pooling, schema initialization, transactional loading,
and PRAGMA foreign_key_check verification.
"""
from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite connections, DDL execution, and transactional table loading."""

    def __init__(self, db_path: str | Path, schema_path: Optional[str | Path] = None):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path) if schema_path else None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create a connection with foreign key enforcement enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Provide a transactional scope around a series of operations."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self, drop_existing: bool = True) -> None:
        """Initialize database with full schema and indexes from schema.sql."""
        if not self.schema_path or not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {self.schema_path}")

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = OFF;")
            if drop_existing:
                tables = [
                    "peer_percentiles", "financial_ratios", "peer_groups", "market_cap",
                    "stock_prices", "prosandcons", "documents", "analysis",
                    "cashflow", "balancesheet", "profitandloss", "sectors", "companies"
                ]
                for t in tables:
                    conn.execute(f"DROP TABLE IF EXISTS {t};")
            
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
            logger.info("Initialized database schema at %s", self.db_path)
        finally:
            conn.close()

    def load_dataframe(
        self,
        table_name: str,
        df: pd.DataFrame,
        clear_existing: bool = True,
        conn: Optional[sqlite3.Connection] = None,
    ) -> int:
        """Insert DataFrame records into target table. Returns number of rows inserted."""
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True

        try:
            if clear_existing:
                conn.execute(f"DELETE FROM {table_name};")
            
            df.to_sql(table_name, conn, if_exists="append", index=False)
            conn.commit()

            cur = conn.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cur.fetchone()[0]
            logger.info("Loaded %d rows into table '%s'", row_count, table_name)
            return row_count
        finally:
            if should_close:
                conn.close()

    def check_foreign_keys(self) -> list[tuple[Any, ...]]:
        """Run PRAGMA foreign_key_check. Returns list of violations (should be empty)."""
        conn = self.get_connection()
        try:
            cur = conn.execute("PRAGMA foreign_key_check;")
            violations = cur.fetchall()
            return [tuple(row) for row in violations]
        finally:
            conn.close()

    def get_table_counts(self) -> dict[str, int]:
        """Fetch row counts for all tables currently defined in SQLite database."""
        conn = self.get_connection()
        counts: dict[str, int] = {}
        try:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cur.fetchall()]
            for t in sorted(tables):
                c = conn.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
                counts[t] = c
            return counts
        finally:
            conn.close()
