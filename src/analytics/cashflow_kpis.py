"""Cash flow KPIs, CFO earnings quality, CapEx intensity, and capital allocation patterns."""
from __future__ import annotations

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def compute_free_cash_flow(
    operating_activity: Optional[float],
    investing_activity: Optional[float],
) -> Optional[float]:
    """Free Cash Flow (FCF) = CFO + CFI. Negative values permitted."""
    if operating_activity is None or investing_activity is None:
        return None
    return round(operating_activity + investing_activity, 2)


def compute_cfo_quality_score(
    cfo_history: list[float],
    pat_history: list[float],
) -> Tuple[Optional[float], str]:
    """
    CFO Quality Score = 5-year average of (CFO / PAT).
    - > 1.0: High Quality
    - 0.5 – 1.0: Moderate
    - < 0.5: Accrual Risk
    Returns (score_ratio, quality_label).
    """
    if not cfo_history or not pat_history:
        return None, "Insufficient Data"

    valid_ratios = []
    for cfo, pat in zip(cfo_history, pat_history):
        if pat is not None and pat != 0 and cfo is not None:
            valid_ratios.append(cfo / pat)

    if not valid_ratios:
        return None, "No Valid PAT"

    avg_ratio = round(sum(valid_ratios) / len(valid_ratios), 2)
    if avg_ratio > 1.0:
        label = "High Quality"
    elif avg_ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return avg_ratio, label


def compute_capex_intensity(
    investing_activity: Optional[float],
    sales: Optional[float],
) -> Tuple[Optional[float], str]:
    """
    CapEx Intensity = (abs(investing_activity) / sales) * 100.
    - < 3%: Asset Light
    - 3% – 8%: Moderate
    - > 8%: Capital Intensive
    Returns (intensity_pct, category_label).
    """
    if investing_activity is None or sales is None or sales <= 0:
        return None, "Unknown"

    intensity = round((abs(investing_activity) / sales) * 100.0, 2)
    if intensity < 3.0:
        label = "Asset Light"
    elif intensity <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return intensity, label


def compute_fcf_conversion_rate(
    fcf: Optional[float],
    operating_profit: Optional[float],
) -> Tuple[Optional[float], str]:
    """
    FCF Conversion Rate = (FCF / Operating Profit) * 100.
    - > 60%: Efficient
    - 30% – 60%: Moderate
    - < 30%: CapEx Heavy
    """
    if fcf is None or operating_profit is None or operating_profit <= 0:
        return None, "Unknown"

    rate = round((fcf / operating_profit) * 100.0, 2)
    if rate > 60.0:
        tier = "Efficient"
    elif rate >= 30.0:
        tier = "Moderate"
    else:
        tier = "CapEx Heavy"

    return rate, tier


def classify_capital_allocation_pattern(
    cfo: Optional[float],
    cfi: Optional[float],
    cff: Optional[float],
    cfo_pat_ratio: Optional[float] = None,
) -> Tuple[str, str, str, str]:
    """
    Classify company into one of 8 capital allocation patterns based on CFO, CFI, CFF signs:
      - (+, -, -): Reinvestor (or Shareholder Returns if cfo_pat_ratio > 1.0)
      - (+, +, -): Liquidating Assets
      - (-, +, +): Distress Signal
      - (-, -, +): Growth Funded by Debt
      - (+, +, +): Cash Accumulator
      - (-, -, -): Pre-Revenue
      - (+, -, +): Mixed
      - other: Undefined / Other
    Returns (cfo_sign, cfi_sign, cff_sign, pattern_label).
    """
    cfo_val = cfo or 0.0
    cfi_val = cfi or 0.0
    cff_val = cff or 0.0

    sgn_cfo = "+" if cfo_val > 0 else "-"
    sgn_cfi = "+" if cfi_val > 0 else "-"
    sgn_cff = "+" if cff_val > 0 else "-"

    sign_tuple = (sgn_cfo, sgn_cfi, sgn_cff)

    if sign_tuple == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            label = "Shareholder Returns"
        else:
            label = "Reinvestor"
    elif sign_tuple == ("+", "+", "-"):
        label = "Liquidating Assets"
    elif sign_tuple == ("-", "+", "+"):
        label = "Distress Signal"
    elif sign_tuple == ("-", "-", "+"):
        label = "Growth Funded by Debt"
    elif sign_tuple == ("+", "+", "+"):
        label = "Cash Accumulator"
    elif sign_tuple == ("-", "-", "-"):
        label = "Pre-Revenue"
    elif sign_tuple == ("+", "-", "+"):
        label = "Mixed"
    elif sign_tuple == ("-", "+", "-"):
        label = "Restructuring"
    else:
        label = "Mixed"

    return sgn_cfo, sgn_cfi, sgn_cff, label
