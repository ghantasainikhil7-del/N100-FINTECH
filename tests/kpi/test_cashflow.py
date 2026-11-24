"""Unit tests for Cash Flow KPIs and 8-pattern Capital Allocation classifier (Day 11: 6 tests)."""
import pytest
from src.analytics.cashflow_kpis import (
    classify_capital_allocation_pattern,
    compute_capex_intensity,
    compute_cfo_quality_score,
    compute_fcf_conversion_rate,
    compute_free_cash_flow,
)


def test_free_cash_flow_normal():
    """FCF = CFO + CFI (negative allowed)."""
    assert compute_free_cash_flow(operating_activity=500.0, investing_activity=-200.0) == 300.0
    assert compute_free_cash_flow(operating_activity=100.0, investing_activity=-250.0) == -150.0


def test_cfo_quality_score():
    """CFO Quality Score classification across tiers."""
    score, label = compute_cfo_quality_score([120.0, 150.0, 130.0], [100.0, 100.0, 100.0])
    assert score == 1.33
    assert label == "High Quality"

    score2, label2 = compute_cfo_quality_score([70.0, 80.0], [100.0, 100.0])
    assert score2 == 0.75
    assert label2 == "Moderate"

    score3, label3 = compute_cfo_quality_score([30.0, 40.0], [100.0, 100.0])
    assert score3 == 0.35
    assert label3 == "Accrual Risk"


def test_capex_intensity():
    """CapEx intensity tiers: Asset Light, Moderate, Capital Intensive."""
    intensity, label = compute_capex_intensity(investing_activity=-20.0, sales=1000.0)
    assert intensity == 2.0
    assert label == "Asset Light"

    intensity2, label2 = compute_capex_intensity(investing_activity=-50.0, sales=1000.0)
    assert intensity2 == 5.0
    assert label2 == "Moderate"

    intensity3, label3 = compute_capex_intensity(investing_activity=-120.0, sales=1000.0)
    assert intensity3 == 12.0
    assert label3 == "Capital Intensive"


def test_fcf_conversion_rate():
    """FCF conversion rate tiers: Efficient, Moderate, CapEx Heavy."""
    rate, tier = compute_fcf_conversion_rate(fcf=70.0, operating_profit=100.0)
    assert rate == 70.0
    assert tier == "Efficient"

    rate2, tier2 = compute_fcf_conversion_rate(fcf=40.0, operating_profit=100.0)
    assert rate2 == 40.0
    assert tier2 == "Moderate"

    rate3, tier3 = compute_fcf_conversion_rate(fcf=20.0, operating_profit=100.0)
    assert rate3 == 20.0
    assert tier3 == "CapEx Heavy"


def test_capital_allocation_reinvestor_and_returns():
    """(+,-,-) classified as Reinvestor or Shareholder Returns."""
    _, _, _, label1 = classify_capital_allocation_pattern(cfo=100, cfi=-40, cff=-30, cfo_pat_ratio=0.8)
    assert label1 == "Reinvestor"

    _, _, _, label2 = classify_capital_allocation_pattern(cfo=100, cfi=-40, cff=-30, cfo_pat_ratio=1.4)
    assert label2 == "Shareholder Returns"


def test_capital_allocation_other_patterns():
    """Test all remaining patterns: Liquidating, Distress, Debt Growth, Accumulator, Pre-Rev."""
    assert classify_capital_allocation_pattern(100, 50, -30)[3] == "Liquidating Assets"
    assert classify_capital_allocation_pattern(-50, 20, 40)[3] == "Distress Signal"
    assert classify_capital_allocation_pattern(-50, -30, 80)[3] == "Growth Funded by Debt"
    assert classify_capital_allocation_pattern(100, 50, 20)[3] == "Cash Accumulator"
    assert classify_capital_allocation_pattern(-50, -20, -10)[3] == "Pre-Revenue"
    assert classify_capital_allocation_pattern(100, -30, 20)[3] == "Mixed"
