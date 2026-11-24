# Nifty 100 Financial Intelligence Platform — Analyst User Guide (10 Pages)

**Document Version:** 1.0.0 · **Target Audience:** Equity Research Analysts & Platform Engineers  
**System Build:** Production-Grade Financial Intelligence Engine for 92 Nifty 100 Constituents  

---

## Page 1: Executive Platform Architecture
The N100 Financial Intelligence Platform delivers institutional fundamental research capabilities for all 92 constituents of the Nifty 100 universe.
- **12 Structured Ingestion Feeds:** Companies, P&L, Balance Sheet, Cash Flow, Financial Ratios, Market Cap, Sectors, Stock Prices, Peer Groups, Analysis, Pros & Cons, Documents.
- **Financial Ratio Engine:** 30+ standardized KPIs across profitability, leverage, growth, and cash flow.
- **Interactive Dashboard:** 8 Streamlit screens operating on sub-second cached queries.
- **RESTful API Server:** 16 FastAPI endpoints under `/api/v1` with OpenAPI 3.0 specification.
- **Automated Reporting:** 92 company tearsheets, 11 sector PDF intelligence reports, and master portfolio summary.

---

## Page 2: Data Foundation & ETL Pipeline
- **Ticker Normalization:** Leading/trailing whitespace stripped, capitalized to uppercase symbols (`normalize_ticker`).
- **Fiscal Period Standard:** Unified to `YYYY-03` format across 10-year histories (`normalize_year`).
- **Currency Standard:** All financial amounts recorded in INR Crore (₹ Cr).
- **16 Data Quality (DQ) Rules:** Strict validation covering primary key uniqueness, foreign key integrity, balance sheet balancing (Assets == Liabilities within 1%), OPM consistency, positive sales, and dividend payout caps.

---

## Page 3: Financial Ratio Engine & Domain Carve-Outs
- **Profitability:** Net Profit Margin, Return on Equity (ROE), Return on Capital Employed (ROCE), Return on Assets (ROA).
- **Leverage & Solvency:** Debt-to-Equity (D/E), Interest Coverage Ratio (ICR), Net Debt.
- **Bank Leverage Carve-Out:** For the 19 companies classified under `Financials`, high leverage is structurally normal. Standard maximum D/E thresholds are automatically bypassed to prevent false-negative insolvency alerts.
- **Debt-Free Labeling:** If Interest Expense = 0, ICR displays as `'Debt Free'` and automatically satisfies any minimum ICR requirement.

---

## Page 4: CAGR Growth Engine & 6 Mathematical Edge Cases
Compound Annual Growth Rates are evaluated over 3, 5, and 10-year windows:
1. **Positive to Positive:** Standard CAGR formula applied.
2. **Decline to Loss:** `DECLINE_TO_LOSS` flag assigned; value returns `None`.
3. **Turnaround:** `TURNAROUND` flag assigned; value returns `None`.
4. **Both Negative:** `BOTH_NEGATIVE` flag assigned; value returns `None`.
5. **Zero Base:** `ZERO_BASE` flag assigned; value returns `None`.
6. **Insufficient History:** `INSUFFICIENT` flag assigned (< N years of data).

---

## Page 5: Cash Flow Intelligence & Allocation Matrix
- **5-Year CFO Quality Score:** Ratio of $\frac{\text{CFO}}{\text{PAT}}$:
  - High Quality (> 1.0)
  - Moderate (0.5 to 1.0)
  - Accrual Risk (< 0.5)
- **CapEx Intensity:** $\frac{|\text{CFI}|}{\text{Sales}} \times 100$:
  - Asset Light (< 3%)
  - Moderate (3% to 8%)
  - Capital Intensive (> 8%)
- **Distress Signals:** Flagged when $\text{CFO} < 0 \land \text{CFF} > 0$ in latest fiscal year.
- **8 Capital Allocation Patterns:** (+,-,-) Reinvestor, (+,-,-) Shareholder Returns, (+,+,-) Liquidating Assets, (-,+,+) Distress Signal, (-,-,+) Growth Funded by Debt, (+,+,+) Cash Accumulator, (-,-,-) Pre-Revenue, (+,-,+) Mixed.

---

## Page 6: Investment Screener & 6 Institutional Presets
1. **Quality Compounder:** ROE > 15%, D/E < 1.0, FCF > 0, Rev CAGR > 10%.
2. **Value Pick:** P/E < 20x, P/B < 3.0x, D/E < 2.0, Div Yield > 1%.
3. **Growth Accelerator:** PAT CAGR > 20%, Rev CAGR > 15%, D/E < 2.0.
4. **Dividend Champion:** Div Yield > 2%, Payout < 80%, FCF > 0.
5. **Debt-Free Blue Chip:** D/E = 0, ROE > 12%, Sales > ₹5,000 Cr.
6. **Turnaround Watch:** Rev CAGR > 10%, FCF positive, declining leverage.

---

## Page 7: Streamlit Dashboard Navigation (8 Screens)
Run command: `streamlit run src/dashboard/app.py`
- `01_home.py`: Universal overview, 6 KPI tiles, sector donut, top compounders.
- `02_profile.py`: Search company, 6 KPI tiles, 10-year Revenue & PAT charts, Pros & Cons badges.
- `03_screener.py`: 10 interactive sliders, 6 presets, live results count, CSV export.
- `04_peers.py`: 11 peer groups with Plotly Scatterpolar radar charts.
- `05_trends.py`: Multi-metric historical overlay with YoY growth annotations.
- `06_sectors.py`: Sector bubble chart and median benchmark bar charts.
- `07_capital.py`: 8-archetype capital allocation treemap.
- `08_reports.py`: Annual report links and one-click tearsheet PDF downloads.

---

## Page 8: RESTful API Integration & cURL Examples
Run command: `uvicorn src.api.main:app --port 8000`
- **Health Check:** `curl -X GET http://localhost:8000/api/v1/health`
- **Company Profile:** `curl -X GET http://localhost:8000/api/v1/companies/TCS`
- **P&L History:** `curl -X GET http://localhost:8000/api/v1/companies/TCS/pl`
- **Screener Filter:** `curl -X GET "http://localhost:8000/api/v1/screener?min_roe=15&max_de=1.0"`
- **Tearsheet Download:** `curl -O http://localhost:8000/api/v1/companies/TCS/tearsheet`

---

## Page 9: Automated Report Generation
- **92 Company Tearsheets:** 2-page publication-grade executive summaries (`reports/tearsheets/`).
- **11 Sector Reports:** Median benchmarks and constituent tables (`reports/sector/`).
- **Master Portfolio Summary:** One page per company with trend arrows (`reports/portfolio/portfolio_summary.pdf`).
- **Execution:** `python -m src.reports.run_sprint5` or `make report`.

---

## Page 10: Troubleshooting & FAQ
- **Q: Database empty?** Run `make load` to load all Excel files and validate DQ rules.
- **Q: How to run tests?** Run `pytest tests/ -v` or `make test`. (68 tests passing).
- **Q: Custom Screener Export?** Use the download button on the Screener screen or access `output/screener_output.xlsx`.
