"""Unit tests for Ratio Engine edge cases, sector carveouts, and KPI registry."""
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
from src.analytics.capital_allocation import (
    PATTERN_DISTRESS_SIGNAL,
    PATTERN_GROWTH_FUNDED_BY_DEBT,
    PATTERN_LIQUIDATING_ASSETS,
    PATTERN_PRE_REVENUE,
    PATTERN_REINVESTOR,
    PATTERN_SHAREHOLDER_RETURNS,
    classify_pattern,
)
from src.analytics.kpi_registry import KpiCategory, KpiStatus, registry
from src.analytics.ratios import (
    compute_asset_turnover,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_net_profit_margin,
    compute_roce,
    compute_roe,
)


def test_roe_negative_equity_returns_none():
    """Negative or zero equity capital + reserves must return None to avoid misleading positive signs."""
    # Negative reserves exceeding capital
    assert compute_roe(net_profit=100.0, equity_capital=20.0, reserves=-50.0) is None
    # Negative net profit with negative equity
    assert compute_roe(net_profit=-100.0, equity_capital=20.0, reserves=-50.0) is None
    # Zero equity
    assert compute_roe(net_profit=100.0, equity_capital=0.0, reserves=0.0) is None


def test_debt_free_company_handling():
    """Debt-free companies must have D/E = 0.0 and ICR = None with 'Debt Free' label."""
    # Zero borrowings
    de, flag = compute_debt_to_equity(borrowings=0.0, equity_capital=100.0, reserves=500.0)
    assert de == 0.0
    assert flag is False

    # Zero interest expense
    icr, label, is_warn = compute_interest_coverage(operating_profit=250.0, other_income=30.0, interest=0.0)
    assert icr is None
    assert label == "Debt Free"
    assert is_warn is False


def test_financials_sector_carveout():
    """High leverage (> 5.0) in banks / NBFCs must suppress high_leverage_flag."""
    # Financial institution with D/E = 8.5
    de_fin, flag_fin = compute_debt_to_equity(borrowings=8500.0, equity_capital=100.0, reserves=900.0, is_financial=True)
    assert de_fin == 8.5
    assert flag_fin is False  # Suppressed

    # Manufacturing / Non-financial with D/E = 8.5
    de_corp, flag_corp = compute_debt_to_equity(borrowings=8500.0, equity_capital=100.0, reserves=900.0, is_financial=False)
    assert de_corp == 8.5
    assert flag_corp is True  # Flagged


def test_icr_at_risk_warning():
    """ICR < 1.5 must trigger 'At Risk' label and warning flag."""
    icr, label, is_warn = compute_interest_coverage(operating_profit=120.0, other_income=10.0, interest=100.0)
    assert icr == 1.3
    assert label == "At Risk"
    assert is_warn is True

    # Normal ICR >= 1.5
    icr_ok, label_ok, is_warn_ok = compute_interest_coverage(operating_profit=300.0, other_income=10.0, interest=100.0)
    assert icr_ok == 3.1
    assert label_ok == "Normal"
    assert is_warn_ok is False


def test_cagr_turnaround_and_decline_to_loss():
    """CAGR must gracefully return None with distinct categorical flags for sign flips."""
    # Base loss, end profit
    val_turn, flag_turn = compute_cagr(start_val=-50.0, end_val=150.0, n_years=5)
    assert val_turn is None
    assert flag_turn == CAGR_FLAG_TURNAROUND

    # Base profit, end loss
    val_loss, flag_loss = compute_cagr(start_val=120.0, end_val=-30.0, n_years=3)
    assert val_loss is None
    assert flag_loss == CAGR_FLAG_DECLINE_TO_LOSS

    # Both negative
    val_neg, flag_neg = compute_cagr(start_val=-100.0, end_val=-40.0, n_years=5)
    assert val_neg is None
    assert flag_neg == CAGR_FLAG_BOTH_NEGATIVE

    # Base = 0
    val_zero, flag_zero = compute_cagr(start_val=0.0, end_val=80.0, n_years=5)
    assert val_zero is None
    assert flag_zero == CAGR_FLAG_ZERO_BASE


def test_capital_allocation_patterns():
    """8 capital allocation patterns properly classified according to CFO, CFI, CFF signs."""
    # (+, -, -) with CFO/PAT <= 1.0 -> Reinvestor
    _, _, _, p1 = classify_pattern(cfo=100.0, cfi=-60.0, cff=-30.0, cfo_pat_ratio=0.9)
    assert p1 == PATTERN_REINVESTOR

    # (+, -, -) with CFO/PAT > 1.0 -> Shareholder Returns
    _, _, _, p2 = classify_pattern(cfo=150.0, cfi=-40.0, cff=-80.0, cfo_pat_ratio=1.2)
    assert p2 == PATTERN_SHAREHOLDER_RETURNS

    # (+, +, -) -> Liquidating Assets
    _, _, _, p3 = classify_pattern(cfo=100.0, cfi=30.0, cff=-50.0)
    assert p3 == PATTERN_LIQUIDATING_ASSETS

    # (-, +, +) -> Distress Signal
    _, _, _, p4 = classify_pattern(cfo=-50.0, cfi=20.0, cff=40.0)
    assert p4 == PATTERN_DISTRESS_SIGNAL

    # (-, -, +) -> Growth Funded by Debt
    _, _, _, p5 = classify_pattern(cfo=-40.0, cfi=-100.0, cff=120.0)
    assert p5 == PATTERN_GROWTH_FUNDED_BY_DEBT

    # (-, -, -) -> Pre-Revenue
    _, _, _, p6 = classify_pattern(cfo=-20.0, cfi=-50.0, cff=-10.0)
    assert p6 == PATTERN_PRE_REVENUE


def test_safe_division_boundary_handling():
    """Division by zero or negative assets/sales safely returns None."""
    assert compute_net_profit_margin(net_profit=50.0, sales=0.0) is None
    assert compute_net_profit_margin(net_profit=50.0, sales=-100.0) is None
    assert compute_asset_turnover(sales=500.0, total_assets=0.0) is None
    assert compute_roce(ebit=100.0, equity_capital=0.0, reserves=0.0, borrowings=0.0) is None


def test_kpi_registry_integrity():
    """Machine-readable KPI registry contains >= 50 KPIs with valid SPEC/EXTENSION tags."""
    summary = registry.summary()
    assert summary["total_kpis"] >= 50
    assert summary["spec_count"] >= 35
    assert summary["extension_count"] >= 10

    # Every KPI has non-empty metadata
    for kpi in registry.all_kpis():
        assert len(kpi.kpi_id) > 0
        assert len(kpi.name) > 0
        assert len(kpi.formula) > 0
        assert kpi.status in (KpiStatus.SPEC, KpiStatus.EXTENSION)
        assert isinstance(kpi.category, KpiCategory)
