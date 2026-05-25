TABLE_SCHEMAS = {
    "stocks": """
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            corp_code TEXT,
            name TEXT NOT NULL,
            market TEXT,
            sector TEXT,
            industry TEXT,
            listing_date TEXT,
            delisting_date TEXT,
            is_etf INTEGER NOT NULL DEFAULT 0,
            is_spac INTEGER NOT NULL DEFAULT 0,
            is_preferred INTEGER NOT NULL DEFAULT 0,
            is_suspended INTEGER NOT NULL DEFAULT 0,
            is_managed INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "daily_prices": """
        CREATE TABLE IF NOT EXISTS daily_prices (
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            adjusted_close REAL,
            volume INTEGER NOT NULL,
            trading_value REAL,
            market_cap REAL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (date, ticker),
            FOREIGN KEY (ticker) REFERENCES stocks(ticker)
        )
    """,
    "dart_corp_codes": """
        CREATE TABLE IF NOT EXISTS dart_corp_codes (
            corp_code TEXT PRIMARY KEY,
            ticker TEXT,
            corp_name TEXT NOT NULL,
            modify_date TEXT
        )
    """,
    "financial_statements": """
        CREATE TABLE IF NOT EXISTS financial_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            corp_code TEXT NOT NULL,
            report_year INTEGER NOT NULL,
            report_code TEXT NOT NULL,
            report_name TEXT,
            disclosure_date TEXT,
            account_name TEXT NOT NULL,
            amount REAL,
            currency TEXT,
            statement_type TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(ticker, corp_code, report_year, report_code, statement_type, account_name)
        )
    """,
    "disclosures": """
        CREATE TABLE IF NOT EXISTS disclosures (
            rcept_no TEXT PRIMARY KEY,
            corp_code TEXT NOT NULL,
            ticker TEXT,
            corp_name TEXT NOT NULL,
            report_name TEXT NOT NULL,
            disclosure_date TEXT NOT NULL,
            disclosure_time TEXT,
            category TEXT,
            url TEXT,
            risk_flag INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "factors": """
        CREATE TABLE IF NOT EXISTS factors (
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            momentum_20d REAL,
            momentum_60d REAL,
            momentum_120d REAL,
            volatility_20d REAL,
            volatility_60d REAL,
            avg_trading_value_20d REAL,
            ma_20 REAL,
            ma_60 REAL,
            ma_120 REAL,
            distance_from_ma20 REAL,
            score_momentum REAL,
            score_liquidity REAL,
            total_score REAL,
            PRIMARY KEY (date, ticker)
        )
    """,
    "backtest_results": """
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            initial_cash REAL NOT NULL,
            final_value REAL NOT NULL,
            total_return REAL NOT NULL,
            cagr REAL,
            mdd REAL,
            volatility REAL,
            sharpe REAL,
            win_rate REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "signals": """
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            strategy_name TEXT NOT NULL,
            reason TEXT,
            target_weight REAL,
            risk_pass INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(date, ticker, signal_type, strategy_name)
        )
    """,
    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            date_time TEXT NOT NULL,
            ticker TEXT NOT NULL,
            side TEXT NOT NULL,
            order_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL,
            status TEXT NOT NULL,
            broker TEXT NOT NULL,
            is_paper INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "executions": """
        CREATE TABLE IF NOT EXISTS executions (
            execution_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            date_time TEXT NOT NULL,
            ticker TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            fee REAL,
            tax REAL,
            slippage REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """,
    "portfolio_snapshots": """
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            date TEXT PRIMARY KEY,
            cash REAL NOT NULL,
            total_value REAL NOT NULL,
            market_value REAL NOT NULL,
            daily_return REAL,
            cumulative_return REAL,
            drawdown REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
}
