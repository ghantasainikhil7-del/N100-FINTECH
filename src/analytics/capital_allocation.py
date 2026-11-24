"""Capital Allocation Pattern Classifier and Export Engine (Sprint 2 Deliverable)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Tuple
import pandas as pd

from src.analytics.ratio_config import CAPITAL_ALLOCATION_CSV

logger = logging.getLogger(__name__)

# The 8 canonical capital allocation patterns
PATTERN_REINVESTOR = "Reinvestor"
PATTERN_SHAREHOLDER_RETURNS = "Shareholder Returns"
PATTERN_LIQUIDATING_ASSETS = "Liquidating Assets"
PATTERN_DISTRESS_SIGNAL = "Distress Signal"
PATTERN_GROWTH_FUNDED_BY_DEBT = "Growth Funded by Debt"
PATTERN_CASH_ACCUMULATOR = "Cash Accumulator"
PATTERN_PRE_REVENUE = "Pre-Revenue"
PATTERN_MIXED = "Mixed"
PATTERN_RESTRUCTURING = "Restructuring"

ALL_PATTERNS = [
    PATTERN_REINVESTOR,
    PATTERN_SHAREHOLDER_RETURNS,
    PATTERN_LIQUIDATING_ASSETS,
    PATTERN_DISTRESS_SIGNAL,
    PATTERN_GROWTH_FUNDED_BY_DEBT,
    PATTERN_CASH_ACCUMULATOR,
    PATTERN_PRE_REVENUE,
    PATTERN_MIXED,
    PATTERN_RESTRUCTURING,
]


def classify_pattern(
    cfo: Optional[float],
    cfi: Optional[float],
    cff: Optional[float],
    cfo_pat_ratio: Optional[float] = None,
) -> Tuple[str, str, str, str]:
    """
    Classify company into one of 8 capital allocation patterns based on signs of CFO, CFI, CFF.
    
    Returns:
        (sgn_cfo, sgn_cfi, sgn_cff, pattern_label)
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
            label = PATTERN_SHAREHOLDER_RETURNS
        else:
            label = PATTERN_REINVESTOR
    elif sign_tuple == ("+", "+", "-"):
        label = PATTERN_LIQUIDATING_ASSETS
    elif sign_tuple == ("-", "+", "+"):
        label = PATTERN_DISTRESS_SIGNAL
    elif sign_tuple == ("-", "-", "+"):
        label = PATTERN_GROWTH_FUNDED_BY_DEBT
    elif sign_tuple == ("+", "+", "+"):
        label = PATTERN_CASH_ACCUMULATOR
    elif sign_tuple == ("-", "-", "-"):
        label = PATTERN_PRE_REVENUE
    elif sign_tuple == ("+", "-", "+"):
        label = PATTERN_MIXED
    elif sign_tuple == ("-", "+", "-"):
        label = PATTERN_RESTRUCTURING
    else:
        label = PATTERN_MIXED

    return sgn_cfo, sgn_cfi, sgn_cff, label


def export_capital_allocation_csv(
    allocations: list[dict[str, Any]],
    output_path: Path | str = CAPITAL_ALLOCATION_CSV,
) -> Path:
    """Save records to output/capital_allocation.csv."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(allocations)
    df.to_csv(path, index=False)
    logger.info("Successfully exported %d capital allocation patterns to %s", len(df), path)
    return path
