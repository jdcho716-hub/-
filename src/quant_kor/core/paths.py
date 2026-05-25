from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "sqlite" / "quant.db"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_APP_DIR = LOG_DIR / "app"
LOG_ERROR_DIR = LOG_DIR / "error"
LOG_AUDIT_DIR = LOG_DIR / "audit"
RAW_KRX_DIR = LOG_DIR / "raw_api_response" / "krx"
MANUAL_KRX_CSV_PATH = PROJECT_ROOT / "data" / "manual" / "krx" / "stock_master.csv"
