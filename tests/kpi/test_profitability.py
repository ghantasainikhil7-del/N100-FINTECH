"""Unit tests for Profitability & Return KPIs (Day 08: 8 tests)."""
import pytest
from src.analytics.ratios import (
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_roa,
    compute_roce,
    compute_roe,
)


def test_npm_normal():
    """Net profit margin computes correctly for positive sales and net profit."""
    assert compute_net_profit_margin(net_profit=200.0, sales=1000.0) == 20.0


def test_npm_zero_sales():
    """Net profit margin returns None when sales is 0."""
    assert compute_net_profit_margin(net_profit=50.0, sales=0.0) is None


def test_npm_negative_profit():
    """Negative profit produces negative NPM."""
    assert compute_net_profit_margin(net_profit=-50.0, sales=500.0) == -10.0


def test_opm_crosscheck_match():
    """OPM matches source within 1% tolerance."""
    opm, mismatch = compute_operating_profit_margin(operating_profit=215.0, sales=1000.0, source_opm=21.5)
    assert opm == 21.5
    assert mismatch is False


def test_opm_crosscheck_mismatch():
    """OPM triggers mismatch flag when difference > 1%."""
    opm, mismatch = compute_operating_profit_margin(operating_profit=215.0, sales=1000.0, source_opm=25.0)
    assert opm == 21.5
    assert mismatch is True


def test_roe_positive_equity():
    """ROE computes correctly when total equity is positive."""
    assert compute_roe(net_profit=100.0, equity_capital=200.0, reserves=300.0) == 20.0


def test_roe_negative_equity():
    """ROE returns None when total equity is negative or zero."""
    assert compute_roe(net_profit=100.0, equity_capital=50.0, reserves=-150.0) is None
    assert compute_roe(net_profit=100.0, equity_capital=0.0, reserves=0.0) is None


def test_roce_and_roa():
    """ROCE and ROA compute correctly, and zero assets returns None."""
    # EBIT=300, Capital Employed = 100 + 400 + 500 = 1000 -> 30%
    assert compute_roce(ebit=300.0, equity_capital=100.0, reserves=400.0, borrowings=500.0) == 30.0
    # ROA
    assert compute_roa(net_profit=150.0, total_assets=1500.0) == 10.0
    assert compute_roa(net_profit=150.0, total_assets=0.0) is None
