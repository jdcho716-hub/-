from __future__ import annotations

import csv
import io
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from quant_kor.infra.clients.krx_client import KRXClient


@dataclass
class CollectResult:
    total: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0


class KRXStockMasterCollector:
    TICKER_KEYS = ["종목코드", "단축코드", "isu_srt_cd", "ISU_SRT_CD", "ticker"]
    NAME_KEYS = ["종목명", "한글 종목명", "isu_abbrv", "ISU_ABBRV", "name"]
    MARKET_KEYS = ["시장구분", "시장", "mkt_tp_nm", "MKT_TP_NM", "market"]

    def __init__(self, conn: sqlite3.Connection, raw_dir: Path, logger: logging.Logger) -> None:
        self.conn = conn
        self.logger = logger
        self.client = KRXClient(raw_dir=raw_dir)

    def run_web_fetch(self) -> CollectResult:
        csv_text = self.client.fetch_stock_master_csv_web(market="ALL")
        return self._import_csv_text(csv_text)

    def import_manual_csv_file(self, csv_file: Path) -> CollectResult:
        csv_text = csv_file.read_text(encoding="utf-8-sig", errors="replace")
        return self._import_csv_text(csv_text)

    def _import_csv_text(self, csv_text: str) -> CollectResult:
        result = CollectResult()
        reader = csv.DictReader(io.StringIO(csv_text))

        for row in reader:
            result.total += 1
            try:
                rec = self._normalize_row(row)
                if rec is None:
                    result.skipped += 1
                    continue
                changed = self._upsert_stock(rec)
                if changed == "insert":
                    result.inserted += 1
                else:
                    result.updated += 1
            except Exception as exc:
                result.failed += 1
                self.logger.exception("Failed to process stock row: %s", exc)

        self.conn.commit()
        return result

    @classmethod
    def _pick_value(cls, row: dict[str, str], keys: list[str]) -> str:
        for k in keys:
            v = row.get(k)
            if v is not None and str(v).strip() != "":
                return str(v).strip()
        return ""

    def _normalize_row(self, row: dict[str, str]):
        ticker = self._pick_value(row, self.TICKER_KEYS)
        name = self._pick_value(row, self.NAME_KEYS)
        market = self._pick_value(row, self.MARKET_KEYS).upper()

        if not ticker or not name:
            return None

        ticker = ticker.zfill(6)
        if len(ticker) != 6 or not ticker.isdigit():
            return None

        if market not in {"KOSPI", "KOSDAQ"}:
            return None

        # TODO: ETF/SPAC/우선주는 공식 분류 컬럼 기준으로 재분류 필요
        is_etf = 1 if "ETF" in name.upper() else 0
        is_spac = 1 if "스팩" in name or "SPAC" in name.upper() else 0
        is_preferred = 1 if name.endswith("우") or "우B" in name or "우선주" in name else 0

        return {
            "ticker": ticker,
            "name": name,
            "market": market,
            "sector": None,
            "industry": None,
            "listing_date": None,
            "is_etf": is_etf,
            "is_spac": is_spac,
            "is_preferred": is_preferred,
            "is_suspended": 0,
            "is_managed": 0,
            "updated_at": datetime.utcnow().isoformat(timespec="seconds"),
        }

    def _upsert_stock(self, rec: dict[str, object]) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT ticker FROM stocks WHERE ticker = ?", (rec["ticker"],))
        exists = cur.fetchone()

        if exists is None:
            cur.execute(
                """
                INSERT INTO stocks (
                    ticker, corp_code, name, market, sector, industry, listing_date, delisting_date,
                    is_etf, is_spac, is_preferred, is_suspended, is_managed, updated_at
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec["ticker"], rec["name"], rec["market"], rec["sector"], rec["industry"], rec["listing_date"],
                    rec["is_etf"], rec["is_spac"], rec["is_preferred"], rec["is_suspended"], rec["is_managed"], rec["updated_at"],
                ),
            )
            return "insert"

        cur.execute(
            """
            UPDATE stocks
            SET name=?, market=?, sector=?, industry=?,
                is_etf=?, is_spac=?, is_preferred=?,
                is_suspended=?, is_managed=?, updated_at=?
            WHERE ticker=?
            """,
            (
                rec["name"], rec["market"], rec["sector"], rec["industry"],
                rec["is_etf"], rec["is_spac"], rec["is_preferred"],
                rec["is_suspended"], rec["is_managed"], rec["updated_at"], rec["ticker"],
            ),
        )
        return "update"
