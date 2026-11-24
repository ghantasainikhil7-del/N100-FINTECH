"""Unit tests for PDF report generation modules."""
import os
import pandas as pd
import pytest
from src.reports.portfolio_report import PortfolioReportGenerator
from src.reports.sector_report import SectorReportGenerator
from src.reports.tearsheet import TearsheetGenerator


def test_portfolio_trend_arrows():
    """Verify YoY trend arrow direction logic."""
    arrow_up, style_up = PortfolioReportGenerator._get_trend_arrow(120.0, 100.0)
    assert arrow_up == "↑"
    assert style_up == "ArrowUp"

    arrow_down, style_down = PortfolioReportGenerator._get_trend_arrow(80.0, 100.0)
    assert arrow_down == "↓"
    assert style_down == "ArrowDown"

    arrow_flat, style_flat = PortfolioReportGenerator._get_trend_arrow(101.0, 100.0, tolerance_pct=2.0)
    assert arrow_flat == "→"
    assert style_flat == "ArrowFlat"


def test_tearsheet_mock_generation(tmp_path):
    """Test generating a 2-page company tearsheet PDF."""
    generator = TearsheetGenerator(output_dir=str(tmp_path))

    df_pl = pd.DataFrame([
        {"year": f"202{i}-03", "sales": 10000.0 * (1.1**i), "net_profit": 2000.0 * (1.1**i)}
        for i in range(5)
    ])
    df_bs = pd.DataFrame([
        {"year": f"202{i}-03", "equity_capital": 500.0, "reserves": 5000.0, "borrowings": 1000.0, "other_liabilities": 2000.0}
        for i in range(5)
    ])
    df_cf = pd.DataFrame([
        {"year": f"202{i}-03", "operating_activity": 2500.0, "investing_activity": -800.0, "financing_activity": -500.0, "net_cash_flow": 1200.0}
        for i in range(5)
    ])
    df_ratios = pd.DataFrame([
        {"year": f"202{i}-03", "return_on_equity_pct": 25.0, "return_on_capital_employed_pct": 30.0, "debt_to_equity": 0.18, "free_cash_flow_cr": 1700.0}
        for i in range(5)
    ])

    pdf_path = generator.generate_tearsheet(
        ticker="TESTCO",
        co_meta={"company_name": "Test Corporation Ltd", "broad_sector": "Information Technology"},
        df_pl=df_pl,
        df_bs=df_bs,
        df_cf=df_cf,
        df_ratios=df_ratios,
        pros=["Consistently high ROE above 20%", "Robust positive free cash flow"],
        cons=["Competitive industry pricing headwinds"],
        cap_alloc_label="Reinvestor",
    )

    assert os.path.exists(pdf_path)
    file_size_kb = os.path.getsize(pdf_path) / 1024.0
    # Must be at least 30 KB
    assert file_size_kb >= 30.0
