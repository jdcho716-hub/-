from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.logger import get_logger, setup_logging
from quant_kor.core.paths import DB_PATH, LOG_APP_DIR, LOG_AUDIT_DIR, LOG_ERROR_DIR
from quant_kor.infra.db.sqlite_db import connect_sqlite, create_all_tables, list_tables


def main() -> None:
    setup_logging(LOG_APP_DIR, LOG_ERROR_DIR, LOG_AUDIT_DIR, "INFO")
    logger = get_logger(__name__)
    print(f"Using DB path: {DB_PATH}")

    logger.info("Initializing sqlite database at %s", DB_PATH)
    conn = connect_sqlite(DB_PATH, timeout=30)
    try:
        create_all_tables(conn)
        tables = list_tables(conn)
        logger.info("Created/validated %d tables", len(tables))
        print("Database initialized.")
        print("Tables:")
        for t in tables:
            print(f"- {t}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
