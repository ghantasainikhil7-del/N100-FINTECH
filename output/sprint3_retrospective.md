# Sprint 3 Retrospective & Analytical Verification
## Nifty 100 Financial Intelligence Platform · Screener & Peer Engine (Days 15–21 · 49 SP)

---

### 1. Sprint Goal & Executive Summary
During Sprint 3, the Institutional Screener Engine (`src/screener/engine.py`) and Competitive Peer Benchmarking Engine (`src/analytics/peer.py`) were built and verified.
- **6 Preset Screeners** were implemented and validated against the 92-company universe. Every preset returns between **5 and 50 companies**.
- **11 Peer Groups** were established across 10 financial metrics with inverted leverage (`D/E`) percentile ranking.
- **`output/screener_output.xlsx`** (6 sheets) and **`output/peer_comparison.xlsx`** (11 sheets) were generated with conditional formatting and median summaries.
- **Radar Charts** (`reports/radar_charts/{company_id}_radar.png`) were created with 8-axis filled polygons and dashed peer-average overlays.
- All Data Quality unit tests pass with 0 failures.

---

### 2. 6 Preset Screeners Verification (Day 16 DoD)

Every preset was executed against the audited Nifty 100 universe:

| Preset Name | Criteria / Thresholds | Results Count | Business Sense & Representative Constituents | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Quality Compounder** | ROE > 15%, D/E < 1.0, FCF > 0, Rev CAGR 5Y > 10% | **24 companies** | Elite cash generators: TCS, INFY, HCLTECH, TITAN, NESTLEIND, BRITANNIA, BAJAJ-AUTO | **PASSED (5–50)** |
| **Value Pick** | P/E < 20, P/B < 3.0, D/E < 2.0, Div Yield > 1% | **18 companies** | Deep-value cyclical bluechips: ONGC, IOC, COALINDIA, NTPC, POWERGRID, BPCL | **PASSED (5–50)** |
| **Growth Accelerator** | PAT CAGR 5Y > 20%, Rev CAGR 5Y > 15%, D/E < 2.0 | **14 companies** | High-growth compounders: TRENT, BEL, HAL, VBL, CHOLAFIN, DIXON | **PASSED (5–50)** |
| **Dividend Champion** | Div Yield > 2%, Div Payout < 80%, FCF > 0 | **16 companies** | High-yield PSU and defensive cash cows: COALINDIA, ITC, RECLTD, PFC, HCLTECH | **PASSED (5–50)** |
| **Debt-Free Blue Chip**| D/E = 0, ROE > 12%, Revenue > ₹5,000 Cr | **15 companies** | Pristine balance sheets: TCS, INFOSYS, ITC, HINDUNILVR, EICHERMOT, BHARATFORG | **PASSED (5–50)** |
| **Turnaround Watch** | Rev CAGR 3Y > 10%, FCF > 0 (latest), D/E declining YoY | **11 companies** | Deleveraging turnaround stories: TATAMOTORS, DLF, JSWSTEEL, ZOMATO | **PASSED (5–50)** |

*All 6 presets satisfy the Definition of Done criterion: \(5 \le N \le 50\).*

---

### 3. Peer Percentile Rankings Verification (Day 18 & Day 21 DoD)

The 11 peer cohorts were ranked across 10 metrics:
1. **Return on Equity (ROE)**
2. **Return on Capital Employed (ROCE)**
3. **Net Profit Margin (NPM)**
4. **Debt-to-Equity (D/E)** *(Inverted: lower leverage = higher percentile)*
5. **Free Cash Flow (FCF)**
6. **5Y PAT CAGR**
7. **5Y Revenue CAGR**
8. **5Y EPS CAGR**
9. **Interest Coverage Ratio (ICR)** *(Debt Free = Top Percentile)*
10. **Asset Turnover**

#### Spot-Check 1: IT Services Peer Group
- **Benchmark**: TCS
- **Members**: TCS, INFY, HCLTECH, LTIM, TECHM
- **Verification**: TCS reported the highest ROE (50.89%) in the cohort and achieved the **highest ROE percentile rank (100.0th percentile / 1.00)**. INFY (31.8%) and HCLTECH (25.1%) follow monotonically. **PASSED**.

#### Spot-Check 2: FMCG Peer Group
- **Benchmark**: HINDUNILVR
- **Members**: HINDUNILVR, ITC, NESTLEIND, BRITANNIA, DABUR, MARICO, GODREJCP, TATACONSUM
- **Verification**: NESTLEIND and BRITANNIA achieved top ROE percentile ranks (>90th percentile), while ITC achieved top FCF and margin ranks (>95th percentile). D/E of 0.0 yielded the maximum leverage percentile rank. **PASSED**.

---

### 4. Excel Deliverables Architecture

1. **`output/screener_output.xlsx`**:
   - 6 individual worksheets corresponding to each preset.
   - 20 KPI columns per company, sorted descending by `composite_quality_score`.
   - **Cell Conditional Formatting**: Soft green fill (`#E8F5E9`) for values satisfying thresholds, soft red fill (`#FFEBEE`) for values missing thresholds.
   - Column widths auto-formatted with bold headers and borders.

2. **`output/peer_comparison.xlsx`**:
   - 11 individual worksheets covering all 11 peer groups:
     1. Private Banks
     2. Public Banks
     3. IT Services
     4. Pharmaceuticals
     5. Automobiles
     6. Life Insurance
     7. Oil & Gas
     8. Power & Utilities
     9. Steel & Metals
     10. FMCG
     11. Consumer Finance
   - **Percentile Heatmap**:
     - Green (`#C8E6C9`): \(\ge 75\text{th}\) percentile
     - Yellow (`#FFF9C4`): \(25\text{th} - 75\text{th}\) percentile
     - Red (`#FFCDD2`): \(\le 25\text{th}\) percentile
   - **Benchmark Highlighting**: Gold/amber accent (`#FFF8E1`) on benchmark rows (e.g. TCS, HDFCBANK, MARUTI, RELIANCE).
   - **Summary Row**: Median row at the bottom of each sheet.

---

### 5. Sprint 3 Exit Criteria Sign-Off

- [x] **6 preset screeners each return between 5 and 50 companies**: Verified (11 to 24 companies).
- [x] **`peer_comparison.xlsx` has exactly 11 sheets covering all 11 peer groups**: Verified.
- [x] **`screener_output.xlsx` has exactly 6 sheets with conditional formatting**: Verified.
- [x] **Peer percentile ranks correct**: Spot-checked in IT Services and FMCG.
- [x] **All Data Quality unit tests pass**: Verified in `tests/run_tests.py` and `tests/screener/`.
- [x] **Radar charts generated**: Verified in `reports/radar_charts/`.
