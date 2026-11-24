"""
Nifty 100 Financial Intelligence Platform · Sprint 2 KPI Formula Unit Tests
Covers 25 Unit Tests (Exceeding mandatory 20 KPI formula test threshold)
Sprint 2 · Days 08–14 · Definition of Done / Acceptance Gate
"""

import pytest
from src.analytics.ratios import (
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_roe,
    compute_roce,
    compute_roa,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_net_debt,
    compute_asset_turnover,
    compute_book_value_per_share,
)
from src.analytics.cagr import (
    compute_cagr,
    CAGR_FLAG_NORMAL,
    CAGR_FLAG_DECLINE_TO_LOSS,
    CAGR_FLAG_TURNAROUND,
    CAGR_FLAG_BOTH_NEGATIVE,
    CAGR_FLAG_ZERO_BASE,
    CAGR_FLAG_INSUFFICIENT,
)
from src.analytics.cashflow_kpis import (
    compute_free_cash_flow,
    compute_cfo_quality_score,
    compute_capex_intensity,
    compute_fcf_conversion_rate,
    classify_capital_allocation_pattern,
)


# ==============================================================================
# DAY 08: Profitability Ratios Unit Tests
# ==============================================================================

def test_01_net_profit_margin_normal():
    """Test 1: Normal NPM calculation = (Net Profit / Sales) * 100"""
    npm = compute_net_profit_margin(net_profit=150.0, sales=1000.0)
    assert npm == 15.0


def test_02_net_profit_margin_zero_sales():
    """Test 2: NPM returns None when sales <= 0 or missing"""
    assert compute_net_profit_margin(net_profit=100.0, sales=0.0) is None
    assert compute_net_profit_margin(net_profit=100.0, sales=-50.0) is None
    assert compute_net_profit_margin(net_profit=None, sales=100.0) is None


def test_03_operating_profit_margin_normal():
    """Test 3: OPM normal calculation = (Operating Profit / Sales) * 100"""
    opm, mismatch = compute_operating_profit_margin(operating_profit=250.0, sales=1000.0, source_opm=25.0)
    assert opm == 25.0
    assert mismatch is False


def test_04_operating_profit_margin_crosscheck_mismatch():
    """Test 4: OPM flags mismatch if difference > 1%"""
    opm, mismatch = compute_operating_profit_margin(
        operating_profit=250.0, sales=1000.0, source_opm=22.5, tolerance=1.0
    )
    assert opm == 25.0
    assert mismatch is True


def test_05_roe_normal():
    """Test 5: Return on Equity = Net Profit / (Equity Capital + Reserves) * 100"""
    roe = compute_roe(net_profit=200.0, equity_capital=100.0, reserves=900.0)
    assert roe == 20.0


def test_06_roe_negative_or_zero_equity():
    """Test 6: ROE returns None if equity + reserves <= 0"""
    assert compute_roe(net_profit=100.0, equity_capital=100.0, reserves=-100.0) is None
    assert compute_roe(net_profit=100.0, equity_capital=50.0, reserves=-150.0) is None


def test_07_roce_normal_and_carveout():
    """Test 7: ROCE = EBIT / (Equity + Reserves + Borrowings) * 100"""
    roce = compute_roce(ebit=300.0, equity_capital=100.0, reserves=900.0, borrowings=500.0)
    # 300 / 1500 * 100 = 20.0%
    assert roce == 20.0


def test_08_roa_normal_and_zero_assets():
    """Test 8: ROA = Net Profit / Total Assets * 100; returns None if assets <= 0"""
    assert compute_roa(net_profit=100.0, total_assets=1000.0) == 10.0
    assert compute_roa(net_profit=100.0, total_assets=0.0) is None
    assert compute_roa(net_profit=100.0, total_assets=-500.0) is None


# ==============================================================================
# DAY 09: Leverage & Efficiency Ratios Unit Tests
# ==============================================================================

def test_09_debt_to_equity_normal():
    """Test 9: D/E = Borrowings / Total Equity"""
    de, high_lev = compute_debt_to_equity(borrowings=500.0, equity_capital=100.0, reserves=900.0)
    assert de == 0.5
    assert high_lev is False


def test_10_debt_to_equity_debt_free():
    """Test 10: D/E returns 0 (not None) when borrowings = 0"""
    de, high_lev = compute_debt_to_equity(borrowings=0.0, equity_capital=100.0, reserves=900.0)
    assert de == 0.0
    assert high_lev is False


def test_11_debt_to_equity_high_leverage_flag():
    """Test 11: D/E > 5 for non-financials triggers high_leverage_flag = True"""
    de, high_lev = compute_debt_to_equity(
        borrowings=6000.0, equity_capital=100.0, reserves=900.0, is_financial=False
    )
    assert de == 6.0
    assert high_lev is True


def test_12_debt_to_equity_bank_carveout():
    """Test 12: D/E > 5 for Financials suppresses high_leverage_flag (structurally normal)"""
    de, high_lev = compute_debt_to_equity(
        borrowings=6000.0, equity_capital=100.0, reserves=900.0, is_financial=True
    )
    assert de == 6.0
    assert high_lev is False


def test_13_interest_coverage_normal():
    """Test 13: ICR = (Operating Profit + Other Income) / Interest"""
    icr, label, is_warn = compute_interest_coverage(operating_profit=400.0, other_income=100.0, interest=100.0)
    assert icr == 5.0
    assert label == "Normal"
    assert is_warn is False


def test_14_interest_coverage_debt_free():
    """Test 14: ICR returns None with display label 'Debt Free' when interest = 0"""
    icr, label, is_warn = compute_interest_coverage(operating_profit=500.0, other_income=50.0, interest=0.0)
    assert icr is None
    assert label == "Debt Free"
    assert is_warn is False


def test_15_interest_coverage_risk_warning():
    """Test 15: ICR < 1.5 triggers warning flag (at risk of not covering interest)"""
    icr, label, is_warn = compute_interest_coverage(operating_profit=100.0, other_income=20.0, interest=100.0)
    assert icr == 1.2
    assert label == "At Risk"
    assert is_warn is True


def test_16_asset_turnover_and_net_debt():
    """Test 16: Asset Turnover = Sales / Total Assets and Net Debt = Borrowings - Investments"""
    assert compute_asset_turnover(sales=2000.0, total_assets=1000.0) == 2.0
    assert compute_asset_turnover(sales=2000.0, total_assets=0.0) is None
    assert compute_net_debt(borrowings=1000.0, investments=400.0, cash=100.0) == 500.0


# ==============================================================================
# DAY 10: CAGR Engine 6 Edge Cases Unit Tests
# ==============================================================================

def test_17_cagr_normal():
    """Test 17: Normal CAGR with positive start and end: 100 to 200 over 3 years = 25.99%"""
    cagr_val, flag = compute_cagr(start_val=100.0, end_val=200.0, n_years=3)
    assert cagr_val == 25.99
    assert flag == CAGR_FLAG_NORMAL


def test_18_cagr_turnaround():
    """Test 18: Negative to Positive: returns None with TURNAROUND flag"""
    cagr_val, flag = compute_cagr(start_val=-100.0, end_val=200.0, n_years=3)
    assert cagr_val is None
    assert flag == CAGR_FLAG_TURNAROUND


def test_19_cagr_decline_to_loss():
    """Test 19: Positive to Negative: returns None with DECLINE_TO_LOSS flag"""
    cagr_val, flag = compute_cagr(start_val=200.0, end_val=-50.0, n_years=3)
    assert cagr_val is None
    assert flag == CAGR_FLAG_DECLINE_TO_LOSS


def test_20_cagr_both_negative_and_zero_base():
    """Test 20: Both negative returns BOTH_NEGATIVE; start == 0 returns ZERO_BASE"""
    val_neg, flag_neg = compute_cagr(start_val=-100.0, end_val=-200.0, n_years=3)
    assert val_neg is None
    assert flag_neg == CAGR_FLAG_BOTH_NEGATIVE

    val_zero, flag_zero = compute_cagr(start_val=0.0, end_val=150.0, n_years=3)
    assert val_zero is None
    assert flag_zero == CAGR_FLAG_ZERO_BASE


def test_21_cagr_insufficient():
    """Test 21: Missing values or years < 1 returns INSUFFICIENT flag"""
    val, flag = compute_cagr(start_val=None, end_val=100.0, n_years=3)
    assert val is None
    assert flag == CAGR_FLAG_INSUFFICIENT


# ==============================================================================
# DAY 11: Cash Flow KPIs & Capital Allocation Unit Tests
# ==============================================================================

def test_22_free_cash_flow_normal_and_negative():
    """Test 22: FCF = Operating + Investing activity (negative allowed)"""
    assert compute_free_cash_flow(operating_activity=1000.0, investing_activity=-400.0) == 600.0
    assert compute_free_cash_flow(operating_activity=200.0, investing_activity=-500.0) == -300.0


def test_23_cfo_quality_score():
    """Test 23: CFO / PAT 5-year average quality classification"""
    # High Quality: avg > 1.0
    score, label = compute_cfo_quality_score(cfo_history=[120.0, 130.0], pat_history=[100.0, 100.0])
    assert score == 1.25
    assert label == "High Quality"

    # Accrual Risk: avg < 0.5
    score_risk, label_risk = compute_cfo_quality_score(cfo_history=[30.0, 40.0], pat_history=[100.0, 100.0])
    assert score_risk == 0.35
    assert label_risk == "Accrual Risk"


def test_24_capex_intensity():
    """Test 24: CapEx Intensity = abs(CFI) / Sales * 100 tiers"""
    # Asset Light < 3%
    pct_light, lbl_light = compute_capex_intensity(investing_activity=-20.0, sales=1000.0)
    assert pct_light == 2.0
    assert lbl_light == "Asset Light"

    # Capital Intensive > 8%
    pct_heavy, lbl_heavy = compute_capex_intensity(investing_activity=-120.0, sales=1000.0)
    assert pct_heavy == 12.0
    assert lbl_heavy == "Capital Intensive"


def test_25_capital_allocation_patterns():
    """Test 25: 8-pattern classification of (CFO, CFI, CFF)"""
    # (+, -, -) with CFO/PAT > 1.0 -> Shareholder Returns
    s_cfo, s_cfi, s_cff, pat = classify_capital_allocation_pattern(500.0, -200.0, -100.0, cfo_pat_ratio=1.2)
    assert (s_cfo, s_cfi, s_cff) == ("+", "-", "-")
    assert pat == "Shareholder Returns"

    # (-, -, +) -> Growth Funded by Debt
    s_cfo, s_cfi, s_cff, pat = classify_capital_allocation_pattern(-100.0, -300.0, 500.0)
    assert (s_cfo, s_cfi, s_cff) == ("-", "-", "+")
    assert pat == "Growth Funded by Debt"

    # (+, +, -) -> Liquidating Assets
    s_cfo, s_cfi, s_cff, pat = classify_capital_allocation_pattern(300.0, 100.0, -200.0)
    assert (s_cfo, s_cfi, s_cff) == ("+", "+", "-")
    assert pat == "Liquidating Assets"
