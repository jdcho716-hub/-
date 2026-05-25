from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quant_kor.core.exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class AppSettings:
    app_env: str
    tz: str
    db_path: str
    db_timeout: int
    enable_real_trading: bool
    kis_is_paper: bool
    log_level: str
    log_dir: str
    raw_api_log_dir: str


@dataclass(frozen=True)
class Paths:
    project_root: Path
    db_file: Path
    log_app: Path
    log_error: Path
    log_audit: Path
    raw_krx: Path
    raw_dart: Path
    raw_kis: Path


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_env_file(env_path: Path = ENV_FILE) -> dict[str, str]:
    if not env_path.exists():
        return {}
    env_data: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_data[key.strip()] = value.strip().strip('"').strip("'")
    return env_data


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_configs(config_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    config_dir = config_dir or (PROJECT_ROOT / "configs")
    files = [
        "base.json",
        "data_sources.json",
        "strategy_momentum.json",
        "risk_rules.json",
        "execution.json",
    ]
    return {name: _read_json(config_dir / name) for name in files}


def load_settings() -> tuple[AppSettings, dict[str, dict[str, Any]], Paths]:
    env_map = load_env_file()
    for k, v in env_map.items():
        os.environ.setdefault(k, v)

    configs = load_json_configs()
    base = configs["base.json"]
    paths_cfg = base.get("paths", {})
    logs_cfg = paths_cfg.get("logs", {})
    raw_cfg = logs_cfg.get("raw_api", {})

    settings = AppSettings(
        app_env=os.getenv("APP_ENV", "dev"),
        tz=os.getenv("TZ", "Asia/Seoul"),
        db_path=os.getenv("DB_PATH", base.get("database", {}).get("db_path", "db/sqlite/quant.db")),
        db_timeout=int(os.getenv("DB_TIMEOUT", str(base.get("database", {}).get("timeout", 30)))),
        enable_real_trading=_parse_bool(os.getenv("ENABLE_REAL_TRADING", "false"), False),
        kis_is_paper=_parse_bool(os.getenv("KIS_IS_PAPER", "true"), True),
        log_level=os.getenv("LOG_LEVEL", base.get("logging", {}).get("level", "INFO")),
        log_dir=os.getenv("LOG_DIR", "logs"),
        raw_api_log_dir=os.getenv("RAW_API_LOG_DIR", "logs/raw_api_response"),
    )

    db_file = PROJECT_ROOT / settings.db_path
    paths = Paths(
        project_root=PROJECT_ROOT,
        db_file=db_file,
        log_app=PROJECT_ROOT / logs_cfg.get("app", "logs/app"),
        log_error=PROJECT_ROOT / logs_cfg.get("error", "logs/error"),
        log_audit=PROJECT_ROOT / logs_cfg.get("audit", "logs/audit"),
        raw_krx=PROJECT_ROOT / raw_cfg.get("krx", "logs/raw_api_response/krx"),
        raw_dart=PROJECT_ROOT / raw_cfg.get("dart", "logs/raw_api_response/dart"),
        raw_kis=PROJECT_ROOT / raw_cfg.get("kis", "logs/raw_api_response/kis"),
    )

    for p in [paths.db_file.parent, paths.log_app, paths.log_error, paths.log_audit, paths.raw_krx, paths.raw_dart, paths.raw_kis]:
        p.mkdir(parents=True, exist_ok=True)

    return settings, configs, paths
