"""Unit tests for CAGR growth metrics and all 6 edge case handlers (Day 10: 10 tests)."""
import pytest
from src.analytics.cagr import (
    CAGR_FLAG_BOTH_NEGATIVE,
    CAGR_FLAG_DECLINE_TO_LOSS,
    CAGR_FLAG_INSUFFICIENT,
    CAGR_FLAG_NORMAL,
    CAGR_FLAG_TURNAROUND,
    CAGR_FLAG_ZERO_BASE,
    compute_cagr,
    format_cagr_display,
)


def test_cagr_normal_5yr():
    """Positive to positive 5-year growth: 100 to 161.051 -> 10.0%."""
    val, flag = compute_cagr(start_val=100.0, end_val=161.051, n_years=5)
    assert flag == CAGR_FLAG_NORMAL
    assert pytest.approx(val, rel=1e-2) == 10.0


def test_cagr_normal_3yr():
    """Positive to positive 3-year growth: 100 to 133.1 -> 10.0%."""
    val, flag = compute_cagr(start_val=100.0, end_val=133.1, n_years=3)
    assert flag == CAGR_FLAG_NORMAL
    assert pytest.approx(val, rel=1e-2) == 10.0


def test_cagr_normal_10yr():
    """Positive to positive 10-year growth: 100 to 259.37 -> 10.0%."""
    val, flag = compute_cagr(start_val=100.0, end_val=259.374, n_years=10)
    assert flag == CAGR_FLAG_NORMAL
    assert pytest.approx(val, rel=1e-2) == 10.0


def test_cagr_decline_to_loss():
    """Base > 0, End < 0 returns None with DECLINE_TO_LOSS flag."""
    val, flag = compute_cagr(start_val=150.0, end_val=-40.0, n_years=5)
    assert val is None
    assert flag == CAGR_FLAG_DECLINE_TO_LOSS
    assert format_cagr_display(val, flag) == "N/A — turned loss"


def test_cagr_turnaround():
    """Base < 0, End > 0 returns None with TURNAROUND flag."""
    val, flag = compute_cagr(start_val=-100.0, end_val=200.0, n_years=5)
    assert val is None
    assert flag == CAGR_FLAG_TURNAROUND
    assert format_cagr_display(val, flag) == "Turnaround ↑"


def test_cagr_both_negative():
    """Base < 0, End < 0 returns None with BOTH_NEGATIVE flag."""
    val, flag = compute_cagr(start_val=-100.0, end_val=-20.0, n_years=5)
    assert val is None
    assert flag == CAGR_FLAG_BOTH_NEGATIVE
    assert format_cagr_display(val, flag) == "N/A — both loss"


def test_cagr_zero_base():
    """Base = 0 returns None with ZERO_BASE flag."""
    val, flag = compute_cagr(start_val=0.0, end_val=500.0, n_years=5)
    assert val is None
    assert flag == CAGR_FLAG_ZERO_BASE
    assert format_cagr_display(val, flag) == "N/A — base=0"


def test_cagr_insufficient_periods():
    """Less than 1 period or missing value returns None with INSUFFICIENT flag."""
    val, flag = compute_cagr(start_val=100.0, end_val=200.0, n_years=0)
    assert val is None
    assert flag == CAGR_FLAG_INSUFFICIENT

    val2, flag2 = compute_cagr(start_val=None, end_val=200.0, n_years=5)
    assert val2 is None
    assert flag2 == CAGR_FLAG_INSUFFICIENT


def test_cagr_zero_end():
    """End value = 0 results in -100% growth."""
    val, flag = compute_cagr(start_val=500.0, end_val=0.0, n_years=5)
    assert val == -100.0
    assert flag == CAGR_FLAG_NORMAL


def test_cagr_display_formatting():
    """Verify all display formats match Section 23.1 specification."""
    assert format_cagr_display(15.24, CAGR_FLAG_NORMAL) == "+15.2%"
    assert format_cagr_display(-8.5, CAGR_FLAG_NORMAL) == "-8.5%"
    assert format_cagr_display(None, CAGR_FLAG_TURNAROUND) == "Turnaround ↑"
    assert format_cagr_display(None, CAGR_FLAG_DECLINE_TO_LOSS) == "N/A — turned loss"
    assert format_cagr_display(None, CAGR_FLAG_INSUFFICIENT) == "N/A — < 3yr"
