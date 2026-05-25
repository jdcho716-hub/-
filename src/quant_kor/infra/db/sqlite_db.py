from __future__ import annotations

import sqlite3
from pathlib import Path

from quant_kor.core.exceptions import DatabaseError
from quant_kor.core.paths import DB_PATH
from quant_kor.infra.db.schema_sqlite import TABLE_SCHEMAS


def connect_sqlite(db_file: Path | None = None, timeout: int = 30) -> sqlite3.Connection:
    target = db_file or DB_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(target), timeout=timeout)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to connect sqlite DB: {exc}") from exc


def create_all_tables(conn: sqlite3.Connection) -> None:
    try:
        cursor = conn.cursor()
        for sql in TABLE_SCHEMAS.values():
            cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DatabaseError(f"Failed to create tables: {exc}") from exc


def list_tables(conn: sqlite3.Connection) -> list[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1;",
        (table_name,),
    )
    return cursor.fetchone() is not None
