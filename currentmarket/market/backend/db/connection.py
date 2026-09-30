import os
import sqlite3
from pathlib import Path
from typing import Any, List, Tuple, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "puravankara.db"

# Try loading .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
_USE_POSTGRES = False
_pg_conn_factory = None

if DATABASE_URL:
    try:
        import psycopg2
        # Test connection quickly
        test_conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
        test_conn.close()
        _USE_POSTGRES = True
        _pg_conn_factory = lambda: psycopg2.connect(DATABASE_URL)
        print("[DB] Connected to live PostgreSQL database.")
    except Exception as e:
        print(f"[DB] PostgreSQL unavailable ({e}). Falling back to local embedded SQLite database.")
        _USE_POSTGRES = False
else:
    print("[DB] DATABASE_URL not set. Using local embedded SQLite database.")


class DBConnection:
    def __init__(self):
        self.is_postgres = _USE_POSTGRES
        if self.is_postgres:
            self.conn = _pg_conn_factory()
        else:
            self.conn = sqlite3.connect(str(DB_FILE))
            self.conn.row_factory = sqlite3.Row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def query(self, sql: str, params: Tuple = ()) -> List[Any]:
        cur = self.conn.cursor()
        if not self.is_postgres:
            # Convert Postgres %s to SQLite ?
            sql = sql.replace("%s", "?")
            sql = sql.replace("ILIKE", "LIKE")
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows

    def query_one(self, sql: str, params: Tuple = ()) -> Optional[Any]:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: Tuple = ()) -> int:
        cur = self.conn.cursor()
        if not self.is_postgres:
            sql = sql.replace("%s", "?")
            sql = sql.replace("ILIKE", "LIKE")
        cur.execute(sql, params)
        self.conn.commit()
        last_id = getattr(cur, "lastrowid", None)
        cur.close()
        return last_id

    def execute_insert(self, sql: str, params: Tuple = ()) -> Optional[int]:
        """
        Executes an INSERT statement and returns the auto-generated primary key ID
        across both PostgreSQL and SQLite.
        """
        cur = self.conn.cursor()
        if self.is_postgres:
            if "RETURNING" not in sql.upper():
                sql = sql.rstrip("; \t\n") + " RETURNING id"
            cur.execute(sql, params)
            row = cur.fetchone()
            self.conn.commit()
            inserted_id = row[0] if row else None
        else:
            sql = sql.replace("%s", "?")
            sql = sql.replace("ILIKE", "LIKE")
            cur.execute(sql, params)
            self.conn.commit()
            inserted_id = cur.lastrowid
        cur.close()
        return inserted_id

    def execute_script(self, script: str):
        cur = self.conn.cursor()
        if not self.is_postgres:
            cur.executescript(script)
        else:
            cur.execute(script)
        self.conn.commit()
        cur.close()


_migration_done = False


def ensure_decision_tables_exist(db: DBConnection):
    """
    Idempotently creates decision_results and decision_evidence tables and adds
    decision_result_id to scenario_runs using dialect-appropriate DDL.
    Preserves all existing data in scenario_runs.
    """
    global _migration_done
    if _migration_done:
        return

    try:
        if db.is_postgres:
            # PostgreSQL DDL
            db.execute("""
                CREATE TABLE IF NOT EXISTS decision_results (
                    id SERIAL PRIMARY KEY,
                    project_name VARCHAR(255) NOT NULL,
                    decision VARCHAR(50) NOT NULL,
                    decision_engine_version VARCHAR(50) DEFAULT 'v2.5-hurdle',
                    scenario_considered BOOLEAN DEFAULT FALSE,
                    executive_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS decision_evidence (
                    id SERIAL PRIMARY KEY,
                    decision_result_id INTEGER NOT NULL REFERENCES decision_results(id) ON DELETE CASCADE,
                    category VARCHAR(100) NOT NULL,
                    factor VARCHAR(255) NOT NULL,
                    value VARCHAR(255),
                    interpretation TEXT,
                    source VARCHAR(255),
                    severity VARCHAR(50) DEFAULT 'INFO'
                )
            """)
            # Check if decision_result_id exists in scenario_runs
            col_check = db.query("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'scenario_runs' AND column_name = 'decision_result_id'
            """)
            if not col_check:
                db.execute("ALTER TABLE scenario_runs ADD COLUMN decision_result_id INTEGER REFERENCES decision_results(id)")
        else:
            # SQLite DDL
            db.execute("""
                CREATE TABLE IF NOT EXISTS decision_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    decision_engine_version TEXT DEFAULT 'v2.5-hurdle',
                    scenario_considered INTEGER DEFAULT 0,
                    executive_summary TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS decision_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_result_id INTEGER NOT NULL REFERENCES decision_results(id) ON DELETE CASCADE,
                    category TEXT NOT NULL,
                    factor TEXT NOT NULL,
                    value TEXT,
                    interpretation TEXT,
                    source TEXT,
                    severity TEXT DEFAULT 'INFO'
                )
            """)
            # Check if decision_result_id exists in scenario_runs
            cols = db.query("PRAGMA table_info(scenario_runs)")
            col_names = [dict(c)["name"] if hasattr(c, "keys") else c[1] for c in cols]
            if "decision_result_id" not in col_names:
                db.execute("ALTER TABLE scenario_runs ADD COLUMN decision_result_id INTEGER REFERENCES decision_results(id)")

        _migration_done = True
    except Exception as e:
        print(f"[DB Migration Warning] ensure_decision_tables_exist: {e}")


def get_db():
    conn = DBConnection()
    ensure_decision_tables_exist(conn)
    return conn

