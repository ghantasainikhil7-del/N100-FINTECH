-- ============================================================================
-- Nifty 100 Financial Intelligence Platform · SQLite DDL Schema
-- Database: nifty100.db
-- Sprint: Sprint 1 (Days 01–07) · 34 Story Points
-- Specification: Section 5, 6, 7 & 8 of Project Execution Plan v1.0
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Master Company Reference
CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR(12) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_logo TEXT,
    about_company TEXT,
    website TEXT,
    chart_link TEXT,
    bse_profile TEXT,
    nse_profile TEXT,
    face_value NUMERIC NOT NULL DEFAULT 1,
    book_value NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Annual Profit & Loss Statements
CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER,
    company_id VARCHAR(12) NOT NULL,
    year VARCHAR(7) NOT NULL,
    sales NUMERIC NOT NULL,
    expenses NUMERIC,
    operating_profit NUMERIC,
    opm_percentage NUMERIC,
    other_income NUMERIC,
    interest NUMERIC DEFAULT 0,
    depreciation NUMERIC DEFAULT 0,
    profit_before_tax NUMERIC,
    tax_percentage NUMERIC,
    net_profit NUMERIC,
    eps NUMERIC,
    dividend_payout NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 3. Annual Balance Sheet Statements
CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER,
    company_id VARCHAR(12) NOT NULL,
    year VARCHAR(7) NOT NULL,
    equity_capital NUMERIC NOT NULL,
    reserves NUMERIC DEFAULT 0,
    borrowings NUMERIC DEFAULT 0,
    other_liabilities NUMERIC DEFAULT 0,
    total_liabilities NUMERIC NOT NULL,
    fixed_assets NUMERIC DEFAULT 0,
    cwip NUMERIC DEFAULT 0,
    investments NUMERIC DEFAULT 0,
    other_asset NUMERIC DEFAULT 0,
    total_assets NUMERIC NOT NULL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 4. Annual Cash Flow Statements
CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER,
    company_id VARCHAR(12) NOT NULL,
    year VARCHAR(7) NOT NULL,
    operating_activity NUMERIC DEFAULT 0,
    investing_activity NUMERIC DEFAULT 0,
    financing_activity NUMERIC DEFAULT 0,
    net_cash_flow NUMERIC DEFAULT 0,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 5. Qualitative Growth Analysis (CAGR)
CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR(12) NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Annual Report Repository
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR(12) NOT NULL,
    Year INTEGER NOT NULL,
    Annual_Report TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 7. Qualitative Insights (Pros & Cons)
CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR(12) NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 8. Sector & Market Cap Category Mapping
CREATE TABLE IF NOT EXISTS sectors (
    company_id VARCHAR(12) PRIMARY KEY,
    broad_sector VARCHAR(100) NOT NULL,
    sub_sector VARCHAR(100) NOT NULL,
    index_weight_pct NUMERIC DEFAULT 1.0,
    market_cap_category VARCHAR(50) DEFAULT 'Large Cap',
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 9. Monthly OHLCV Stock Prices
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id VARCHAR(12) NOT NULL,
    date VARCHAR(10) NOT NULL,
    open_price NUMERIC NOT NULL,
    high_price NUMERIC NOT NULL,
    low_price NUMERIC NOT NULL,
    close_price NUMERIC NOT NULL,
    volume INTEGER,
    adjusted_close NUMERIC,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 10. Pre-Computed Financial Ratios (KPI Engine Backbone)
CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER,
    company_id VARCHAR(12) NOT NULL,
    year VARCHAR(7) NOT NULL,
    net_profit_margin_pct NUMERIC,
    operating_profit_margin_pct NUMERIC,
    return_on_equity_pct NUMERIC,
    debt_to_equity NUMERIC,
    interest_coverage NUMERIC,
    asset_turnover NUMERIC,
    free_cash_flow_cr NUMERIC,
    capex_cr NUMERIC,
    earnings_per_share NUMERIC,
    book_value_per_share NUMERIC,
    dividend_payout_ratio_pct NUMERIC,
    total_debt_cr NUMERIC,
    cash_from_operations_cr NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 11. Peer Comparison Cohorts
CREATE TABLE IF NOT EXISTS peer_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_group_name VARCHAR(100) NOT NULL,
    company_id VARCHAR(12) NOT NULL,
    is_benchmark BOOLEAN DEFAULT 0,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 12. Annual Valuation Multiples
CREATE TABLE IF NOT EXISTS market_cap (
    id INTEGER,
    company_id VARCHAR(12) NOT NULL,
    year INTEGER NOT NULL,
    market_cap_crore NUMERIC,
    enterprise_value_crore NUMERIC,
    pe_ratio NUMERIC,
    pb_ratio NUMERIC,
    ev_ebitda NUMERIC,
    dividend_yield_pct NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_pnl_company ON profitandloss(company_id);
CREATE INDEX IF NOT EXISTS idx_bs_company ON balancesheet(company_id);
CREATE INDEX IF NOT EXISTS idx_cf_company ON cashflow(company_id);
CREATE INDEX IF NOT EXISTS idx_ratios_company ON financial_ratios(company_id);
CREATE INDEX IF NOT EXISTS idx_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX IF NOT EXISTS idx_sectors_broad ON sectors(broad_sector);
CREATE INDEX IF NOT EXISTS idx_peers_group ON peer_groups(peer_group_name);
CREATE INDEX IF NOT EXISTS idx_docs_company_year ON documents(company_id, Year);
