"""Analytics and Financial Ratio Engine for Nifty 100 Platform."""
from src.analytics.cagr import compute_cagr, format_cagr_display
from src.analytics.cashflow_kpis import (
    classify_capital_allocation_pattern,
    compute_capex_intensity,
    compute_cfo_quality_score,
    compute_fcf_conversion_rate,
    compute_free_cash_flow,
)
from src.analytics.engine import RatioEngine
from src.analytics.ratios import (
    compute_asset_turnover,
    compute_book_value_per_share,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_net_debt,
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_roa,
    compute_roce,
    compute_roe,
)

__all__ = [
    "RatioEngine",
    "compute_net_profit_margin",
    "compute_operating_profit_margin",
    "compute_roe",
    "compute_roce",
    "compute_roa",
    "compute_debt_to_equity",
    "compute_interest_coverage",
    "compute_net_debt",
    "compute_asset_turnover",
    "compute_book_value_per_share",
    "compute_cagr",
    "format_cagr_display",
    "compute_free_cash_flow",
    "compute_cfo_quality_score",
    "compute_capex_intensity",
    "compute_fcf_conversion_rate",
    "classify_capital_allocation_pattern",
]
