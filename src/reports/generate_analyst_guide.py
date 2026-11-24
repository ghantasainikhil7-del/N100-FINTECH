"""Generator for docs/analyst_guide.pdf using ReportLab (10-Page Comprehensive Guide)."""
from __future__ import annotations

import logging
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

NAVY = colors.HexColor("#1B365D")
DARK_GRAY = colors.HexColor("#333333")
LIGHT_GRAY = colors.HexColor("#666666")
BORDER_COLOR = colors.HexColor("#D3D3D3")
CARD_BG = colors.HexColor("#F8F9FA")


def generate_analyst_guide(out_path: str = "docs/analyst_guide.pdf") -> str:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("DocTitle", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=NAVY, spaceAfter=8)
    h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=6)
    h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#2C3E50"), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13, textColor=DARK_GRAY, spaceAfter=6)
    code_style = ParagraphStyle("Code", fontName="Courier", fontSize=8, leading=11, textColor=colors.HexColor("#1E3A8A"), backColor=colors.HexColor("#EEF2F7"))

    story = []
    uw = 523

    # =========================================================================
    # PAGE 1: TITLE & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("Nifty 100 Financial Intelligence Platform", title_style))
    story.append(Paragraph("<b>Comprehensive User Manual & Technical Integration Guide</b>", ParagraphStyle("Sub", fontName="Helvetica", fontSize=12, leading=15, textColor=LIGHT_GRAY)))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=14))
    story.append(Paragraph("<b>Document Version:</b> 1.0.0 | <b>Target Audience:</b> Equity Research Analysts & Data Engineers", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Executive Platform Architecture", h1_style))
    story.append(Paragraph("""
    The N100 Financial Intelligence Platform provides enterprise-grade fundamental analytics for all 92 constituents of the Nifty 100 universe.
    Engineered with a robust 12-dataset ingestion pipeline, 30+ standardized KPIs, an institutional multi-metric screener,
    KMeans archetypal clustering, and automated ReportLab PDF generation, the platform accelerates qualitative and quantitative research.
    """, body_style))

    story.append(Paragraph("System Architecture Highlights:", h2_style))
    story.append(Paragraph("• <b>ETL Foundation:</b> 12 source files normalized with 16 rigorous Data Quality (DQ) validation gates.", body_style))
    story.append(Paragraph("• <b>Financial KPI Engine:</b> Profitability, leverage, growth, and cash flow formulas with special bank leverage carve-outs.", body_style))
    story.append(Paragraph("• <b>Interactive Dashboard:</b> 8 Streamlit screens operating on sub-second cached queries.", body_style))
    story.append(Paragraph("• <b>RESTful API:</b> 16 FastAPI endpoints providing JSON feeds, OpenAPI schemas, and binary downloads.", body_style))
    story.append(Paragraph("• <b>Automated Reports:</b> 92 company tearsheets, 11 sector PDF reports, and master portfolio summary.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: ETL & DATA QUALITY ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. Data Foundation & ETL Pipeline", h1_style))
    story.append(Paragraph("""
    The data layer extracts financial statements from 12 structured Excel datasets across a 10-year lookback period.
    The primary tables include companies, profitandloss, balancesheet, cashflow, sectors, market_cap, and financial_ratios.
    """, body_style))

    story.append(Paragraph("Data Normalization Standards:", h2_style))
    story.append(Paragraph("• <b>Company ID:</b> Tickers are trimmed of whitespace and uppercased (e.g. ' TCS ' -> 'TCS').", body_style))
    story.append(Paragraph("• <b>Fiscal Year:</b> Standardized to 'YYYY-03' format (e.g., 'Mar 2024', 'FY24' -> '2024-03').", body_style))
    story.append(Paragraph("• <b>Currency Units:</b> All values are consistently expressed in INR Crore (₹ Cr).", body_style))

    story.append(Paragraph("16 Data Quality (DQ) Rules Summary:", h2_style))
    dq_data = [
        [Paragraph("<b>Rule ID</b>", body_style), Paragraph("<b>Target Validation</b>", body_style), Paragraph("<b>Severity</b>", body_style)],
        [Paragraph("DQ-01 / 02", body_style), Paragraph("Primary Key Uniqueness & (Ticker, Year) Integrity", body_style), Paragraph("CRITICAL", body_style)],
        [Paragraph("DQ-03", body_style), Paragraph("Foreign Key referential integrity to companies table", body_style), Paragraph("CRITICAL", body_style)],
        [Paragraph("DQ-04", body_style), Paragraph("Balance Sheet Equation (Assets == Liabilities within 1%)", body_style), Paragraph("WARNING", body_style)],
        [Paragraph("DQ-05", body_style), Paragraph("Operating Profit Margin cross-check vs. reported OPM", body_style), Paragraph("WARNING", body_style)],
        [Paragraph("DQ-06", body_style), Paragraph("Positive Sales revenue validation", body_style), Paragraph("WARNING", body_style)],
    ]
    t = Table(dq_data, colWidths=[uw*0.2, uw*0.6, uw*0.2])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), CARD_BG), ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR), ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR)]))
    story.append(t)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: FINANCIAL RATIO ENGINE & BANK CARVE-OUTS
    # =========================================================================
    story.append(Paragraph("3. Financial Ratio Engine Methodology", h1_style))
    story.append(Paragraph("""
    The financial ratio engine computes 30+ standardized KPIs across profitability, leverage, growth, and cash flow quality.
    Specific domain adaptations are applied to accommodate unique sector characteristics.
    """, body_style))

    story.append(Paragraph("Core Ratio Formulas:", h2_style))
    story.append(Paragraph("• <b>Net Profit Margin:</b> (Net Profit / Sales) * 100. Returns None if Sales = 0.", body_style))
    story.append(Paragraph("• <b>Return on Equity (ROE):</b> (Net Profit / (Equity Capital + Reserves)) * 100. Returns None if Net Worth <= 0.", body_style))
    story.append(Paragraph("• <b>Return on Capital Employed (ROCE):</b> EBIT / (Equity + Reserves + Borrowings) * 100.", body_style))
    story.append(Paragraph("• <b>Debt-to-Equity (D/E):</b> Borrowings / Net Worth. Returns 0.0 for debt-free companies.", body_style))
    story.append(Paragraph("• <b>Interest Coverage Ratio (ICR):</b> (Operating Profit + Other Income) / Interest Expense. Returns 'Debt Free' label if Interest = 0.", body_style))
    story.append(Paragraph("• <b>Free Cash Flow (FCF):</b> Operating Cash Flow + Investing Cash Flow (Capex).", body_style))

    story.append(Paragraph("Banking & Financial Sector Carve-Out:", h2_style))
    story.append(Paragraph("""
    For the 19 companies classified under the 'Financials' broad sector (private banks, public banks, NBFCs, insurance),
    customer deposits and borrowing represent operating inventory rather than industrial debt.
    Consequently, maximum D/E thresholds are automatically bypassed for Financials to avoid false-positive insolvency warnings.
    """, body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CAGR ENGINE & EDGE CASES
    # =========================================================================
    story.append(Paragraph("4. CAGR Growth Engine & 6 Edge Cases", h1_style))
    story.append(Paragraph("""
    Compound Annual Growth Rates (CAGR) are computed over 3-year, 5-year, and 10-year rolling windows for Revenue, Net Profit (PAT), and EPS.
    Because standard exponential CAGR formulas fail mathematically when starting or ending values are negative or zero,
    the platform implements a robust 6-state edge case handler.
    """, body_style))

    cagr_table = [
        [Paragraph("<b>Scenario</b>", body_style), Paragraph("<b>Condition</b>", body_style), Paragraph("<b>Assigned Flag</b>", body_style), Paragraph("<b>Reported Value</b>", body_style)],
        [Paragraph("Positive to Positive", body_style), Paragraph("Start > 0 and End > 0", body_style), Paragraph("NORMAL", body_style), Paragraph("Computed CAGR %", body_style)],
        [Paragraph("Decline to Loss", body_style), Paragraph("Start > 0 and End <= 0", body_style), Paragraph("DECLINE_TO_LOSS", body_style), Paragraph("None", body_style)],
        [Paragraph("Turnaround", body_style), Paragraph("Start <= 0 and End > 0", body_style), Paragraph("TURNAROUND", body_style), Paragraph("None", body_style)],
        [Paragraph("Both Negative", body_style), Paragraph("Start < 0 and End < 0", body_style), Paragraph("BOTH_NEGATIVE", body_style), Paragraph("None", body_style)],
        [Paragraph("Zero Base", body_style), Paragraph("Start == 0", body_style), Paragraph("ZERO_BASE", body_style), Paragraph("None", body_style)],
        [Paragraph("Insufficient History", body_style), Paragraph("Data points < N years", body_style), Paragraph("INSUFFICIENT", body_style), Paragraph("None", body_style)],
    ]
    t_cagr = Table(cagr_table, colWidths=[uw*0.25, uw*0.3, uw*0.25, uw*0.2])
    t_cagr.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), CARD_BG), ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR), ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR)]))
    story.append(t_cagr)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CASH FLOW INTELLIGENCE & CAPITAL ALLOCATION
    # =========================================================================
    story.append(Paragraph("5. Cash Flow Intelligence & Allocation Matrix", h1_style))
    story.append(Paragraph("""
    The cash flow intelligence module classifies operational earnings quality, capital expenditure aggression,
    and assigns each company to one of 8 capital allocation archetypes based on the sign of cash flows (+, -, -).
    """, body_style))

    story.append(Paragraph("1. CFO Quality Score:", h2_style))
    story.append(Paragraph("Computes the 5-year average ratio of CFO / PAT:", body_style))
    story.append(Paragraph("• <b>> 1.0 (High Quality):</b> Net income is fully backed by real cash realizations.", body_style))
    story.append(Paragraph("• <b>0.5 to 1.0 (Moderate):</b> Working capital delays absorb moderate cash.", body_style))
    story.append(Paragraph("• <b>< 0.5 (Accrual Risk):</b> Aggressive revenue recognition or rising inventory/receivables.", body_style))

    story.append(Paragraph("2. CapEx Intensity Tiers:", h2_style))
    story.append(Paragraph("• <b>< 3.0% (Asset Light):</b> Software, financial services, asset-light FMCG.", body_style))
    story.append(Paragraph("• <b>3.0% to 8.0% (Moderate):</b> Automotive assembly, pharmaceuticals.", body_style))
    story.append(Paragraph("• <b>> 8.0% (Capital Intensive):</b> Telecom infrastructure, power, steel.", body_style))

    story.append(Paragraph("3. Distress Signal Detection:", h2_style))
    story.append(Paragraph("Flagged when CFO < 0 AND CFF > 0 in the latest year. Indicates operations burn cash while external debt/equity finances survival.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: INVESTMENT SCREENER & PRESETS
    # =========================================================================
    story.append(Paragraph("6. Investment Screener & Pre-Built Templates", h1_style))
    story.append(Paragraph("""
    The screener module allows analysts to apply 18 configurable filters across profitability, valuation, and growth.
    It includes 6 pre-configured institutional templates:
    """, body_style))

    story.append(Paragraph("1. Quality Compounder:", h2_style))
    story.append(Paragraph("Filters for companies with ROE > 15%, D/E < 1.0, positive FCF, and 5Y Revenue CAGR > 10%.", body_style))

    story.append(Paragraph("2. Value Pick:", h2_style))
    story.append(Paragraph("Filters for P/E < 20x, P/B < 3.0x, D/E < 2.0, and Dividend Yield > 1.0%.", body_style))

    story.append(Paragraph("3. Growth Accelerator:", h2_style))
    story.append(Paragraph("Filters for 5Y PAT CAGR > 20%, 5Y Revenue CAGR > 15%, and manageable leverage D/E < 2.0.", body_style))

    story.append(Paragraph("4. Dividend Champion:", h2_style))
    story.append(Paragraph("Filters for Dividend Yield > 2.0%, Dividend Payout < 80%, and positive operational FCF.", body_style))

    story.append(Paragraph("5. Debt-Free Blue Chip:", h2_style))
    story.append(Paragraph("Filters for strictly zero borrowings (D/E = 0), ROE > 12%, and Sales > ₹5,000 Cr.", body_style))

    story.append(Paragraph("6. Turnaround Watch:", h2_style))
    story.append(Paragraph("Filters for 3Y Revenue CAGR > 10%, FCF turning positive in latest fiscal year, and declining D/E.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: STREAMLIT DASHBOARD USER GUIDE
    # =========================================================================
    story.append(Paragraph("7. Streamlit Dashboard Navigation Guide", h1_style))
    story.append(Paragraph("""
    The interactive dashboard runs on port 8501 (`streamlit run src/dashboard/app.py`).
    It contains 8 primary screens accessible via the left sidebar:
    """, body_style))

    story.append(Paragraph("• <b>Screen 1 (Home):</b> Universal index overview, sector donut chart, top compounders.", body_style))
    story.append(Paragraph("• <b>Screen 2 (Profile):</b> Company card, 6 KPI tiles, 10-year Revenue & Profit charts, Pros & Cons badges.", body_style))
    story.append(Paragraph("• <b>Screen 3 (Screener):</b> 10 interactive sliders, 6 preset buttons, live matching count, and CSV export.", body_style))
    story.append(Paragraph("• <b>Screen 4 (Peers):</b> 11 peer group selections with Plotly Scatterpolar radar charts and benchmark comparisons.", body_style))
    story.append(Paragraph("• <b>Screen 5 (Trends):</b> Multi-metric historical overlays with YoY growth annotations.", body_style))
    story.append(Paragraph("• <b>Screen 6 (Sectors):</b> Bubble map (Revenue vs ROE vs Market Cap) and median benchmark bar charts.", body_style))
    story.append(Paragraph("• <b>Screen 7 (Capital):</b> Interactive treemap of all 92 companies by capital allocation archetype.", body_style))
    story.append(Paragraph("• <b>Screen 8 (Reports):</b> Clickable BSE filing links and instant tearsheet PDF downloads.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: REST API INTEGRATION & CURL EXAMPLES
    # =========================================================================
    story.append(Paragraph("8. RESTful API Server & Integration", h1_style))
    story.append(Paragraph("""
    The FastAPI server (`uvicorn src.api.main:app --port 8000`) exposes 16 production endpoints under `/api/v1`.
    Automated interactive documentation is available at `http://localhost:8000/docs`.
    """, body_style))

    story.append(Paragraph("Sample API Invocations (cURL):", h2_style))
    story.append(Paragraph("1. Health Check:", body_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/health'", code_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Fetch Company Profile (TCS):", body_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/companies/TCS'", code_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3. Run Screener Query (ROE > 15%, Max D/E 1.0):", body_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/screener?min_roe=15&max_de=1.0'", code_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. Download Tearsheet PDF:", body_style))
    story.append(Paragraph("curl -O 'http://localhost:8000/api/v1/companies/TCS/tearsheet'", code_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: REPORT GENERATION (TEARSHEETS & SECTORS)
    # =========================================================================
    story.append(Paragraph("9. Automated Report Generation", h1_style))
    story.append(Paragraph("""
    The reporting engine utilizes ReportLab to generate publication-grade PDF documents with zero text overflow.
    """, body_style))

    story.append(Paragraph("Deliverables Generated:", h2_style))
    story.append(Paragraph("• <b>92 Company Tearsheets:</b> 2-page executive tearsheets in `reports/tearsheets/<TICKER>_tearsheet.pdf`.", body_style))
    story.append(Paragraph("• <b>11 Sector Reports:</b> Industry intelligence summaries in `reports/sector/<SECTOR>_report.pdf`.", body_style))
    story.append(Paragraph("• <b>Master Portfolio Summary:</b> One page per company in `reports/portfolio/portfolio_summary.pdf`.", body_style))

    story.append(Paragraph("Batch Execution Command:", h2_style))
    story.append(Paragraph("python -m src.reports.run_sprint5", code_style))
    story.append(Paragraph("Or via Makefile target: `make report`", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: TROUBLESHOOTING & COMMON ISSUES
    # =========================================================================
    story.append(Paragraph("10. Troubleshooting & FAQ", h1_style))
    story.append(Paragraph("""
    This section provides operational guidelines for resolving common issues.
    """, body_style))

    story.append(Paragraph("Q1: Missing database tables or zero rows returned?", h2_style))
    story.append(Paragraph("Run `make load` or `python -m src.etl.loader` to download raw files, initialize SQLite schema, and populate all 10 tables.", body_style))

    story.append(Paragraph("Q2: How are missing or anomalous pre-computed ratios handled?", h2_style))
    story.append(Paragraph("The platform prioritizes calculated values from the raw financial statements over third-party fields. Anomalies > 5% are logged to `output/ratio_edge_cases.log`.", body_style))

    story.append(Paragraph("Q3: How to run the automated regression test suite?", h2_style))
    story.append(Paragraph("Run `pytest tests/ -v` or `make test`. All 60+ tests should pass with 0 failures.", body_style))

    story.append(Paragraph("Q4: Port conflict on localhost:8000 or 8501?", h2_style))
    story.append(Paragraph("Specify alternate ports: `uvicorn src.api.main:app --port 8080` or `streamlit run src/dashboard/app.py --server.port 8502`.", body_style))

    doc.build(story)
    logger.info("Successfully generated 10-page analyst guide at %s", out_path)
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_analyst_guide()
