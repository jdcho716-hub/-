from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.settings import load_settings
from quant_kor.infra.db.sqlite_db import connect_sqlite, list_tables


def main() -> None:
    settings, _, paths = load_settings()
    conn = connect_sqlite(paths.db_file, timeout=settings.db_timeout)
    try:
        tables = list_tables(conn)
    finally:
        conn.close()

    print(f"DB file: {paths.db_file}")
    if not paths.db_file.exists():
        print("Database file not found.")
        raise SystemExit(1)

    print("Tables:")
    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    main()
