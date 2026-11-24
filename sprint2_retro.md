# Sprint 2 Retrospective — Financial Ratio Engine (Days 08–14)

**Project:** Nifty 100 Financial Intelligence Platform  
**Epic:** Epic 02 · Financial Ratio Engine (42 Story Points)  
**Status:** Completed & Ready for Review  
**Date:** September 2026  

---

## 1. Executive Summary & Delivery Milestones

Sprint 2 successfully implemented the comprehensive **Financial Ratio Engine** computing 50+ Key Performance Indicators (KPIs) across all 92 Nifty 100 constituents and 14 financial years. The computed metrics populate the `financial_ratios` SQLite table and power all downstream modules, including the multi-parameter screener, financial health score, and tearsheet reports.

### Key Milestones Delivered:
1. **Profitability & Returns Engine ([`src/analytics/ratios.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/ratios.py))**:
   - Net Profit Margin (NPM), Operating Profit Margin (OPM with ±1% source cross-check), Return on Equity (ROE), Return on Capital Employed (ROCE), and Return on Assets (ROA).
   - Strict edge case handling: zero sales returns `None`, negative equity returns `None`.
2. **Leverage & Efficiency Engine ([`src/analytics/ratios.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/ratios.py))**:
   - Debt-to-Equity (D/E) with Bank & NBFC carve-out suppressing false warnings on financial companies.
   - Interest Coverage Ratio (ICR): interest = 0 correctly displays `'Debt Free'`, and ICR < 1.5 triggers `'At Risk'` warning.
   - Net Debt, Asset Turnover, and Book Value Per Share calculations.
3. **CAGR Growth Engine ([`src/analytics/cagr.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/cagr.py))**:
   - Multi-period rolling CAGR (3Y, 5Y, 10Y) across Sales, PAT, and EPS.
   - All 6 edge cases handled cleanly: `NORMAL`, `DECLINE_TO_LOSS`, `TURNAROUND` (e.g. Tata Motors), `BOTH_NEGATIVE`, `ZERO_BASE`, and `INSUFFICIENT` (< 3yr/5yr history).
4. **Cash Flow & Capital Allocation ([`src/analytics/cashflow_kpis.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/cashflow_kpis.py))**:
   - Free Cash Flow (CFO + CFI), 5-year CFO Quality Score (`High Quality`, `Moderate`, `Accrual Risk`), CapEx Intensity, and FCF Conversion Rate.
   - 8-pattern Capital Allocation Classifier generating [`output/capital_allocation.csv`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/output/capital_allocation.csv).
5. **Orchestrator & Database Population ([`src/analytics/engine.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/engine.py))**:
   - Populated `financial_ratios` table in `data/nifty100.db` with 1,184+ company-year records.
   - Exported comprehensive [`output/ratio_edge_cases.log`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/output/ratio_edge_cases.log).
6. **Formula Unit Test Suite ([`tests/kpi/`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/tests/kpi/))**:
   - 32 pytest unit tests covering profitability, leverage, CAGR edge cases, and cash flow patterns (exceeding the required 20 tests).

---

## 2. Table Population & Data Integrity Audit

| Metric | Target Requirement | Actual Result | Status |
| :--- | :--- | :--- | :---: |
| **Total Rows in `financial_ratios`** | $\ge 1,100$ rows | **1,184 rows** | **PASSED** |
| **Companies Covered** | 92 Nifty 100 Companies | 92 / 92 (100%) | **PASSED** |
| **Years Covered** | FY 2011 to FY 2024 | 14 Financial Years | **PASSED** |
| **Mandatory KPI Columns Populated** | 14 columns | 18 columns populated | **PASSED** |
| **Zero Null-Only Columns** | No column completely null | All columns populated | **PASSED** |

---

## 3. Manual Spot-Check: 3 Companies (Difference < 0.1%)

A manual verification was conducted against source filings to validate formula accuracy:

### Company 1: TCS (Tata Consultancy Services Ltd) — FY2023
- **Reported Net Profit:** ₹39,106 Cr | **Total Equity (Equity + Reserves):** ₹90,424 Cr
  - **Manual ROE:** $\frac{39106}{90424} \times 100 = 43.25\%$
  - **Ratio Engine ROE:** **43.25%** | **Difference:** **0.00%** (Well within $\pm 0.1\%$ gate)
- **5-Year Sales History:** FY18 = ₹123,104 Cr, FY23 = ₹225,458 Cr
  - **Manual 5Y Sales CAGR:** $\left(\frac{225458}{123104}\right)^{1/5} - 1 = 12.86\%$
  - **Ratio Engine 5Y Sales CAGR:** **12.86%** | **Difference:** **0.00%**

### Company 2: INFY (Infosys Ltd) — FY2023
- **Reported Net Profit:** ₹24,095 Cr | **Total Equity:** ₹75,408 Cr
  - **Manual ROE:** $\frac{24095}{75408} \times 100 = 31.95\%$
  - **Ratio Engine ROE:** **31.95%** | **Difference:** **0.00%**
- **5-Year Sales History:** FY18 = ₹70,522 Cr, FY23 = ₹146,767 Cr
  - **Manual 5Y Sales CAGR:** $\left(\frac{146767}{70522}\right)^{1/5} - 1 = 15.79\%$
  - **Ratio Engine 5Y Sales CAGR:** **15.79%** | **Difference:** **0.00%**

### Company 3: RELIANCE (Reliance Industries Ltd) — FY2023
- **Reported Net Profit:** ₹66,702 Cr | **Total Equity:** ₹714,359 Cr
  - **Manual ROE:** $\frac{66702}{714359} \times 100 = 9.34\%$
  - **Ratio Engine ROE:** **9.34%** | **Difference:** **0.00%**
- **5-Year Sales History:** FY18 = ₹391,677 Cr, FY23 = ₹879,468 Cr
  - **Manual 5Y Sales CAGR:** $\left(\frac{879468}{391677}\right)^{1/5} - 1 = 17.56\%$
  - **Ratio Engine 5Y Sales CAGR:** **17.56%** | **Difference:** **0.00%**

---

## 4. Edge Case Resolution & Anomaly Documentation

All formula discrepancies and edge cases were logged to [`output/ratio_edge_cases.log`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/output/ratio_edge_cases.log):

1. **Pre-Computed ROE Anomaly in Source (`TCS 0.52`)**:
   - *Category:* `[DATA SOURCE ISSUE]`
   - *Finding:* In `companies.xlsx`, TCS was recorded with `roe_percentage = 0.52`, representing decimal notation ($0.52 \approx 52\%$) instead of percentage notation ($52.0\%$).
   - *Action:* Replaced with mathematically computed ROE ($46.85\%$) in `financial_ratios`.
2. **Bank & NBFC Carve-Out (19 Financial Companies)**:
   - *Category:* `[SECTOR CARVE-OUT]`
   - *Finding:* Banks (e.g. HDFCBANK, SBIN, ICICIBANK) and NBFCs (BAJFINANCE) operate with structural leverage > 5×.
   - *Action:* Suppressed `high_leverage_flag` and applied sector-relative ROCE benchmarks.
3. **Debt-Free Companies & Undefined ICR**:
   - *Category:* `[DEBT FREE]`
   - *Finding:* Companies with zero debt (e.g. TCS, INFY) have ₹0 interest expense, resulting in division by zero.
   - *Action:* `interest_coverage` numeric column stores `None`, and `icr_label` displays `'Debt Free'` instead of infinity.
4. **CAGR Turnaround Transitions**:
   - *Category:* `[CAGR ANOMALY]`
   - *Finding:* Companies transitioning from losses to profits (e.g. Tata Motors FY19 $\to$ FY24) cannot be computed with exponential formula without imaginary numbers.
   - *Action:* Handled via `TURNAROUND` flag and displayed as `'Turnaround ↑'`.

---

## 5. Screener Preview Verification

A sample screening query was executed on latest financial records:
- **Criteria:** `Return on Equity > 15%` AND `Debt-to-Equity < 1.0`
- **Result Count:** **28 companies** qualified (comfortably within the target gate of $15\text{--}50$ companies).
- **Representative Constituents:** TCS, INFY, HINDUNILVR, ITC, SUNPHARMA, TITAN, NESTLEIND, BRITANNIA, BAJAJ-AUTO.
- **Business Logic Assessment:** High-quality, debt-disciplined market leaders correctly identified.

---

## 6. Definition of Done & Exit Criteria Sign-Off

| Criteria Gate | Requirement | Actual Result | Status |
| :--- | :--- | :---: | :---: |
| **`financial_ratios` Rows** | $\ge 1,100$ rows | **1,184 rows** | **PASSED** |
| **KPI Column Completeness** | All 14 columns populated | 18 columns populated | **PASSED** |
| **KPI Formula Tests** | 20 unit tests with 0 failures | 32 passed, 0 failures | **PASSED** |
| **Manual Spot-Check** | 3 companies match manual Excel within 0.1% | 0.00% difference | **PASSED** |
| **`ratio_edge_cases.log`** | Documented anomalies with categories | Fully documented | **PASSED** |
| **Screener Preview** | $15 \le \text{Count} \le 50$ for ROE > 15%, D/E < 1 | 28 companies | **PASSED** |

**Conclusion:** Sprint 2 acceptance gates are 100% satisfied. The platform is ready for **Sprint 3: Investment Screener, Health Scoring & Sector Analytics**.
