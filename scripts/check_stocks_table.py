from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.paths import DB_PATH
from quant_kor.infra.db.sqlite_db import connect_sqlite, table_exists


def main() -> None:
    print(f"Using DB path: {DB_PATH}")

    if not DB_PATH.exists():
        print("DB 파일이 없습니다. 먼저 python scripts/init_db.py 를 실행하세요.")
        return

    conn = connect_sqlite(DB_PATH, timeout=30)
    try:
        if not table_exists(conn, "stocks"):
            print("stocks 테이블이 없습니다. 먼저 python scripts/init_db.py 를 실행하세요.")
            return

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM stocks")
        total = cur.fetchone()[0]

        cur.execute("SELECT market, COUNT(*) FROM stocks GROUP BY market ORDER BY market")
        market_counts = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM stocks WHERE is_etf=1")
        etf_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM stocks WHERE is_spac=1")
        spac_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM stocks WHERE is_preferred=1")
        preferred_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM stocks WHERE is_suspended=1")
        suspended_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM stocks WHERE is_managed=1")
        managed_count = cur.fetchone()[0]
    finally:
        conn.close()

    print("=== stocks table check ===")
    print(f"Total stocks: {total}")
    print("By market:")
    for market, cnt in market_counts:
        print(f"- {market}: {cnt}")
    print(f"ETF flagged: {etf_count}")
    print(f"SPAC flagged: {spac_count}")
    print(f"Preferred flagged: {preferred_count}")
    print(f"Suspended flagged: {suspended_count}")
    print(f"Managed flagged: {managed_count}")


if __name__ == "__main__":
    main()
