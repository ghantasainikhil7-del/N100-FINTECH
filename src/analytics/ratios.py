"""Financial Ratio calculations: Profitability, Leverage, Efficiency, and Returns."""
from __future__ import annotations

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. PROFITABILITY & RETURN RATIOS
# ==============================================================================

def compute_net_profit_margin(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """Net Profit Margin = (Net Profit / Sales) * 100. Returns None if sales <= 0 or missing."""
    if net_profit is None or sales is None or sales <= 0:
        return None
    return round((net_profit / sales) * 100.0, 2)


def compute_operating_profit_margin(
    operating_profit: Optional[float],
    sales: Optional[float],
    source_opm: Optional[float] = None,
    tolerance: float = 1.0,
) -> Tuple[Optional[float], bool]:
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100.
    Returns (computed_opm, has_crosscheck_mismatch).
    """
    if operating_profit is None or sales is None or sales <= 0:
        return None, False

    computed = round((operating_profit / sales) * 100.0, 2)
    mismatch = False
    if source_opm is not None:
        if abs(computed - source_opm) > tolerance:
            mismatch = True
    return computed, mismatch


def compute_roe(
    net_profit: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
) -> Optional[float]:
    """
    Return on Equity (ROE) = Net Profit / (Equity Capital + Reserves) * 100.
    Edge Case: Return None if total equity <= 0 or missing.
    """
    if net_profit is None or equity_capital is None:
        return None
    total_equity = equity_capital + (reserves or 0.0)
    if total_equity <= 0:
        return None
    return round((net_profit / total_equity) * 100.0, 2)


def compute_roce(
    ebit: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
    borrowings: Optional[float],
    is_financial: bool = False,
) -> Optional[float]:
    """
    Return on Capital Employed (ROCE) = EBIT / Capital Employed * 100.
    Capital Employed = Equity + Reserves + Borrowings.
    For financial institutions (banks/NBFCs), sector-relative benchmarking is advised.
    """
    if ebit is None or equity_capital is None:
        return None
    total_equity = equity_capital + (reserves or 0.0)
    capital_employed = total_equity + (borrowings or 0.0)
    if capital_employed <= 0:
        return None
    return round((ebit / capital_employed) * 100.0, 2)


def compute_roa(net_profit: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """Return on Assets (ROA) = (Net Profit / Total Assets) * 100. Returns None if total_assets <= 0."""
    if net_profit is None or total_assets is None or total_assets <= 0:
        return None
    return round((net_profit / total_assets) * 100.0, 2)


# ==============================================================================
# 2. LEVERAGE & EFFICIENCY RATIOS
# ==============================================================================

def compute_debt_to_equity(
    borrowings: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
    is_financial: bool = False,
) -> Tuple[Optional[float], bool]:
    """
    Debt to Equity = Borrowings / Total Equity.
    - If borrowings == 0: returns (0.0, False)
    - If total equity <= 0: returns (None, False)
    - High leverage flag: True if D/E > 5 and NOT in Financials sector.
    """
    if borrowings is None or borrowings == 0:
        return 0.0, False

    if equity_capital is None:
        return None, False

    total_equity = equity_capital + (reserves or 0.0)
    if total_equity <= 0:
        return None, False

    de = round(borrowings / total_equity, 2)
    high_leverage = (de > 5.0) and (not is_financial)
    return de, high_leverage


def compute_interest_coverage(
    operating_profit: Optional[float],
    other_income: Optional[float],
    interest: Optional[float],
) -> Tuple[Optional[float], str, bool]:
    """
    Interest Coverage Ratio (ICR) = (Operating Profit + Other Income) / Interest.
    Returns (icr_numeric, icr_label, is_warning).
    - If interest == 0: returns (None, 'Debt Free', False)
    - If ICR < 1.5: returns (icr, 'At Risk', True)
    - Normal: returns (icr, 'Normal', False)
    """
    if interest is None or interest == 0:
        return None, "Debt Free", False

    op = operating_profit or 0.0
    oi = other_income or 0.0
    earnings_available = op + oi
    icr = round(earnings_available / interest, 2)
    is_warning = icr < 1.5
    label = "At Risk" if is_warning else "Normal"
    return icr, label, is_warning


def compute_net_debt(
    borrowings: Optional[float],
    investments: Optional[float],
    cash: Optional[float] = 0.0,
) -> float:
    """Net Debt = Borrowings - (Investments + Cash). Uses investments as liquid asset proxy."""
    b = borrowings or 0.0
    inv = investments or 0.0
    c = cash or 0.0
    return round(b - inv - c, 2)


def compute_asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """Asset Turnover = Sales / Total Assets. Returns None if total_assets <= 0."""
    if sales is None or total_assets is None or total_assets <= 0:
        return None
    return round(sales / total_assets, 2)


def compute_book_value_per_share(
    equity_capital: Optional[float],
    reserves: Optional[float],
    face_value: Optional[float] = 1.0,
) -> Optional[float]:
    """
    Book Value Per Share = Total Equity / Number of Shares.
    Number of Shares = Equity Capital / Face Value.
    """
    if equity_capital is None or equity_capital <= 0:
        return None
    fv = face_value or 1.0
    if fv <= 0:
        fv = 1.0
    total_equity = equity_capital + (reserves or 0.0)
    shares_count = equity_capital / fv
    if shares_count <= 0:
        return None
    return round(total_equity / shares_count, 2)
