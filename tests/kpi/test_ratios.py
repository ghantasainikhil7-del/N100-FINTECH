"""20 Unit Tests covering core financial ratio calculations, flags, and cash flow KPIs."""
import pytest
from src.analytics.cagr import (
    CAGR_FLAG_BOTH_NEGATIVE,
    CAGR_FLAG_DECLINE_TO_LOSS,
    CAGR_FLAG_INSUFFICIENT,
    CAGR_FLAG_NORMAL,
    CAGR_FLAG_TURNAROUND,
    CAGR_FLAG_ZERO_BASE,
    compute_cagr,
)
from src.analytics.cashflow_kpis import (
    classify_capital_allocation_pattern,
    compute_capex_intensity,
    compute_cfo_quality_score,
    compute_fcf_conversion_rate,
    compute_free_cash_flow,
)
from src.analytics.ratios import (
    compute_asset_turnover,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_net_debt,
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_roa,
    compute_roce,
    compute_roe,
)


# ==============================================================================
# 20 KPI UNIT TESTS (Sprint 6 Day 41)
# ==============================================================================

# Test 1: ROE with positive equity
def test_roe_positive_equity():
    """Verify ROE calculation with standard positive equity."""
    # net_profit=1000, equity_capital=200, reserves=800 -> total_equity=1000 -> ROE=100.0%
    roe = compute_roe(net_profit=100.0, equity_capital=100.0, reserves=400.0)
    assert roe == 20.0


# Test 2: ROE with negative equity -> None
def test_roe_negative_equity():
    """Verify ROE returns None when total equity is negative or zero."""
    roe = compute_roe(net_profit=100.0, equity_capital=100.0, reserves=-200.0)
    assert roe is None


# Test 3: D/E for debt-free company -> 0
def test_debt_to_equity_debt_free():
    """Verify D/E returns 0.0 for debt-free companies."""
    de, high_lev = compute_debt_to_equity(borrowings=0.0, equity_capital=100.0, reserves=900.0)
    assert de == 0.0
    assert high_lev is False


# Test 4: ICR when interest = 0 -> (None, 'Debt Free', False)
def test_icr_zero_interest():
    """Verify ICR returns None with 'Debt Free' label when interest expense is 0."""
    icr, label, is_warning = compute_interest_coverage(operating_profit=500.0, other_income=50.0, interest=0.0)
    assert icr is None
    assert label == "Debt Free"
    assert is_warning is False


# Test 5: D/E > 5 flag for non-financial company
def test_high_leverage_flag_non_financial():
    """Verify high leverage flag is set when D/E > 5.0 for non-financial entities."""
    de, high_lev = compute_debt_to_equity(borrowings=6000.0, equity_capital=100.0, reserves=900.0, is_financial=False)
    assert de == 6.0
    assert high_lev is True


# Test 6: Financial sector carve-out for high leverage
def test_high_leverage_carve_out_financial():
    """Verify financial institutions with D/E > 5.0 are not flagged as high leverage anomalies."""
    de, high_lev = compute_debt_to_equity(borrowings=8000.0, equity_capital=100.0, reserves=900.0, is_financial=True)
    assert de == 8.0
    assert high_lev is False


# Test 7: CAGR turnaround flag (loss to profit)
def test_cagr_turnaround_flag():
    """Verify CAGR calculation correctly identifies turnaround from negative base."""
    cagr, flag = compute_cagr(start_val=-100.0, end_val=250.0, periods=5)
    assert flag == CAGR_FLAG_TURNAROUND
    assert cagr is not None


# Test 8: CAGR decline-to-loss (profit to loss)
def test_cagr_decline_to_loss_flag():
    """Verify CAGR calculation flags transition from positive to negative earnings."""
    cagr, flag = compute_cagr(start_val=200.0, end_val=-50.0, periods=5)
    assert flag == CAGR_FLAG_DECLINE_TO_LOSS


# Test 9: Normal CAGR calculation
def test_cagr_normal_calculation():
    """Verify normal positive CAGR over 5 periods: 100 -> 200 is approx 14.87%."""
    cagr, flag = compute_cagr(start_val=100.0, end_val=200.0, periods=5)
    assert flag == CAGR_FLAG_NORMAL
    assert round(cagr, 2) == 14.87


# Test 10: OPM cross-check and calculation
def test_opm_calculation():
    """Verify operating profit margin = (OP / Sales) * 100."""
    opm = compute_operating_profit_margin(operating_profit=250.0, sales=1000.0)
    assert opm == 25.0


# Test 11: CFO quality score calculation (> 1.0 High Quality)
def test_cfo_quality_score_high_quality():
    """Verify 5-year average CFO/PAT > 1.0 yields High Quality label."""
    cfo_history = [1200.0, 1400.0, 1300.0, 1500.0, 1600.0]
    pat_history = [1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
    score, label = compute_cfo_quality_score(cfo_history, pat_history)
    assert score == 1.4
    assert label == "High Quality"


# Test 12: CFO quality score accrual risk (< 0.5 Accrual Risk)
def test_cfo_quality_score_accrual_risk():
    """Verify 5-year average CFO/PAT < 0.5 yields Accrual Risk label."""
    cfo_history = [200.0, 300.0, 400.0, 350.0, 450.0]
    pat_history = [1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
    score, label = compute_cfo_quality_score(cfo_history, pat_history)
    assert score < 0.5
    assert label == "Accrual Risk"


# Test 13: CapEx intensity asset-light (< 3%)
def test_capex_intensity_asset_light():
    """Verify CapEx intensity < 3% classifies as Asset Light."""
    intensity, label = compute_capex_intensity(investing_activity=-20.0, sales=1000.0)
    assert intensity == 2.0
    assert label == "Asset Light"


# Test 14: CapEx intensity capital-intensive (> 8%)
def test_capex_intensity_capital_intensive():
    """Verify CapEx intensity > 8% classifies as Capital Intensive."""
    intensity, label = compute_capex_intensity(investing_activity=-120.0, sales=1000.0)
    assert intensity == 12.0
    assert label == "Capital Intensive"


# Test 15: Free Cash Flow (FCF = CFO + CFI)
def test_free_cash_flow_calculation():
    """Verify Free Cash Flow computation CFO + CFI."""
    fcf = compute_free_cash_flow(operating_activity=1500.0, investing_activity=-600.0)
    assert fcf == 900.0


# Test 16: ROCE calculation (EBIT / Capital Employed * 100)
def test_roce_calculation():
    """Verify Return on Capital Employed."""
    # EBIT=300, Equity=500, Reserves=500, Borrowings=500 -> CapEmployed=1500 -> ROCE=20%
    roce = compute_roce(ebit=300.0, equity_capital=500.0, reserves=500.0, borrowings=500.0)
    assert roce == 20.0


# Test 17: ROA calculation (Net Profit / Total Assets * 100)
def test_roa_calculation():
    """Verify Return on Assets."""
    roa = compute_roa(net_profit=150.0, total_assets=1500.0)
    assert roa == 10.0


# Test 18: Net Debt computation Borrowings - (Investments + Cash)
def test_net_debt_calculation():
    """Verify Net Debt calculation with liquidity buffer."""
    nd = compute_net_debt(borrowings=1000.0, investments=400.0, cash=100.0)
    assert nd == 500.0


# Test 19: Capital allocation archetype classification: (+, -, -) Reinvestor
def test_capital_allocation_reinvestor():
    """Verify (+, -, -) cash flow pattern classifies as Reinvestor."""
    sgn_cfo, sgn_cfi, sgn_cff, label = classify_capital_allocation_pattern(
        cfo=1000.0, cfi=-600.0, cff=-300.0, cfo_pat_ratio=0.8
    )
    assert (sgn_cfo, sgn_cfi, sgn_cff) == ("+", "-", "-")
    assert label == "Reinvestor"


# Test 20: FCF conversion rate computation (> 60% Efficient)
def test_fcf_conversion_rate():
    """Verify FCF conversion rate = (FCF / Operating Profit) * 100."""
    rate, tier = compute_fcf_conversion_rate(fcf=700.0, operating_profit=1000.0)
    assert rate == 70.0
    assert tier == "Efficient"
