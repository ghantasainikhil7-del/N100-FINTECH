"""Compound Annual Growth Rate (CAGR) Engine with all 6 edge case handlers."""
from __future__ import annotations

import logging
from typing import Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

CAGR_FLAG_NORMAL = "NORMAL"
CAGR_FLAG_DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
CAGR_FLAG_TURNAROUND = "TURNAROUND"
CAGR_FLAG_BOTH_NEGATIVE = "BOTH_NEGATIVE"
CAGR_FLAG_ZERO_BASE = "ZERO_BASE"
CAGR_FLAG_INSUFFICIENT = "INSUFFICIENT"

CAGR_DISPLAY_MAP = {
    CAGR_FLAG_NORMAL: "{val:.1f}%",
    CAGR_FLAG_DECLINE_TO_LOSS: "N/A — turned loss",
    CAGR_FLAG_TURNAROUND: "Turnaround ↑",
    CAGR_FLAG_BOTH_NEGATIVE: "N/A — both loss",
    CAGR_FLAG_ZERO_BASE: "N/A — base=0",
    CAGR_FLAG_INSUFFICIENT: "N/A — < 3yr",
}


def compute_cagr(
    start_val: Optional[float],
    end_val: Optional[float],
    n_years: int,
) -> Tuple[Optional[float], str]:
    """
    Compute CAGR: ((end / start) ** (1 / n_years) - 1) * 100.
    Handles all 6 edge cases:
      1. Normal: start > 0 and end > 0
      2. Decline to Loss: start > 0 and end < 0
      3. Turnaround: start < 0 and end > 0
      4. Both Negative: start < 0 and end < 0
      5. Zero Base: start == 0
      6. Insufficient: missing values or n_years < 1
    """
    if start_val is None or end_val is None or n_years < 1:
        return None, CAGR_FLAG_INSUFFICIENT

    # Case 5: Zero base
    if start_val == 0:
        return None, CAGR_FLAG_ZERO_BASE

    # Case 2: Turned into loss
    if start_val > 0 and end_val < 0:
        return None, CAGR_FLAG_DECLINE_TO_LOSS

    # Case 3: Turnaround (from loss to profit)
    if start_val < 0 and end_val > 0:
        return None, CAGR_FLAG_TURNAROUND

    # Case 4: Both negative
    if start_val < 0 and end_val < 0:
        return None, CAGR_FLAG_BOTH_NEGATIVE

    # Case 1: Standard positive growth
    if start_val > 0 and end_val >= 0:
        if end_val == 0:
            return -100.0, CAGR_FLAG_NORMAL
        ratio = end_val / start_val
        val = ((ratio ** (1.0 / n_years)) - 1.0) * 100.0
        return round(val, 2), CAGR_FLAG_NORMAL

    return None, CAGR_FLAG_INSUFFICIENT


def format_cagr_display(val: Optional[float], flag: str) -> str:
    """Format CAGR value for user-facing displays and reports."""
    if flag == CAGR_FLAG_NORMAL and val is not None:
        return f"{val:+.1f}%"
    return CAGR_DISPLAY_MAP.get(flag, "N/A")


def calculate_series_cagr(
    series_df: pd.DataFrame,
    year_col: str,
    metric_col: str,
    window: int,
) -> list[Tuple[Optional[float], str]]:
    """
    Calculate rolling n-year CAGR for each row in a company's chronological series.
    Returns list of (cagr_val, flag) corresponding to each row.
    """
    if series_df.empty or metric_col not in series_df.columns:
        return []

    sorted_df = series_df.sort_values(by=year_col).reset_index(drop=True)
    results = []
    n = len(sorted_df)

    for i in range(n):
        if i < window:
            results.append((None, CAGR_FLAG_INSUFFICIENT))
        else:
            start_val = sorted_df.loc[i - window, metric_col]
            end_val = sorted_df.loc[i, metric_col]
            res = compute_cagr(start_val, end_val, window)
            results.append(res)

    return results
