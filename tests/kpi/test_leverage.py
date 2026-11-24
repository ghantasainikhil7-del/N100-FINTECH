"""Unit tests for Leverage & Efficiency KPIs (Day 09: 8 tests)."""
import pytest
from src.analytics.ratios import (
    compute_asset_turnover,
    compute_book_value_per_share,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_net_debt,
)


def test_de_normal():
    """Normal D/E calculation."""
    de, flag = compute_debt_to_equity(borrowings=200.0, equity_capital=100.0, reserves=400.0)
    assert de == 0.4
    assert flag is False


def test_de_debt_free():
    """Borrowings = 0 returns 0.0 (not None)."""
    de, flag = compute_debt_to_equity(borrowings=0.0, equity_capital=100.0, reserves=400.0)
    assert de == 0.0
    assert flag is False


def test_de_high_leverage_non_financial():
    """D/E > 5 for non-financial sets high_leverage_flag = True."""
    de, flag = compute_debt_to_equity(borrowings=6000.0, equity_capital=100.0, reserves=900.0, is_financial=False)
    assert de == 6.0
    assert flag is True


def test_de_high_leverage_bank_carveout():
    """D/E > 5 for banks/NBFCs suppresses high_leverage_flag (flag = False)."""
    de, flag = compute_debt_to_equity(borrowings=8000.0, equity_capital=100.0, reserves=900.0, is_financial=True)
    assert de == 8.0
    assert flag is False


def test_icr_normal():
    """Normal interest coverage ratio calculation."""
    icr, label, warning = compute_interest_coverage(operating_profit=500.0, other_income=50.0, interest=100.0)
    assert icr == 5.5
    assert label == "Normal"
    assert warning is False


def test_icr_debt_free():
    """Interest = 0 returns None and label 'Debt Free'."""
    icr, label, warning = compute_interest_coverage(operating_profit=500.0, other_income=50.0, interest=0.0)
    assert icr is None
    assert label == "Debt Free"
    assert warning is False


def test_icr_warning_flag():
    """ICR < 1.5 triggers warning flag."""
    icr, label, warning = compute_interest_coverage(operating_profit=100.0, other_income=20.0, interest=100.0)
    assert icr == 1.2
    assert label == "At Risk"
    assert warning is True


def test_asset_turnover_and_net_debt():
    """Asset turnover computes correctly, zero assets returns None; Net debt computes correctly."""
    assert compute_asset_turnover(sales=2000.0, total_assets=1000.0) == 2.0
    assert compute_asset_turnover(sales=2000.0, total_assets=0.0) is None
    assert compute_net_debt(borrowings=500.0, investments=300.0, cash=50.0) == 150.0
    assert compute_book_value_per_share(equity_capital=100.0, reserves=900.0, face_value=2.0) == 20.0
