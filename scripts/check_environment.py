from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_kor.core.settings import load_settings


def main() -> None:
    settings, configs, paths = load_settings()

    checks = {
        "configs/base.json": "base.json" in configs,
        "configs/data_sources.json": "data_sources.json" in configs,
        "configs/strategy_momentum.json": "strategy_momentum.json" in configs,
        "configs/risk_rules.json": "risk_rules.json" in configs,
        "configs/execution.json": "execution.json" in configs,
        "db directory exists": paths.db_file.parent.exists(),
        "logs/app exists": paths.log_app.exists(),
        "logs/error exists": paths.log_error.exists(),
        "logs/audit exists": paths.log_audit.exists(),
        "raw/krx exists": paths.raw_krx.exists(),
        "raw/dart exists": paths.raw_dart.exists(),
        "raw/kis exists": paths.raw_kis.exists(),
        "ENABLE_REAL_TRADING is False": settings.enable_real_trading is False,
        "KIS_IS_PAPER is True": settings.kis_is_paper is True,
    }

    print("=== Quant KOR Environment Check ===")
    print(f"PROJECT_ROOT: {paths.project_root}")
    print(f"DB_PATH: {settings.db_path}")
    print(f"APP_ENV: {settings.app_env}")
    print(f"ENABLE_REAL_TRADING: {settings.enable_real_trading}")
    print(f"KIS_IS_PAPER: {settings.kis_is_paper}")

    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"[{'OK' if ok else 'FAIL'}] {name}")

    if failed:
        print("\nEnvironment check completed with failures.")
        raise SystemExit(1)

    print("\nEnvironment check completed successfully.")


if __name__ == "__main__":
    main()
