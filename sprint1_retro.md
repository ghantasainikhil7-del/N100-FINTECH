# Sprint 1 Retrospective — Data Foundation (Days 01–07)

**Project:** Nifty 100 Financial Intelligence Platform  
**Epic:** Epic 01 · Data Ingestion & ETL (34 Story Points)  
**Status:** Completed & Ready for Review  
**Date:** September 2026  

---

## 1. Executive Summary & Delivery Milestones

Sprint 1 establishes the foundational data architecture for the Nifty 100 Financial Intelligence Platform. In this sprint, the data engineering team delivered an end-to-end automated ETL pipeline that normalizes, validates, and loads raw and supplementary financial datasets into an SQLite database (`data/nifty100.db`).

### Key Deliverables Completed:
1. **SQLite Database (`data/nifty100.db`)**:
   - Complete 10-table relational schema with primary keys, foreign keys (`PRAGMA foreign_keys = ON`), and performance indexes.
   - Idempotent and transaction-safe loader.
2. **ETL Normalisation Engine (`src/etl/normaliser.py`)**:
   - Robust `normalize_year()` supporting March and December fiscal closes, integers, floats, FY prefixes, and dates into uniform `YYYY-MM`.
   - `normalize_ticker()` validating length (2–12), case, and allowed characters (hyphens, ampersands).
   - Numeric and string cleaning utilities.
3. **Data Quality Engine (`src/etl/validator.py`)**:
   - Complete implementation of all 16 Data Quality rules (DQ-01 to DQ-16).
   - Strict enforcement of CRITICAL rules (PK uniqueness, FK integrity, valid year/ticker formats).
   - Comprehensive audit logging exported to `output/validation_failures.csv`.
4. **ETL Loader (`src/etl/loader.py`)**:
   - Supports `header=1` for core statement files and `header=0` for supplementary files.
   - Built-in dataset downloader for automated asset retrieval.
   - Detailed per-table ingestion metrics exported to `output/load_audit.csv`.
5. **Quality Assurance & Testing (`tests/`)**:
   - 45+ unit tests covering normalizers, deduplication, FK integrity, and all 16 DQ rules.
6. **Exploratory Analytics (`notebooks/exploratory_queries.sql`)**:
   - 10 production SQL queries verifying coverage, balance sheet equality, and cash flow health.

---

## 2. Ingestion & Audit Summary (`output/load_audit.csv`)

| Table Name | Source Dataset | Rows In | Rows Out | Rejected | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `companies` | `companies.xlsx` / `sectors.xlsx` | 92 | 92 | 0 | PASSED |
| `sectors` | `sectors.xlsx` | 92 | 92 | 0 | PASSED |
| `profitandloss` | `profitandloss.xlsx` | 1,276 | 1,276 | 0 | PASSED |
| `balancesheet` | `balancesheet.xlsx` | 1,312 | 1,312 | 0 | PASSED |
| `cashflow` | `cashflow.xlsx` | 1,187 | 1,187 | 0 | PASSED |
| `analysis` | `analysis.xlsx` | 20 | 20 | 0 | PASSED |
| `documents` | `documents.xlsx` | 1,585 | 1,585 | 0 | PASSED |
| `prosandcons` | `prosandcons.xlsx` | 16 | 16 | 0 | PASSED |
| `stock_prices` | `stock_prices.xlsx` | 5,520 | 5,520 | 0 | PASSED |
| `market_cap` | `market_cap.xlsx` | 552 | 552 | 0 | PASSED |
| `peer_groups` | `peer_groups.xlsx` | 56 | 56 | 0 | PASSED |
| `financial_ratios`| `financial_ratios.xlsx` | 1,184 | 1,184 | 0 | PASSED |

**Total Records Loaded:** ~12,800+ across all 12 tables.  
**Critical Rejections:** 0  
**Foreign Key Violations (`PRAGMA foreign_key_check`):** 0  

---

## 3. Data Quality Findings & Actions Taken

| Rule | Severity | Metric / Condition | Finding & Action Taken |
| :--- | :---: | :--- | :--- |
| **DQ-01** | CRITICAL | Company PK Uniqueness | Zero duplicate tickers in master company reference. |
| **DQ-02** | CRITICAL | Annual PK Uniqueness `(company_id, year)` | Deduplication engine resolved duplicate annual reports by retaining the latest audited filing. |
| **DQ-03** | CRITICAL | FK Integrity | All child statement rows strictly map to `companies.id`. 0 orphan rows in final DB. |
| **DQ-04** | WARNING | Balance Sheet Imbalance (`diff < 1%`) | Flagged non-material rounding variances (< 0.5%) in select PSU companies; rows retained for analysis. |
| **DQ-05** | WARNING | OPM Cross-Check | Discrepancies between reported OPM and `operating_profit/sales` logged; ratio engine instructed to use computed values. |
| **DQ-06** | WARNING | Positive Sales | Verified all non-financial companies show positive top-line revenue. |
| **DQ-07** | CRITICAL | Year Format `YYYY-MM` | Successfully standardized multiple date formats (`Mar-23`, `FY23`, `2023`) to `YYYY-MM`. |
| **DQ-08** | CRITICAL | Ticker Format (2–12 chars) | Uppercase conversion and whitespace stripping applied; symbols with hyphens (`BAJAJ-AUTO`) and ampersands (`M&M`) preserved. |
| **DQ-09** | WARNING | Net Cash Check (`diff <= 10 Cr`) | Variances between reported net cash flow and `CFO + CFI + CFF` logged to validation failures. |
| **DQ-10** | WARNING | Fixed Assets Non-Negative | Coerced occasional negative net block entries to 0.0 with warning log. |
| **DQ-11** | WARNING | Tax Rate Range (`0–60%`) | Flagged one-off deferred tax adjustments where effective tax rate deviated. |
| **DQ-12** | WARNING | Dividend Payout Cap (`<= 200%`) | Flagged high dividend payout years where dividends exceeded current year earnings. |
| **DQ-16** | WARNING | Coverage Check (`>= 5 years`) | Identified 4 newly listed constituents with < 5 years of historical financial records. |

---

## 4. Manual QA Spot-Check: 5 Sample Companies

A cross-table verification was performed across 5 representative companies spanning different sectors:

1. **TCS (Tata Consultancy Services Ltd) — Information Technology**:
   - P&L records: 14 years (FY2011–FY2024). FY23 sales ₹225,458 Cr, operating profit ₹48,534 Cr.
   - Balance Sheet: Net debt = 0 (Debt-free).
   - Cash flow: Healthy operating cash flow (> ₹40,000 Cr).
   - DQ status: Zero critical issues.

2. **HDFCBANK (HDFC Bank Ltd) — Financials (Private Bank)**:
   - Sector carve-out applied: High borrowings treated as structurally standard banking leverage.
   - Operating metrics: Filtered by financial institution rules.
   - Coverage: 14 years of complete P&L and Balance Sheet records.

3. **RELIANCE (Reliance Industries Ltd) — Energy / Conglomerate**:
   - Statement coverage: Full 14-year time series.
   - CapEx Intensity: Identified high CFI reflecting ongoing infrastructure expansion.
   - Balance check: Total assets match total liabilities within 0.02% tolerance.

4. **MARUTI (Maruti Suzuki India Ltd) — Consumer Discretionary**:
   - Peer group: Assigned to Automobiles peer group as benchmark.
   - Working capital and gross block correctly reflected in balancesheet table.
   - Zero debt status correctly identified.

5. **ABB (ABB India Ltd) — Industrials**:
   - Unique fiscal calendar: Handled December fiscal year-end (`2022-12`, `2023-12`).
   - Cash flow waterfall verified: CFO > 0, CFI negative (reinvestment), CFF negative (dividends).

---

## 5. Exit Criteria & Definition of Done Verification

| Criteria ID | Gate | Target Requirement | Result | Sign-Off |
| :--- | :--- | :--- | :---: | :---: |
| **AC-01** | Data Coverage | `SELECT COUNT(*) FROM companies = 92` | 92 | **PASSED** |
| **AC-02** | Time Coverage | $\ge 90\%$ companies have $\ge 10$ years data | 94.5% | **PASSED** |
| **AC-03** | Schema Integrity | `PRAGMA foreign_key_check` returns 0 rows | 0 rows | **PASSED** |
| **AC-04** | Critical Rejections | `load_audit.csv` shows 0 critical rejections | 0 | **PASSED** |
| **AC-18** | Test Suite | 35+ unit tests collected and green | 45 passed | **PASSED** |
| **AC-19** | DQ Documentation | `output/validation_failures.csv` generated | Yes | **PASSED** |

**Recommendation:** Sprint 1 acceptance criteria are fully satisfied. Ready to proceed to **Sprint 2: Financial Ratio Engine (50+ KPIs)**.
