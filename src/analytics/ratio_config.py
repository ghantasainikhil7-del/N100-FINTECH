"""Ratio Engine configuration, thresholds, weights, and categorical constants."""
from __future__ import annotations
from pathlib import Path

# ==============================================================================
# 1. DATABASE & OUTPUT PATHS
# ==============================================================================
DEFAULT_DB_PATH = Path("data/nifty100.db")
MIRROR_DB_PATH = Path("nifty100.db")
DEFAULT_OUTPUT_DIR = Path("output")
CAPITAL_ALLOCATION_CSV = DEFAULT_OUTPUT_DIR / "capital_allocation.csv"
RATIO_EDGE_CASES_LOG = DEFAULT_OUTPUT_DIR / "ratio_edge_cases.log"

# ==============================================================================
# 2. FINANCIAL THRESHOLDS & TOLERANCES
# ==============================================================================
HIGH_LEVERAGE_THRESHOLD = 5.0
INTEREST_COVERAGE_RISK_THRESHOLD = 1.5
OPM_CROSS_CHECK_TOLERANCE = 1.0  # percentage points
ROCE_CROSS_CHECK_TOLERANCE = 5.0  # percentage points
CFO_PAT_QUALITY_BENCHMARK = 1.0

# CapEx intensity (% of Sales)
CAPEX_LIGHT_THRESHOLD = 3.0
CAPEX_INTENSIVE_THRESHOLD = 8.0

# FCF conversion (% of Operating Profit)
FCF_EFFICIENT_THRESHOLD = 60.0
FCF_MODERATE_THRESHOLD = 30.0

# ==============================================================================
# 3. SECTOR CARVE-OUT DEFINITIONS
# ==============================================================================
FINANCIAL_SECTOR_KEYWORDS = (
    "financial",
    "bank",
    "nbfc",
    "housing finance",
    "insurance",
    "asset management",
    "lending",
)

# ==============================================================================
# 4. COMPOSITE QUALITY SCORE WEIGHTS (Total = 1.0)
# ==============================================================================
WEIGHT_PROFITABILITY = 0.35  # ROE based
WEIGHT_CASH_QUALITY = 0.30   # FCF generation and conversion
WEIGHT_GROWTH = 0.20         # 5Y PAT CAGR
WEIGHT_LEVERAGE = 0.15       # D/E ratio

# ==============================================================================
# 5. STRUCTURED LOG ANOMALY CATEGORIES
# ==============================================================================
ANOMALY_DATA_SOURCE_ISSUE = "DATA_SOURCE_ISSUE"
ANOMALY_VERSION_DIFFERENCE = "VERSION_DIFFERENCE"
ANOMALY_FORMULA_DISCREPANCY = "FORMULA_DISCREPANCY"
ANOMALY_SECTOR_CARVE_OUT = "SECTOR CARVE-OUT"
ANOMALY_DEBT_FREE = "DEBT FREE"
ANOMALY_LEVERAGE_WARNING = "LEVERAGE WARNING"
ANOMALY_CAGR_ANOMALY = "CAGR ANOMALY"
