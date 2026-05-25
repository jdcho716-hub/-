from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Stock(Base):
    __tablename__ = "stocks"

    ticker: Mapped[str] = mapped_column(String(12), primary_key=True)
    corp_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    market: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    listing_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    delisting_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    is_etf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_spac: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_managed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("date", "ticker", name="uq_daily_prices_date_ticker"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(12), ForeignKey("stocks.ticker"), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    adjusted_close: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    trading_value: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True, index=True)
    market_cap: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="KRX")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DartCorpCode(Base):
    __tablename__ = "dart_corp_codes"

    corp_code: Mapped[str] = mapped_column(String(12), primary_key=True)
    ticker: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    corp_name: Mapped[str] = mapped_column(String(200), nullable=False)
    modify_date: Mapped[Date | None] = mapped_column(Date, nullable=True)


class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    __table_args__ = (
        UniqueConstraint(
            "ticker", "corp_code", "report_year", "report_code", "statement_type", "account_name",
            name="uq_financial_statements_key"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    corp_code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    report_year: Mapped[int] = mapped_column(Integer, nullable=False)
    report_code: Mapped[str] = mapped_column(String(20), nullable=False)
    report_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disclosure_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    account_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    statement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Disclosure(Base):
    __tablename__ = "disclosures"

    rcept_no: Mapped[str] = mapped_column(String(30), primary_key=True)
    corp_code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    ticker: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    corp_name: Mapped[str] = mapped_column(String(200), nullable=False)
    report_name: Mapped[str] = mapped_column(String(300), nullable=False)
    disclosure_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    disclosure_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Factor(Base):
    __tablename__ = "factors"
    __table_args__ = (UniqueConstraint("date", "ticker", name="uq_factors_date_ticker"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    momentum_20d: Mapped[float | None] = mapped_column(Float, nullable=True)
    momentum_60d: Mapped[float | None] = mapped_column(Float, nullable=True)
    momentum_120d: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility_20d: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility_60d: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_trading_value_20d: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    ma_20: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    ma_60: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    ma_120: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    distance_from_ma20: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_momentum: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_liquidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    initial_cash: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    final_value: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    total_return: Mapped[float] = mapped_column(Float, nullable=False)
    cagr: Mapped[float | None] = mapped_column(Float, nullable=True)
    mdd: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility: Mapped[float | None] = mapped_column(Float, nullable=True)
    sharpe: Mapped[float | None] = mapped_column(Float, nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("date", "ticker", "signal_type", "strategy_name", name="uq_signals_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(10), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_pass: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    date_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    broker: Mapped[str] = mapped_column(String(20), nullable=False, default="KIS")
    is_paper: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Execution(Base):
    __tablename__ = "executions"

    execution_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.order_id"), nullable=False, index=True)
    date_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    fee: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    tax: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    slippage: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    cash: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    market_value: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    daily_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    cumulative_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
