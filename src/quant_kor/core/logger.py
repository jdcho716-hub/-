from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _file_handler(path: Path, level: int, fmt: str) -> RotatingFileHandler:
    h = RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(logging.Formatter(fmt))
    return h


def setup_logging(app_dir: Path, error_dir: Path, audit_dir: Path, level: str = "INFO") -> None:
    app_dir.mkdir(parents=True, exist_ok=True)
    error_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, level.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()

    root.addHandler(_file_handler(app_dir / "app.log", log_level, fmt))
    root.addHandler(_file_handler(error_dir / "error.log", logging.ERROR, fmt))

    sh = logging.StreamHandler()
    sh.setLevel(log_level)
    sh.setFormatter(logging.Formatter(fmt))
    root.addHandler(sh)

    audit = logging.getLogger("audit")
    audit.setLevel(logging.INFO)
    audit.handlers.clear()
    audit.addHandler(_file_handler(audit_dir / "audit.log", logging.INFO, fmt))
    audit.propagate = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
