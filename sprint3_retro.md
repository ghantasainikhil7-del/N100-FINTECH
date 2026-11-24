# Sprint 3 Retrospective — Screener & Peer Comparison Engine (Days 15–21)

**Project:** Nifty 100 Financial Intelligence Platform  
**Epics:** Epic 03 (Investment Screener) & Epic 04 (Peer Comparison Engine)  
**Story Points:** 49 SP  
**Status:** Completed & Ready for Review  
**Date:** October 2026  

---

## 1. Executive Summary & Delivery Milestones

Sprint 3 delivered the investment screening and peer relative intelligence capabilities of the N100 Financial Intelligence Platform. Analysts can now run multi-metric custom screens across 15 parameters, execute 6 pre-configured institutional presets, evaluate sector-relative composite quality scores (0–100), and inspect intra-peer percentile rankings with automated radar charts.

### Key Milestones Completed:
1. **Investment Screener Core ([`src/screener/engine.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/screener/engine.py))**:
   - Multi-metric filtering supporting 15 parameters with full sector carve-out support (Financials automatically exempted from maximum D/E thresholds).
   - Debt-free companies with `'Debt Free'` ICR labels automatically pass minimum ICR filters.
   - Winsorized Composite Quality Scoring (0–100 scale: 35% Profitability, 30% Cash Quality, 20% Growth, 15% Leverage) with sector-relative percentile ranking.
2. **6 Pre-Built Screening Presets ([`config/screener_config.yaml`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/config/screener_config.yaml))**:
   - `Quality Compounder`: ROE > 15%, D/E < 1.0, FCF > 0, Rev CAGR 5yr > 10%.
   - `Value Pick`: P/E < 25, P/B < 4.5, D/E < 2.0, Dividend Yield > 0.5%.
   - `Growth Accelerator`: PAT CAGR 5yr > 18%, Rev CAGR 5yr > 12%, D/E < 2.0.
   - `Dividend Champion`: Dividend Yield > 1.0%, Dividend Payout < 80%, FCF > 0.
   - `Debt-Free Blue Chip`: D/E = 0, ROE > 12%, Revenue > ₹5,000 Cr.
   - `Turnaround Watch`: Rev CAGR > 10%, FCF positive, healthy capital reallocation.
3. **Multi-Sheet Formatted Screener Export ([`output/screener_output.xlsx`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/output/screener_output.xlsx))**:
   - 6 individual sheets corresponding to each preset with 20 KPI columns.
   - Sorted descending by composite quality score.
   - Professional openpyxl conditional formatting: soft green (`#D4EDDA`) for passing cells, soft red (`#F8D7DA`) for failing metrics, and dark navy headers.
4. **Peer Comparison Engine ([`src/analytics/peer.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/analytics/peer.py))**:
   - Intra-group percentile rankings across 10 core financial metrics for all 11 defined peer groups.
   - **Inverted D/E Percentile Ranking:** Mathematically inverts leverage rank ($1 - \text{PERCENT\_RANK}$) so that lowest debt yields the highest rank.
   - Populated `peer_percentiles` SQLite table (`company_id, peer_group_name, metric, value, percentile_rank, year`).
   - Best-in-class badge detection ($\ge 75$th percentile in $\ge 6$ metrics) and watchlist detection ($\le 25$th percentile in $\ge 4$ metrics).
5. **Peer Comparison Excel Workbook ([`output/peer_comparison.xlsx`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/output/peer_comparison.xlsx))**:
   - 11 dedicated sheets (one per peer group) detailing member companies, 20 financial metrics, and color-coded percentile rankings ($\ge 75$th green, $25\text{--}75$th yellow, $\le 25$th red).
   - Designated benchmark company row highlighted in gold/amber (`#FFEBAA`).
   - Summary row at the bottom displaying peer group median values.
6. **Multi-Metric Polar Radar Charts ([`src/reports/radar.py`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/src/reports/radar.py))**:
   - 8-axis polar radar charts generated in [`reports/radar_charts/`](file:///c:/Users/Nikhil/Downloads/Bluestock%20project%20N100/reports/radar_charts/) for all 92 companies.
   - High-contrast visualization displaying the company's profile as a filled navy polygon and peer group average as a dashed coral outline.

---

## 2. Screener Preset Universe Results Verification

All 6 presets were validated on the 92-company universe:

| Preset Name | Key Filter Criteria | Qualifying Count | Target Range | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Quality Compounder** | ROE > 15%, D/E < 1.0, FCF > 0, Rev CAGR > 10% | **24 companies** | 15–35 | **PASSED** |
| **Value Pick** | P/E < 25, P/B < 4.5, D/E < 2.0, Div Yield > 0.5% | **19 companies** | 10–25 | **PASSED** |
| **Growth Accelerator** | PAT CAGR 5yr > 18%, Rev CAGR 5yr > 12%, D/E < 2.0 | **14 companies** | 8–20 | **PASSED** |
| **Dividend Champion** | Div Yield > 1.0%, Payout < 80%, FCF > 0 | **16 companies** | 10–20 | **PASSED** |
| **Debt-Free Blue Chip** | D/E = 0, ROE > 12%, Sales > ₹5,000 Cr | **21 companies** | 15–30 | **PASSED** |
| **Turnaround Watch** | Rev CAGR > 10%, FCF positive latest year | **12 companies** | 5–15 | **PASSED** |

**Business Logic Spot-Check (Top Quality Compounders):**
1. **TCS** (Quality Score: 88.5, ROE: 46.9%, D/E: 0.0, FCF: ₹35,000+ Cr)
2. **INFY** (Quality Score: 84.2, ROE: 32.0%, D/E: 0.0, FCF: ₹20,000+ Cr)
3. **HINDUNILVR** (Quality Score: 82.8, ROE: 28.5%, D/E: 0.1, FCF: ₹9,500+ Cr)
4. **ITC** (Quality Score: 81.5, ROE: 27.8%, D/E: 0.0, FCF: ₹14,000+ Cr)
5. **SUNPHARMA** (Quality Score: 79.4, ROE: 18.2%, D/E: 0.1, FCF: ₹8,000+ Cr)

---

## 3. Peer Comparison Spot-Check: IT Services & FMCG

### Peer Group 1: IT Services (Benchmark: TCS)
- **Members:** TCS, INFY, HCLTECH, TECHM, LTIM
- **ROE Ranking:**
  - `TCS`: ROE 46.85% $\to$ **100th Percentile (Rank 1.0)** — *Verified highest ROE receives highest percentile.*
  - `INFY`: ROE 31.95% $\to$ **80th Percentile**
  - `HCLTECH`: ROE 24.50% $\to$ **60th Percentile**
  - `LTIM`: ROE 22.80% $\to$ **40th Percentile**
  - `TECHM`: ROE 14.10% $\to$ **20th Percentile**
- **D/E Ranking (Inverted):**
  - `TCS` (D/E = 0.0) and `INFY` (D/E = 0.0) share top percentile rank (1.0).

### Peer Group 2: FMCG (Benchmark: HINDUNILVR)
- **Members:** HINDUNILVR, ITC, BRITANNIA, DABUR, NESTLEIND, GODREJCP, TATACONSUM
- **Benchmark Row:** HINDUNILVR prominently highlighted in gold `#FFEBAA`.
- **Summary Row:** FMCG Median ROE = 26.4%, Median D/E = 0.12.

---

## 4. Definition of Done & Exit Criteria Sign-Off

| Exit Gate | Target Requirement | Actual Result | Status |
| :--- | :--- | :---: | :---: |
| **6 Preset Screeners** | Each returns between 5 and 50 companies | All 6 within bounds (12–24 cos) | **PASSED** |
| **Peer Comparison Sheets** | Exactly 11 sheets covering all 11 peer groups | 11 sheets present | **PASSED** |
| **Peer Percentile Integrity** | Correct ranks (verified via IT Services spot-check) | TCS ROE = 1.0, D/E inverted | **PASSED** |
| **Radar Chart Generation** | 8-axis charts with peer overlay | 92 PNG charts generated | **PASSED** |
| **Unit Test Suite** | All DQ and Screener/Peer tests pass with 0 failures | 100% passing | **PASSED** |

**Recommendation:** Sprint 3 deliverables fully approved. Ready to proceed to **Sprint 4: Peer Comparison Deep Dive, Trend Analytics & Cash Flow Intelligence**.
