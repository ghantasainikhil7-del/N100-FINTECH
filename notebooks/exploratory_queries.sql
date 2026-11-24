-- ==============================================================================
-- NIFTY 100 FINANCIAL INTELLIGENCE PLATFORM
-- SPRINT 1: EXPLORATORY DATA QUALITY & FOUNDATION QUERIES (10 QUERIES)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 1: Total Companies & Sector Distribution
-- Purpose: Verify full 92 company universe and macro sector breakdown
-- ------------------------------------------------------------------------------
SELECT 
    s.broad_sector,
    COUNT(c.id) AS company_count,
    ROUND(SUM(s.index_weight_pct), 2) AS total_sector_weight_pct
FROM companies c
JOIN sectors s ON c.id = s.company_id
GROUP BY s.broad_sector
ORDER BY company_count DESC;

-- ------------------------------------------------------------------------------
-- Query 2: Annual Financial Statement History & Year Coverage per Company
-- Purpose: Verify years of available records across P&L, BS, and Cash Flow
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS company_id,
    c.company_name,
    COUNT(DISTINCT pl.year) AS pl_years,
    COUNT(DISTINCT bs.year) AS bs_years,
    COUNT(DISTINCT cf.year) AS cf_years,
    MIN(pl.year) AS earliest_year,
    MAX(pl.year) AS latest_year
FROM companies c
LEFT JOIN profitandloss pl ON c.id = pl.company_id
LEFT JOIN balancesheet bs ON c.id = bs.company_id
LEFT JOIN cashflow cf ON c.id = cf.company_id
GROUP BY c.id, c.company_name
ORDER BY pl_years ASC, c.id ASC;

-- ------------------------------------------------------------------------------
-- Query 3: Coverage Check — Companies with Less Than 5 Years of History (DQ-16)
-- Purpose: Identify newly listed companies or limited history constituents
-- ------------------------------------------------------------------------------
SELECT 
    c.id,
    c.company_name,
    s.broad_sector,
    COUNT(DISTINCT pl.year) AS years_available
FROM companies c
JOIN sectors s ON c.id = s.company_id
LEFT JOIN profitandloss pl ON c.id = pl.company_id
GROUP BY c.id, c.company_name, s.broad_sector
HAVING years_available < 5
ORDER BY years_available ASC;

-- ------------------------------------------------------------------------------
-- Query 4: Top 10 Profit Making Companies (Latest Available Year)
-- Purpose: Verify net profit figures and rankings across the universe
-- ------------------------------------------------------------------------------
SELECT 
    pl.company_id,
    c.company_name,
    s.broad_sector,
    pl.year,
    pl.sales,
    pl.net_profit,
    ROUND((pl.net_profit / pl.sales) * 100, 2) AS npm_pct
FROM profitandloss pl
JOIN companies c ON pl.company_id = c.id
JOIN sectors s ON c.id = s.company_id
WHERE pl.year = (SELECT MAX(year) FROM profitandloss)
ORDER BY pl.net_profit DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 5: Debt-Free Companies Screening (Zero Borrowings)
-- Purpose: List companies with zero borrowings in latest balance sheet
-- ------------------------------------------------------------------------------
SELECT 
    bs.company_id,
    c.company_name,
    s.broad_sector,
    bs.year,
    bs.equity_capital + bs.reserves AS total_equity,
    bs.borrowings
FROM balancesheet bs
JOIN companies c ON bs.company_id = c.id
JOIN sectors s ON c.id = s.company_id
WHERE bs.year = (SELECT MAX(year) FROM balancesheet)
  AND (bs.borrowings = 0 OR bs.borrowings IS NULL)
ORDER BY total_equity DESC;

-- ------------------------------------------------------------------------------
-- Query 6: Cash Flow Integrity & Operating Cash Flow Leaders
-- Purpose: Validate operating cash flow vs net profit (accrual quality)
-- ------------------------------------------------------------------------------
SELECT 
    cf.company_id,
    c.company_name,
    cf.year,
    cf.operating_activity AS cfo,
    pl.net_profit AS pat,
    ROUND(cf.operating_activity / NULLIF(pl.net_profit, 0), 2) AS cfo_to_pat_ratio,
    cf.net_cash_flow
FROM cashflow cf
JOIN profitandloss pl ON cf.company_id = pl.company_id AND cf.year = pl.year
JOIN companies c ON cf.company_id = c.id
WHERE cf.year = (SELECT MAX(year) FROM cashflow)
  AND cf.operating_activity > 0
ORDER BY cf.operating_activity DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 7: Balance Sheet Balance Verification (DQ-04 & DQ-15 Audit)
-- Purpose: Verify asset and liability balance tolerance (< 1%)
-- ------------------------------------------------------------------------------
SELECT 
    bs.company_id,
    bs.year,
    bs.total_assets,
    bs.total_liabilities,
    ROUND(ABS(bs.total_assets - bs.total_liabilities), 2) AS diff,
    ROUND((ABS(bs.total_assets - bs.total_liabilities) / NULLIF(bs.total_assets, 0)) * 100, 4) AS diff_pct
FROM balancesheet bs
WHERE diff > 0.01
ORDER BY diff_pct DESC
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 8: Annual Report Document Repository Coverage & Missing Link Count
-- Purpose: Identify gaps in annual reports from BSE repository
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS company_id,
    c.company_name,
    COUNT(d.id) AS total_documents_available,
    MIN(d.year) AS earliest_report_year,
    MAX(d.year) AS latest_report_year
FROM companies c
LEFT JOIN documents d ON c.id = d.company_id
GROUP BY c.id, c.company_name
ORDER BY total_documents_available ASC, c.id ASC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 9: Peer Group Benchmark Distribution
-- Purpose: Verify 11 peer groups and designated benchmark companies
-- ------------------------------------------------------------------------------
SELECT 
    pg.peer_group_name,
    COUNT(pg.company_id) AS total_members,
    MAX(CASE WHEN pg.is_benchmark = 1 THEN pg.company_id ELSE NULL END) AS benchmark_ticker
FROM peer_groups pg
GROUP BY pg.peer_group_name
ORDER BY total_members DESC;

-- ------------------------------------------------------------------------------
-- Query 10: Multi-Year Price History & Volatility Range (Simulated)
-- Purpose: Check price history date range and monthly coverage per company
-- ------------------------------------------------------------------------------
SELECT 
    sp.company_id,
    COUNT(sp.id) AS monthly_price_points,
    MIN(sp.date) AS start_date,
    MAX(sp.date) AS end_date,
    ROUND(MIN(sp.low_price), 2) AS historical_low,
    ROUND(MAX(sp.high_price), 2) AS historical_high,
    ROUND(AVG(sp.close_price), 2) AS avg_close
FROM stock_prices sp
GROUP BY sp.company_id
ORDER BY sp.company_id ASC
LIMIT 10;
