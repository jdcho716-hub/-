from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.logger import get_logger, setup_logging
from quant_kor.core.paths import (
    DB_PATH,
    LOG_APP_DIR,
    LOG_AUDIT_DIR,
    LOG_ERROR_DIR,
    MANUAL_KRX_CSV_PATH,
    RAW_KRX_DIR,
)
from quant_kor.infra.db.sqlite_db import connect_sqlite
from quant_kor.ingestion.krx_collector import KRXStockMasterCollector


def _read_csv_text_with_fallback(path: Path) -> tuple[str, str]:
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    last_exc: Exception | None = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc), enc
        except UnicodeDecodeError as exc:
            last_exc = exc
            continue
    if last_exc:
        raise last_exc
    raise RuntimeError("Unexpected encoding fallback failure")


def _rewrite_csv_for_collector(csv_text: str) -> str:
    """Normalize header names so collector can consume more variants.

    Required mapping in this stage:
    - ticker: 종목코드, 단축코드, 표준코드, ISU_SRT_CD, isu_srt_cd, ticker
    - name: 종목명, 한글 종목명, 한글종목명, ISU_ABBRV, isu_abbrv, name
    - market: 시장구분, 시장, 시장명, MKT_TP_NM, mkt_tp_nm, market
    """

    ticker_candidates = ["종목코드", "단축코드", "표준코드", "ISU_SRT_CD", "isu_srt_cd", "ticker"]
    name_candidates = ["종목명", "한글 종목명", "한글종목명", "ISU_ABBRV", "isu_abbrv", "name"]
    market_candidates = ["시장구분", "시장", "시장명", "MKT_TP_NM", "mkt_tp_nm", "market"]

    reader = csv.DictReader(csv_text.splitlines())
    # csv module writer is avoided to keep a simple deterministic normalized text builder
    normalized_rows: list[dict[str, str]] = []

    for row in reader:
        def pick(candidates: list[str]) -> str:
            for key in candidates:
                val = row.get(key)
                if val is not None and str(val).strip() != "":
                    return str(val).strip()
            return ""

        normalized_rows.append(
            {
                "종목코드": pick(ticker_candidates),
                "종목명": pick(name_candidates),
                "시장구분": pick(market_candidates),
            }
        )

    # build normalized CSV text
    normalized_text = "종목코드,종목명,시장구분\n"
    for r in normalized_rows:
        # basic CSV escaping
        code = r["종목코드"].replace('"', '""')
        name = r["종목명"].replace('"', '""')
        market = r["시장구분"].replace('"', '""')
        normalized_text += f'"{code}","{name}","{market}"\n'

    return normalized_text


def main() -> None:
    setup_logging(LOG_APP_DIR, LOG_ERROR_DIR, LOG_AUDIT_DIR, "INFO")
    logger = get_logger(__name__)

    print(f"Using DB path: {DB_PATH}")
    print(f"Manual CSV path: {MANUAL_KRX_CSV_PATH}")

    if not MANUAL_KRX_CSV_PATH.exists():
        print("수동 CSV 파일이 없습니다.")
        print("아래 경로에 KRX 종목 마스터 CSV를 저장한 뒤 다시 실행하세요:")
        print(MANUAL_KRX_CSV_PATH)
        return

    try:
        csv_text, used_encoding = _read_csv_text_with_fallback(MANUAL_KRX_CSV_PATH)
    except Exception:
        logger.exception("Failed to decode manual CSV file with utf-8-sig/cp949/euc-kr")
        print("CSV 인코딩 해석에 실패했습니다. utf-8-sig, cp949, euc-kr 파일인지 확인하세요.")
        return

    print(f"Detected CSV encoding: {used_encoding}")

    normalized_csv_text = _rewrite_csv_for_collector(csv_text)

    conn = connect_sqlite(DB_PATH, timeout=30)
    try:
        collector = KRXStockMasterCollector(conn=conn, raw_dir=RAW_KRX_DIR, logger=logger)
        result = collector._import_csv_text(normalized_csv_text)
    except Exception:
        logger.exception("Manual KRX CSV import failed")
        print("수동 CSV import 중 오류가 발생했습니다. logs/error/error.log를 확인하세요.")
        return
    finally:
        conn.close()

    print("=== Manual KRX Stock Master Import Summary ===")
    print(f"Inserted: {result.inserted}")
    print(f"Updated: {result.updated}")
    print(f"Skipped: {result.skipped}")
    print(f"Failed: {result.failed}")


if __name__ == "__main__":
    main()
