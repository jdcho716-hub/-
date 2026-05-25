from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from quant_kor.core.settings import load_settings


def build_engine() -> Engine:
    settings, _, _ = load_settings()
    return create_engine(settings.db_url, echo=settings.db_echo, future=True)


def get_session_factory() -> sessionmaker:
    engine = build_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
