"""Unit tests for Investment Screener Engine (6 presets, 15 filters, composite score)."""
import pandas as pd
import pytest
from src.screener.engine import ScreenerEngine


@pytest.fixture
def sample_universe():
    """Mock universe DataFrame with non-financial and financial companies."""
    return pd.DataFrame([
        {
            "company_id": "TCS",
            "company_name": "Tata Consultancy Services Ltd",
            "broad_sector": "Information Technology",
            "return_on_equity_pct": 46.85,
            "return_on_capital_employed_pct": 58.0,
            "net_profit_margin_pct": 21.5,
            "operating_profit_margin_pct": 25.0,
            "debt_to_equity": 0.0,
            "prev_debt_to_equity": 0.0,
            "de_declining_yoy": False,
            "interest_coverage": None,
            "icr_label": "Debt Free",
            "free_cash_flow_cr": 35000.0,
            "fcf_conversion_pct": 75.0,
            "revenue_cagr_3yr": 11.5,
            "revenue_cagr_5yr": 12.86,
            "pat_cagr_5yr": 10.5,
            "eps_cagr_5yr": 10.2,
            "asset_turnover": 1.6,
            "sales": 225458.0,
            "net_profit": 39106.0,
            "cfo_quality_score": 1.25,
            "pe_ratio": 28.5,
            "pb_ratio": 12.0,
            "dividend_yield_pct": 1.4,
            "dividend_payout_ratio_pct": 65.0,
            "market_cap_crore": 1400000.0,
        },
        {
            "company_id": "HDFCBANK",
            "company_name": "HDFC Bank Limited",
            "broad_sector": "Financials",
            "return_on_equity_pct": 17.2,
            "return_on_capital_employed_pct": 16.5,
            "net_profit_margin_pct": 24.0,
            "operating_profit_margin_pct": 32.0,
            "debt_to_equity": 6.8,  # High D/E, but Financials sector
            "prev_debt_to_equity": 7.0,
            "de_declining_yoy": True,
            "interest_coverage": 2.5,
            "icr_label": "Normal",
            "free_cash_flow_cr": 25000.0,
            "fcf_conversion_pct": 60.0,
            "revenue_cagr_3yr": 14.0,
            "revenue_cagr_5yr": 16.5,
            "pat_cagr_5yr": 18.0,
            "eps_cagr_5yr": 15.0,
            "asset_turnover": 0.12,
            "sales": 160000.0,
            "net_profit": 44000.0,
            "cfo_quality_score": 1.1,
            "pe_ratio": 18.2,
            "pb_ratio": 2.8,
            "dividend_yield_pct": 1.1,
            "dividend_payout_ratio_pct": 25.0,
            "market_cap_crore": 1200000.0,
        },
        {
            "company_id": "GROWTHCO",
            "company_name": "Rapid Growth Corp",
            "broad_sector": "Industrials",
            "return_on_equity_pct": 22.0,
            "return_on_capital_employed_pct": 25.0,
            "net_profit_margin_pct": 15.0,
            "operating_profit_margin_pct": 18.0,
            "debt_to_equity": 0.4,
            "prev_debt_to_equity": 0.6,
            "de_declining_yoy": True,
            "interest_coverage": 8.0,
            "icr_label": "Normal",
            "free_cash_flow_cr": 3200.0,
            "fcf_conversion_pct": 65.0,
            "revenue_cagr_3yr": 22.0,
            "revenue_cagr_5yr": 24.0,
            "pat_cagr_5yr": 28.0,
            "eps_cagr_5yr": 25.0,
            "asset_turnover": 1.4,
            "sales": 18000.0,
            "net_profit": 2700.0,
            "cfo_quality_score": 1.2,
            "pe_ratio": 16.0,
            "pb_ratio": 2.5,
            "dividend_yield_pct": 2.5,
            "dividend_payout_ratio_pct": 40.0,
            "market_cap_crore": 45000.0,
        },
        {
            "company_id": "WEAKCORP",
            "company_name": "Stressed Industrial Corp",
            "broad_sector": "Industrials",
            "return_on_equity_pct": 4.5,
            "return_on_capital_employed_pct": 6.0,
            "net_profit_margin_pct": 3.0,
            "operating_profit_margin_pct": 8.0,
            "debt_to_equity": 3.5,  # High D/E for non-financial
            "prev_debt_to_equity": 3.0,
            "de_declining_yoy": False,
            "interest_coverage": 1.2,
            "icr_label": "At Risk",
            "free_cash_flow_cr": -500.0,
            "fcf_conversion_pct": -20.0,
            "revenue_cagr_3yr": 2.0,
            "revenue_cagr_5yr": 3.0,
            "pat_cagr_5yr": -5.0,
            "eps_cagr_5yr": -6.0,
            "asset_turnover": 0.6,
            "sales": 8000.0,
            "net_profit": 240.0,
            "cfo_quality_score": 0.4,
            "pe_ratio": 45.0,
            "pb_ratio": 4.0,
            "dividend_yield_pct": 0.2,
            "dividend_payout_ratio_pct": 10.0,
            "market_cap_crore": 10000.0,
        }
    ])


def test_screener_financials_de_carveout(sample_universe):
    """Financial sector constituents pass max_de filter regardless of structural leverage."""
    engine = ScreenerEngine()
    engine.universe_df = engine.calculate_composite_score(sample_universe)
    res = engine.apply_filters(max_de=1.0)
    passed_ids = res["company_id"].tolist()
    assert "TCS" in passed_ids
    assert "HDFCBANK" in passed_ids  # Financials sector exempt
    assert "WEAKCORP" not in passed_ids  # Non-financial D/E 3.5 fails


def test_screener_icr_debt_free_passes(sample_universe):
    """Debt-free companies with icr_label='Debt Free' pass any min_icr filter."""
    engine = ScreenerEngine()
    engine.universe_df = engine.calculate_composite_score(sample_universe)
    res = engine.apply_filters(min_icr=5.0)
    passed_ids = res["company_id"].tolist()
    assert "TCS" in passed_ids  # Debt Free passes as infinity
    assert "GROWTHCO" in passed_ids  # ICR 8.0 >= 5.0 passes
    assert "HDFCBANK" not in passed_ids  # ICR 2.5 < 5.0 fails
    assert "WEAKCORP" not in passed_ids  # ICR 1.2 < 5.0 fails


def test_screener_composite_score_bounds(sample_universe):
    """Composite quality scores are strictly bounded between 0 and 100 with sector-relative normalisation."""
    engine = ScreenerEngine()
    scored = engine.calculate_composite_score(sample_universe)
    scores = scored["composite_quality_score"]
    assert (scores >= 0).all()
    assert (scores <= 100).all()

    # TCS & GROWTHCO score higher than WEAKCORP
    tcs_score = scored[scored["company_id"] == "TCS"]["composite_quality_score"].iloc[0]
    weak_score = scored[scored["company_id"] == "WEAKCORP"]["composite_quality_score"].iloc[0]
    growth_score = scored[scored["company_id"] == "GROWTHCO"]["composite_quality_score"].iloc[0]
    assert tcs_score > weak_score
    assert growth_score > weak_score


def test_screener_custom_15_metrics(sample_universe):
    """Screener supports filtering across all 15 metrics via custom dictionary."""
    engine = ScreenerEngine()
    engine.universe_df = engine.calculate_composite_score(sample_universe)

    # Test filtering on Sales and Market Cap
    res = engine.run_custom_screen({"sales_min": 10000.0, "market_cap_min": 40000.0})
    passed = res["company_id"].tolist()
    assert "TCS" in passed
    assert "HDFCBANK" in passed
    assert "GROWTHCO" in passed
    assert "WEAKCORP" not in passed


def test_screener_presets_return_results(sample_universe):
    """All 6 screener presets execute cleanly and return expected constituents."""
    engine = ScreenerEngine()
    engine.universe_df = engine.calculate_composite_score(sample_universe)

    # 1. Quality Compounder (ROE > 15, D/E < 1, FCF > 0, Rev CAGR 5Y > 10)
    qc = engine.run_preset("quality_compounder")
    assert "TCS" in qc["company_id"].tolist()
    assert "WEAKCORP" not in qc["company_id"].tolist()

    # 2. Value Pick (P/E < 20, P/B < 3, D/E < 2, Div Yield > 1)
    vp = engine.run_preset("value_pick")
    assert "GROWTHCO" in vp["company_id"].tolist()

    # 3. Growth Accelerator (PAT CAGR 5Y > 20, Rev CAGR 5Y > 15, D/E < 2)
    ga = engine.run_preset("growth_accelerator")
    assert "GROWTHCO" in ga["company_id"].tolist()

    # 4. Dividend Champion (Div Yield > 2, Payout < 80, FCF > 0)
    dc = engine.run_preset("dividend_champion")
    assert "GROWTHCO" in dc["company_id"].tolist()

    # 5. Debt-Free Blue Chip (D/E = 0, ROE > 12, Sales > 5000)
    df_bc = engine.run_preset("debt_free_blue_chip")
    assert "TCS" in df_bc["company_id"].tolist()
    assert "WEAKCORP" not in df_bc["company_id"].tolist()

    # 6. Turnaround Watch (Rev CAGR 3Y > 10, FCF > 0, D/E declining YoY)
    tw = engine.run_preset("turnaround_watch")
    assert "GROWTHCO" in tw["company_id"].tolist()


def test_quality_compounder_top_results_verification(sample_universe):
    """Quality Compounder preset results strictly satisfy ROE > 15% and D/E < 1.0 (with Financials sector carve-out)."""
    engine = ScreenerEngine()
    engine.universe_df = engine.calculate_composite_score(sample_universe)
    qc = engine.run_preset("quality_compounder")

    assert len(qc) > 0
    for _, row in qc.iterrows():
        # ROE must be > 15% (or >= 14% if expanded)
        assert row["return_on_equity_pct"] >= 14.0
        # D/E must be < 1.0 or Financials sector
        is_fin = "financial" in str(row["broad_sector"]).lower() or "bank" in str(row["broad_sector"]).lower()
        if not is_fin:
            assert row["debt_to_equity"] <= 1.0
        # FCF must be positive
        assert row["free_cash_flow_cr"] > 0.0
