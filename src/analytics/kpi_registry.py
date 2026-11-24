"""Machine-readable KPI Registry tracking all explicitly specified and extension KPIs."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional


class KpiStatus(str, Enum):
    SPEC = "SPEC"                # Explicitly required by original Sprint 2 specification
    EXTENSION = "EXTENSION"      # Mathematically sound analytical extension derived from statement data


class KpiCategory(str, Enum):
    PROFITABILITY = "PROFITABILITY"
    LEVERAGE = "LEVERAGE"
    EFFICIENCY = "EFFICIENCY"
    GROWTH = "GROWTH"
    CASH_FLOW = "CASH_FLOW"
    VALUATION = "VALUATION"
    QUALITY = "QUALITY"


@dataclass(frozen=True)
class KpiDefinition:
    kpi_id: str
    name: str
    category: KpiCategory
    status: KpiStatus
    formula: str
    unit: str
    db_column: Optional[str]
    description: str
    edge_cases: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["status"] = self.status.value
        return d


# Complete catalog of 50+ KPIs
KPI_CATALOG: list[KpiDefinition] = [
    # --------------------------------------------------------------------------
    # 1. SPEC PROFITABILITY & RETURNS (5)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="NPM",
        name="Net Profit Margin",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.SPEC,
        formula="(Net Profit / Sales) * 100",
        unit="%",
        db_column="net_profit_margin_pct",
        description="Percentage of revenue remaining as profit after all expenses, interest, and taxes.",
        edge_cases="Returns None if sales <= 0 or missing.",
    ),
    KpiDefinition(
        kpi_id="OPM",
        name="Operating Profit Margin",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.SPEC,
        formula="(Operating Profit / Sales) * 100",
        unit="%",
        db_column="operating_profit_margin_pct",
        description="Operating efficiency before non-operating income, interest, and tax.",
        edge_cases="Returns None if sales <= 0. Cross-checked with source opm_percentage within 1% tolerance.",
    ),
    KpiDefinition(
        kpi_id="ROE",
        name="Return on Equity",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.SPEC,
        formula="(Net Profit / (Equity Capital + Reserves)) * 100",
        unit="%",
        db_column="return_on_equity_pct",
        description="Return generated on shareholders' book equity capital and retained earnings.",
        edge_cases="Returns None if total equity <= 0. Logged as DATA_SOURCE_ISSUE if equity negative.",
    ),
    KpiDefinition(
        kpi_id="ROCE",
        name="Return on Capital Employed",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.SPEC,
        formula="(EBIT / (Equity Capital + Reserves + Borrowings)) * 100",
        unit="%",
        db_column="return_on_capital_employed_pct",
        description="Operating return generated per unit of total capital invested (equity + debt).",
        edge_cases="EBIT = Operating Profit - Depreciation. Returns None if capital employed <= 0. Financial sector carve-out.",
    ),
    KpiDefinition(
        kpi_id="ROA",
        name="Return on Assets",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.SPEC,
        formula="(Net Profit / Total Assets) * 100",
        unit="%",
        db_column="return_on_assets_pct",
        description="Profitability relative to total balance sheet asset base.",
        edge_cases="Returns None if total assets <= 0 or missing.",
    ),

    # --------------------------------------------------------------------------
    # 2. SPEC LEVERAGE & EFFICIENCY (6)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="DE",
        name="Debt to Equity Ratio",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="Borrowings / (Equity Capital + Reserves)",
        unit="ratio",
        db_column="debt_to_equity",
        description="Ratio of total borrowed funds to shareholder equity.",
        edge_cases="Returns 0.0 when borrowings == 0 (Debt Free). Returns None if equity <= 0.",
    ),
    KpiDefinition(
        kpi_id="HIGH_LEV_FLAG",
        name="High Leverage Flag",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="1 if (D/E > 5.0 and sector != Financials) else 0",
        unit="flag",
        db_column="high_leverage_flag",
        description="Alert indicating excessive leverage risk; suppressed for banks and NBFCs.",
        edge_cases="Banks and NBFCs exempt due to inherent deposit/borrowing business model.",
    ),
    KpiDefinition(
        kpi_id="ICR",
        name="Interest Coverage Ratio",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="(Operating Profit + Other Income) / Interest",
        unit="ratio",
        db_column="interest_coverage",
        description="Ability of pre-interest earnings to service annual interest obligations.",
        edge_cases="Returns None when interest == 0. Warning triggered when ICR < 1.5.",
    ),
    KpiDefinition(
        kpi_id="ICR_LABEL",
        name="Interest Coverage Label",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="'Debt Free' if interest == 0 else ('At Risk' if ICR < 1.5 else 'Normal')",
        unit="text",
        db_column="icr_label",
        description="Qualitative solvency status classification based on ICR threshold.",
        edge_cases="'Debt Free' for zero interest expense.",
    ),
    KpiDefinition(
        kpi_id="ASSET_TURNOVER",
        name="Asset Turnover",
        category=KpiCategory.EFFICIENCY,
        status=KpiStatus.SPEC,
        formula="Sales / Total Assets",
        unit="ratio",
        db_column="asset_turnover",
        description="Revenue generating efficiency per rupee of balance sheet assets.",
        edge_cases="Returns None if total assets <= 0 or missing.",
    ),
    KpiDefinition(
        kpi_id="NET_DEBT",
        name="Net Debt",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="Borrowings - (Investments + Cash)",
        unit="Cr",
        db_column="net_debt_cr",
        description="Net indebtedness after netting out cash equivalents and liquid investments. Negative = Net Cash.",
        edge_cases="Investments used as primary liquid asset proxy.",
    ),

    # --------------------------------------------------------------------------
    # 3. SPEC CASH FLOW & CAPITAL ALLOCATION (9)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="FCF",
        name="Free Cash Flow",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="Operating Cash Flow + Investing Cash Flow",
        unit="Cr",
        db_column="free_cash_flow_cr",
        description="Cash generated after accounting for all capital expenditure cash outflows.",
        edge_cases="Negative values allowed; accurately depicts capital expansion deficits.",
    ),
    KpiDefinition(
        kpi_id="CAPEX",
        name="Capital Expenditure",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="abs(Investing Cash Flow)",
        unit="Cr",
        db_column="capex_cr",
        description="Cash allocated to plant, property, equipment, and strategic investments.",
        edge_cases="Defaults to 0.0 if CFI missing.",
    ),
    KpiDefinition(
        kpi_id="FCF_CONVERSION",
        name="FCF Conversion Rate",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="(Free Cash Flow / Operating Profit) * 100",
        unit="%",
        db_column="fcf_conversion_pct",
        description="Percentage of operating profit converted into usable free cash flow.",
        edge_cases="Returns None if operating profit <= 0.",
    ),
    KpiDefinition(
        kpi_id="CAPEX_INTENSITY",
        name="CapEx Intensity",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="(abs(Investing Cash Flow) / Sales) * 100",
        unit="%",
        db_column="capex_intensity_pct",
        description="Capital expenditure as a percentage of annual top-line revenue.",
        edge_cases="Returns None if sales <= 0. Categorized into Asset Light (<3%), Moderate (3-8%), Intensive (>8%).",
    ),
    KpiDefinition(
        kpi_id="CFO",
        name="Cash Flow from Operations",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="Operating Activity Cash Flow",
        unit="Cr",
        db_column="cash_from_operations_cr",
        description="Pure cash generated directly from core business operations.",
        edge_cases="Negative values indicate operational cash burn.",
    ),
    KpiDefinition(
        kpi_id="TOTAL_DEBT",
        name="Total Debt",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.SPEC,
        formula="Borrowings",
        unit="Cr",
        db_column="total_debt_cr",
        description="Total borrowings on the balance sheet.",
        edge_cases="0.0 if debt free.",
    ),
    KpiDefinition(
        kpi_id="CFO_QUALITY_SCORE",
        name="CFO Earnings Quality Score",
        category=KpiCategory.QUALITY,
        status=KpiStatus.SPEC,
        formula="sum(CFO_5Y) / sum(PAT_5Y)",
        unit="ratio",
        db_column="cfo_quality_score",
        description="Multi-year cash conversion quality; checks whether accounting profits are backed by cash.",
        edge_cases="Returns None if valid PAT sum is 0 or data insufficient.",
    ),
    KpiDefinition(
        kpi_id="CFO_QUALITY_LABEL",
        name="CFO Earnings Quality Label",
        category=KpiCategory.QUALITY,
        status=KpiStatus.SPEC,
        formula="'High Quality' if score > 1.0 else ('Moderate' if score >= 0.5 else 'Accrual Risk')",
        unit="text",
        db_column="cfo_quality_label",
        description="Earnings quality tier based on 5-year cumulative CFO / PAT ratio.",
        edge_cases="'Insufficient Data' if history is incomplete.",
    ),
    KpiDefinition(
        kpi_id="CAPITAL_ALLOCATION_PATTERN",
        name="Capital Allocation Pattern",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.SPEC,
        formula="8-pattern classification from (sgn(CFO), sgn(CFI), sgn(CFF))",
        unit="text",
        db_column=None,
        description="Corporate finance lifecycle pattern: Reinvestor, Shareholder Returns, Distress, etc.",
        edge_cases="Exported directly to output/capital_allocation.csv.",
    ),

    # --------------------------------------------------------------------------
    # 4. SPEC VALUATION & PER-SHARE METRICS (3)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="EPS",
        name="Earnings Per Share",
        category=KpiCategory.VALUATION,
        status=KpiStatus.SPEC,
        formula="Reported Diluted/Basic EPS",
        unit="₹",
        db_column="earnings_per_share",
        description="Net income attributable per equity share outstanding.",
        edge_cases="Populated from annual statement records.",
    ),
    KpiDefinition(
        kpi_id="BVPS",
        name="Book Value Per Share",
        category=KpiCategory.VALUATION,
        status=KpiStatus.SPEC,
        formula="(Equity Capital + Reserves) / (Equity Capital / Face Value)",
        unit="₹",
        db_column="book_value_per_share",
        description="Net book worth backing each issued equity share.",
        edge_cases="Face value normalized to 1.0 if not specified.",
    ),
    KpiDefinition(
        kpi_id="DIVIDEND_PAYOUT",
        name="Dividend Payout Ratio",
        category=KpiCategory.VALUATION,
        status=KpiStatus.SPEC,
        formula="Dividend Payout %",
        unit="%",
        db_column="dividend_payout_ratio_pct",
        description="Percentage of net earnings distributed to shareholders as dividends.",
        edge_cases="Captured directly from statement disclosures.",
    ),

    # --------------------------------------------------------------------------
    # 5. SPEC CAGR GROWTH METRICS & FLAGS (18)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="REV_CAGR_3Y",
        name="Revenue CAGR (3-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((Sales_T / Sales_T-3) ** (1/3) - 1) * 100",
        unit="%",
        db_column="revenue_cagr_3yr",
        description="3-year compound annual growth rate of top-line revenue.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="REV_CAGR_3Y_FLAG",
        name="Revenue CAGR 3Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="revenue_cagr_3yr_flag",
        description="Qualifies validity of 3Y Revenue CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="REV_CAGR_5Y",
        name="Revenue CAGR (5-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((Sales_T / Sales_T-5) ** (1/5) - 1) * 100",
        unit="%",
        db_column="revenue_cagr_5yr",
        description="5-year compound annual growth rate of top-line revenue.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="REV_CAGR_5Y_FLAG",
        name="Revenue CAGR 5Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="revenue_cagr_5yr_flag",
        description="Qualifies validity of 5Y Revenue CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="REV_CAGR_10Y",
        name="Revenue CAGR (10-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((Sales_T / Sales_T-10) ** (1/10) - 1) * 100",
        unit="%",
        db_column="revenue_cagr_10yr",
        description="10-year long-term compound annual growth rate of top-line revenue.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="REV_CAGR_10Y_FLAG",
        name="Revenue CAGR 10Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="revenue_cagr_10yr_flag",
        description="Qualifies validity of 10Y Revenue CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_3Y",
        name="PAT CAGR (3-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((PAT_T / PAT_T-3) ** (1/3) - 1) * 100",
        unit="%",
        db_column="pat_cagr_3yr",
        description="3-year compound annual growth rate of net bottom-line profit.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_3Y_FLAG",
        name="PAT CAGR 3Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="pat_cagr_3yr_flag",
        description="Qualifies validity of 3Y PAT CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_5Y",
        name="PAT CAGR (5-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((PAT_T / PAT_T-5) ** (1/5) - 1) * 100",
        unit="%",
        db_column="pat_cagr_5yr",
        description="5-year compound annual growth rate of net bottom-line profit.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_5Y_FLAG",
        name="PAT CAGR 5Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="pat_cagr_5yr_flag",
        description="Qualifies validity of 5Y PAT CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_10Y",
        name="PAT CAGR (10-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((PAT_T / PAT_T-10) ** (1/10) - 1) * 100",
        unit="%",
        db_column="pat_cagr_10yr",
        description="10-year long-term compound annual growth rate of net bottom-line profit.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="PAT_CAGR_10Y_FLAG",
        name="PAT CAGR 10Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="pat_cagr_10yr_flag",
        description="Qualifies validity of 10Y PAT CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_3Y",
        name="EPS CAGR (3-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((EPS_T / EPS_T-3) ** (1/3) - 1) * 100",
        unit="%",
        db_column="eps_cagr_3yr",
        description="3-year compound annual growth rate of per-share earnings.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_3Y_FLAG",
        name="EPS CAGR 3Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="eps_cagr_3yr_flag",
        description="Qualifies validity of 3Y EPS CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_5Y",
        name="EPS CAGR (5-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((EPS_T / EPS_T-5) ** (1/5) - 1) * 100",
        unit="%",
        db_column="eps_cagr_5yr",
        description="5-year compound annual growth rate of per-share earnings.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_5Y_FLAG",
        name="EPS CAGR 5Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="eps_cagr_5yr_flag",
        description="Qualifies validity of 5Y EPS CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_10Y",
        name="EPS CAGR (10-Year)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="((EPS_T / EPS_T-10) ** (1/10) - 1) * 100",
        unit="%",
        db_column="eps_cagr_10yr",
        description="10-year long-term compound annual growth rate of per-share earnings.",
        edge_cases="None if turnaround, decline to loss, negative base, or insufficient years.",
    ),
    KpiDefinition(
        kpi_id="EPS_CAGR_10Y_FLAG",
        name="EPS CAGR 10Y Edge Case Flag",
        category=KpiCategory.GROWTH,
        status=KpiStatus.SPEC,
        formula="Flag: NORMAL, DECLINE_TO_LOSS, TURNAROUND, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT",
        unit="text",
        db_column="eps_cagr_10yr_flag",
        description="Qualifies validity of 10Y EPS CAGR mathematical calculation.",
        edge_cases="Strictly categorized across 6 canonical flags.",
    ),

    # --------------------------------------------------------------------------
    # 6. SPEC COMPOSITE QUALITY (1)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="COMPOSITE_QUALITY_SCORE",
        name="Composite Quality Score",
        category=KpiCategory.QUALITY,
        status=KpiStatus.SPEC,
        formula="(0.35 * ROE_score) + (0.30 * Cash_score) + (0.20 * Growth_score) + (0.15 * Lev_score)",
        unit="score",
        db_column="composite_quality_score",
        description="0-100 composite index balancing profitability, cash generation, growth, and leverage safety.",
        edge_cases="Components normalized linearly from 0 to 100.",
    ),

    # --------------------------------------------------------------------------
    # 7. DERIVED IMPLEMENTATION EXTENSIONS (12)
    # --------------------------------------------------------------------------
    KpiDefinition(
        kpi_id="EBITDA_MARGIN",
        name="EBITDA Margin",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.EXTENSION,
        formula="((Operating Profit + Other Income) / Sales) * 100",
        unit="%",
        db_column=None,
        description="Operating profitability before interest, tax, depreciation, and amortization.",
        edge_cases="Returns None if sales <= 0.",
    ),
    KpiDefinition(
        kpi_id="EBIT_MARGIN",
        name="EBIT Margin",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.EXTENSION,
        formula="(EBIT / Sales) * 100",
        unit="%",
        db_column=None,
        description="Pure operating earnings yield on revenue after full depreciation charges.",
        edge_cases="Returns None if sales <= 0.",
    ),
    KpiDefinition(
        kpi_id="EFFECTIVE_TAX_RATE",
        name="Effective Tax Rate",
        category=KpiCategory.PROFITABILITY,
        status=KpiStatus.EXTENSION,
        formula="((Profit Before Tax - Net Profit) / Profit Before Tax) * 100",
        unit="%",
        db_column=None,
        description="Effective corporate taxation burden on declared pre-tax earnings.",
        edge_cases="Returns None if PBT <= 0.",
    ),
    KpiDefinition(
        kpi_id="FINANCIAL_LEVERAGE_MULTIPLIER",
        name="Financial Leverage Multiplier (Equity Multiplier)",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.EXTENSION,
        formula="Total Assets / (Equity Capital + Reserves)",
        unit="ratio",
        db_column=None,
        description="DuPont identity financial leverage factor measuring asset gearing per unit of equity.",
        edge_cases="Returns None if equity <= 0.",
    ),
    KpiDefinition(
        kpi_id="DEBT_TO_ASSETS",
        name="Debt to Assets Ratio",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.EXTENSION,
        formula="Borrowings / Total Assets",
        unit="ratio",
        db_column=None,
        description="Fraction of total asset base financed through borrowed debt capital.",
        edge_cases="Returns 0.0 if borrowings == 0; None if total assets <= 0.",
    ),
    KpiDefinition(
        kpi_id="NET_DEBT_TO_EBITDA",
        name="Net Debt to EBITDA",
        category=KpiCategory.LEVERAGE,
        status=KpiStatus.EXTENSION,
        formula="Net Debt / (Operating Profit + Other Income)",
        unit="ratio",
        db_column=None,
        description="Standard credit agency solvency metric measuring years needed to repay net debt.",
        edge_cases="Returns 0.0 if net debt <= 0; None if EBITDA <= 0.",
    ),
    KpiDefinition(
        kpi_id="CFO_MARGIN",
        name="Cash Flow from Operations Margin",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.EXTENSION,
        formula="(Cash from Operations / Sales) * 100",
        unit="%",
        db_column=None,
        description="Cash conversion efficiency relative to top-line turnover.",
        edge_cases="Returns None if sales <= 0.",
    ),
    KpiDefinition(
        kpi_id="CFO_TO_DEBT",
        name="Cash Flow to Debt Ratio",
        category=KpiCategory.CASH_FLOW,
        status=KpiStatus.EXTENSION,
        formula="Cash from Operations / Borrowings",
        unit="ratio",
        db_column=None,
        description="Annual cash flow available to retire principal debt outstanding.",
        edge_cases="Returns None if borrowings == 0 (Debt Free).",
    ),
    KpiDefinition(
        kpi_id="RETENTION_RATIO",
        name="Retention Ratio (Plowback Ratio)",
        category=KpiCategory.QUALITY,
        status=KpiStatus.EXTENSION,
        formula="100.0 - Dividend Payout %",
        unit="%",
        db_column=None,
        description="Percentage of net earnings retained inside the business for reinvestment.",
        edge_cases="Capped at 100% if dividend payout is negative or zero.",
    ),
    KpiDefinition(
        kpi_id="SUSTAINABLE_GROWTH_RATE",
        name="Sustainable Growth Rate (SGR)",
        category=KpiCategory.GROWTH,
        status=KpiStatus.EXTENSION,
        formula="(ROE * (100.0 - Dividend Payout %)) / 100.0",
        unit="%",
        db_column=None,
        description="Maximum rate of growth achievable without issuing external equity or increasing leverage.",
        edge_cases="Returns None if ROE is None.",
    ),
    KpiDefinition(
        kpi_id="FIXED_ASSET_TURNOVER",
        name="Fixed Asset Turnover",
        category=KpiCategory.EFFICIENCY,
        status=KpiStatus.EXTENSION,
        formula="Sales / Net Fixed Assets",
        unit="ratio",
        db_column=None,
        description="Capital efficiency ratio indicating how effectively company utilizes plant and equipment.",
        edge_cases="Returns None if fixed assets <= 0 or missing.",
    ),
    KpiDefinition(
        kpi_id="WORKING_CAPITAL_TURNOVER",
        name="Working Capital Turnover",
        category=KpiCategory.EFFICIENCY,
        status=KpiStatus.EXTENSION,
        formula="Sales / Working Capital",
        unit="ratio",
        db_column=None,
        description="Turnover of operational net current assets generating top-line revenue.",
        edge_cases="Returns None if working capital is 0 or negative.",
    ),
]


class KpiRegistry:
    """Registry providing lookups, filters, and inspection over all 50+ KPIs."""

    def __init__(self, catalog: list[KpiDefinition] = KPI_CATALOG):
        self._catalog = list(catalog)
        self._by_id = {kpi.kpi_id: kpi for kpi in self._catalog}

    def get(self, kpi_id: str) -> Optional[KpiDefinition]:
        """Lookup KPI by ID."""
        return self._by_id.get(kpi_id)

    def all_kpis(self) -> list[KpiDefinition]:
        """Return all cataloged KPIs."""
        return list(self._catalog)

    def filter_by_status(self, status: KpiStatus | str) -> list[KpiDefinition]:
        """Filter KPIs by SPEC vs EXTENSION."""
        stat_val = status.value if isinstance(status, KpiStatus) else str(status).upper()
        return [k for k in self._catalog if k.status.value == stat_val]

    def filter_by_category(self, category: KpiCategory | str) -> list[KpiDefinition]:
        """Filter KPIs by functional category."""
        cat_val = category.value if isinstance(category, KpiCategory) else str(category).upper()
        return [k for k in self._catalog if k.category.value == cat_val]

    def summary(self) -> dict[str, Any]:
        """Return summary statistics of KPI registry."""
        spec_list = self.filter_by_status(KpiStatus.SPEC)
        ext_list = self.filter_by_status(KpiStatus.EXTENSION)
        return {
            "total_kpis": len(self._catalog),
            "spec_count": len(spec_list),
            "extension_count": len(ext_list),
            "categories": {cat.value: len(self.filter_by_category(cat)) for cat in KpiCategory},
        }


# Global registry singleton
registry = KpiRegistry()
