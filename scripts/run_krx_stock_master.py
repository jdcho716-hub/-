from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.logger import get_logger, setup_logging
from quant_kor.core.paths import DB_PATH, LOG_APP_DIR, LOG_AUDIT_DIR, LOG_ERROR_DIR, RAW_KRX_DIR
from quant_kor.infra.clients.krx_client import KRXHTTPForbiddenError
from quant_kor.infra.db.sqlite_db import connect_sqlite
from quant_kor.ingestion.krx_collector import KRXStockMasterCollector


def main() -> None:
    setup_logging(LOG_APP_DIR, LOG_ERROR_DIR, LOG_AUDIT_DIR, "INFO")
    logger = get_logger(__name__)
    print(f"Using DB path: {DB_PATH}")

    conn = connect_sqlite(DB_PATH, timeout=30)
    try:
        collector = KRXStockMasterCollector(conn=conn, raw_dir=RAW_KRX_DIR, logger=logger)
        result = collector.run_web_fetch()
        print("=== KRX Stock Master Collection Summary ===")
        print(f"Total rows parsed: {result.total}")
        print(f"Inserted: {result.inserted}")
        print(f"Updated: {result.updated}")
        print(f"Skipped: {result.skipped}")
        print(f"Failed: {result.failed}")
    except KRXHTTPForbiddenError:
        logger.exception("KRX web endpoint blocked by HTTP 403")
        print("KRX 웹 엔드포인트가 자동 요청을 차단했습니다. KRX Open API 인증키 방식 또는 수동 CSV import 방식을 사용하세요.")
        print("대안 A) KRX Open API 인증키 방식: src/quant_kor/infra/clients/krx_client.py 의 fetch_stock_master_csv_openapi 인터페이스 확장")
        print("대안 B) 수동 CSV import: data/manual/krx/stock_master.csv 배치 후 python scripts/import_krx_stock_master_csv.py 실행")
    except Exception:
        logger.exception("KRX stock master collection failed")
        print("KRX 수집 중 예기치 못한 오류가 발생했습니다. logs/error/error.log를 확인하세요.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
