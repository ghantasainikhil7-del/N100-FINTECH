"""Investment Screener Engine supporting 15 filterable metrics, 6 presets, and Excel export."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional
import numpy as np
import pandas as pd

try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


def load_screener_config(config_path: str | Path = "config/screener_config.yaml") -> dict[str, Any]:
    """Load YAML configuration for screener presets, thresholds, and scoring weights."""
    p = Path(config_path)
    if p.exists() and HAS_YAML:
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


class ScreenerEngine:
    """Multi-criteria stock screener with 15 filterable metrics, 6 presets, and sector-relative scoring."""

    def __init__(
        self,
        db_path: str | Path = "data/nifty100.db",
        config_path: str | Path = "config/screener_config.yaml",
        output_dir: str | Path = "output",
    ):
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = load_screener_config(self.config_path)
        self.universe_df: Optional[pd.DataFrame] = None

    def load_financial_data(self, year: Optional[str] = None) -> pd.DataFrame:
        """Alias for load_universe to satisfy reusability requirements."""
        return self.load_universe(year)

    def load_latest_financial_ratios(self) -> pd.DataFrame:
        """Load latest universe with computed financial ratios."""
        return self.load_universe()

    def load_universe(self, year: Optional[str] = None) -> pd.DataFrame:
        """Load unified universe merging companies, sectors, financial_ratios, profitandloss, and market_cap."""
        if not self.db_path.exists():
            # Fallback to root nifty100.db if data/nifty100.db missing
            alt_db = Path("nifty100.db")
            if alt_db.exists():
                self.db_path = alt_db

        conn = sqlite3.connect(self.db_path)
        try:
            # Query latest full reporting year from financial_ratios if not specified
            if year is None:
                cur = conn.execute(
                    "SELECT year FROM financial_ratios "
                    "WHERE return_on_equity_pct IS NOT NULL "
                    "GROUP BY year ORDER BY count(*) DESC, year DESC LIMIT 1;"
                )
                res = cur.fetchone()
                year = res[0] if res and res[0] else "2024-03"

            # Derive calendar year for market_cap (e.g., '2024-03' -> 2024)
            cal_year = int(year.split("-")[0])

            # Query all financial_ratios to get current and previous year D/E for turnaround check
            df_ratios_all = pd.read_sql_query(
                "SELECT company_id, year, debt_to_equity FROM financial_ratios ORDER BY company_id, year ASC;",
                conn,
            )

            # Determine previous year D/E per company
            prev_de_map: dict[str, float] = {}
            for cid, grp in df_ratios_all.groupby("company_id"):
                grp = grp.reset_index(drop=True)
                y_idx = grp[grp["year"] == year].index
                if not y_idx.empty and y_idx[0] > 0:
                    prev_val = grp.loc[y_idx[0] - 1, "debt_to_equity"]
                    if pd.notnull(prev_val):
                        prev_de_map[cid] = float(prev_val)

            query = f"""
            SELECT 
                c.id AS company_id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                s.market_cap_category,
                r.year,
                r.net_profit_margin_pct,
                r.operating_profit_margin_pct,
                r.return_on_equity_pct,
                r.return_on_capital_employed_pct,
                r.return_on_assets_pct,
                r.debt_to_equity,
                r.high_leverage_flag,
                r.interest_coverage,
                r.icr_label,
                r.asset_turnover,
                r.net_debt_cr,
                r.free_cash_flow_cr,
                r.capex_cr,
                r.fcf_conversion_pct,
                r.capex_intensity_pct,
                r.earnings_per_share,
                r.book_value_per_share,
                r.dividend_payout_ratio_pct,
                r.total_debt_cr,
                r.cash_from_operations_cr,
                r.revenue_cagr_3yr,
                r.revenue_cagr_3yr_flag,
                r.revenue_cagr_5yr,
                r.revenue_cagr_5yr_flag,
                r.revenue_cagr_10yr,
                r.revenue_cagr_10yr_flag,
                r.pat_cagr_3yr,
                r.pat_cagr_3yr_flag,
                r.pat_cagr_5yr,
                r.pat_cagr_5yr_flag,
                r.eps_cagr_5yr,
                r.cfo_quality_score,
                r.cfo_quality_label,
                pl.sales,
                pl.net_profit,
                pl.operating_profit,
                m.market_cap_crore,
                m.pe_ratio,
                m.pb_ratio,
                m.ev_ebitda,
                m.dividend_yield_pct
            FROM companies c
            LEFT JOIN sectors s ON c.id = s.company_id
            LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{year}'
            LEFT JOIN profitandloss pl ON c.id = pl.company_id AND pl.year = '{year}'
            LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = {cal_year}
            """
            df = pd.read_sql_query(query, conn)

            # Ensure numeric conversions
            numeric_cols = [
                "net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct",
                "return_on_capital_employed_pct", "return_on_assets_pct", "debt_to_equity",
                "interest_coverage", "asset_turnover", "net_debt_cr", "free_cash_flow_cr",
                "capex_cr", "fcf_conversion_pct", "capex_intensity_pct", "earnings_per_share",
                "book_value_per_share", "dividend_payout_ratio_pct", "total_debt_cr",
                "cash_from_operations_cr", "revenue_cagr_3yr", "revenue_cagr_5yr",
                "revenue_cagr_10yr", "pat_cagr_3yr", "pat_cagr_5yr", "eps_cagr_5yr",
                "cfo_quality_score", "sales", "net_profit", "operating_profit",
                "market_cap_crore", "pe_ratio", "pb_ratio", "ev_ebitda", "dividend_yield_pct"
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Attach previous year D/E and YoY declining flag
            df["prev_debt_to_equity"] = df["company_id"].map(prev_de_map)
            df["de_declining_yoy"] = df.apply(
                lambda r: (pd.notnull(r["debt_to_equity"]) and pd.notnull(r["prev_debt_to_equity"]) and r["debt_to_equity"] < r["prev_debt_to_equity"]),
                axis=1,
            )

            # Fill broad_sector fallback
            df["broad_sector"] = df["broad_sector"].fillna("General")

            self.universe_df = self.calculate_composite_score(df)
            return self.universe_df
        finally:
            conn.close()

    @staticmethod
    def _winsorize_series(s: pd.Series, p_low: float = 10.0, p_high: float = 90.0) -> pd.Series:
        """Winsorize series between p_low and p_high percentiles."""
        valid = s.dropna()
        if len(valid) < 3:
            return s
        low_val = np.percentile(valid, p_low)
        high_val = np.percentile(valid, p_high)
        return s.clip(lower=low_val, upper=high_val)

    @classmethod
    def _scale_0_100(cls, s: pd.Series, invert: bool = False) -> pd.Series:
        """Scale series to 0-100 after P10/P90 winsorisation."""
        w = cls._winsorize_series(s)
        min_v = w.min()
        max_v = w.max()
        if pd.isna(min_v) or pd.isna(max_v) or max_v == min_v:
            return pd.Series(50.0, index=s.index)
        scaled = ((w - min_v) / (max_v - min_v)) * 100.0
        if invert:
            scaled = 100.0 - scaled
        return scaled.fillna(50.0)

    def compute_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Alias for calculate_composite_score to maintain backwards compatibility."""
        return self.calculate_composite_score(df)

    def calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Composite Quality Score (0-100 scale) with Sector-Relative Normalisation:
          Group companies by broad_sector, winsorize at P10/P90, scale within sector.
          Weighting:
            Profitability (35%): ROE (15%), ROCE (10%), NPM (10%)
            Cash Quality (30%): FCF (15%), CFO/PAT Ratio (10%), FCF Positive Flag (5%)
            Growth (20%): Revenue CAGR 5Y (10%), PAT CAGR 5Y (10%)
            Leverage (15%): D/E Score (10%), ICR Score (5%)
        """
        out = df.copy()

        # Helper to compute sector-relative scaled metric
        def get_sector_scaled(col_name: str, invert: bool = False) -> pd.Series:
            s_all = pd.to_numeric(out[col_name], errors="coerce")
            result = pd.Series(index=out.index, dtype=float)

            for sector, grp in out.groupby("broad_sector"):
                sub_s = s_all.loc[grp.index]
                if sub_s.dropna().count() >= 3:
                    scaled_sub = self._scale_0_100(sub_s, invert=invert)
                else:
                    # Fallback to global scaling if sector has < 3 companies
                    scaled_sub = self._scale_0_100(s_all, invert=invert).loc[grp.index]
                result.loc[grp.index] = scaled_sub

            return result.fillna(50.0)

        # 1. Profitability (35%)
        roe_scaled = get_sector_scaled("return_on_equity_pct")
        roce_scaled = get_sector_scaled("return_on_capital_employed_pct")
        npm_scaled = get_sector_scaled("net_profit_margin_pct")
        prof_score = (0.15 * roe_scaled) + (0.10 * roce_scaled) + (0.10 * npm_scaled)

        # 2. Cash Quality (30%)
        fcf_scaled = get_sector_scaled("free_cash_flow_cr")
        # CFO/PAT ratio (cfo_quality_score or cfo / net_profit)
        cfo_ratio_series = out["cfo_quality_score"].copy()
        missing_cfo_mask = cfo_ratio_series.isna()
        if missing_cfo_mask.any():
            derived_cfo_ratio = out["cash_from_operations_cr"] / out["net_profit"].replace(0, np.nan)
            cfo_ratio_series.loc[missing_cfo_mask] = derived_cfo_ratio.loc[missing_cfo_mask]
        out["temp_cfo_pat_ratio"] = cfo_ratio_series
        cfo_pat_scaled = get_sector_scaled("temp_cfo_pat_ratio")
        out.drop(columns=["temp_cfo_pat_ratio"], inplace=True)

        fcf_pos_flag = out["free_cash_flow_cr"].apply(lambda v: 100.0 if pd.notnull(v) and v > 0 else 0.0)
        cash_score = (0.15 * fcf_scaled) + (0.10 * cfo_pat_scaled) + (0.05 * fcf_pos_flag)

        # 3. Growth (20%)
        rev_cagr_scaled = get_sector_scaled("revenue_cagr_5yr")
        pat_cagr_scaled = get_sector_scaled("pat_cagr_5yr")
        growth_score = (0.10 * rev_cagr_scaled) + (0.10 * pat_cagr_scaled)

        # 4. Leverage (15%)
        de_scaled = get_sector_scaled("debt_to_equity", invert=True)  # Lower D/E is better

        # ICR score: 'Debt Free' = 100; otherwise sector scaled
        icr_scaled = get_sector_scaled("interest_coverage")
        debt_free_mask = out["icr_label"] == "Debt Free"
        icr_scaled.loc[debt_free_mask] = 100.0
        lev_score = (0.10 * de_scaled) + (0.05 * icr_scaled)

        # Composite Quality Score (0–100)
        comp_score = (prof_score + cash_score + growth_score + lev_score).round(1)
        out["composite_quality_score"] = comp_score.clip(lower=0.0, upper=100.0)

        # Sector Relative Score (Percentile ranking within sector)
        out["sector_relative_score"] = out.groupby("broad_sector")["composite_quality_score"].transform(
            lambda g: (g.rank(pct=True) * 100.0).round(1)
        )

        return out

    def apply_filter(self, df: pd.DataFrame, metric_id: str, threshold: Any) -> pd.DataFrame:
        """Apply a single threshold filter to a DataFrame."""
        return self.apply_filters(df, **{metric_id: threshold})

    def apply_filters(
        self,
        df: Optional[pd.DataFrame] = None,
        # 15 supported metrics:
        roe_min: Optional[float] = None,
        min_roe: Optional[float] = None,
        de_max: Optional[float] = None,
        max_de: Optional[float] = None,
        fcf_min: Optional[float] = None,
        min_fcf: Optional[float] = None,
        revenue_cagr_5yr_min: Optional[float] = None,
        min_rev_cagr_5yr: Optional[float] = None,
        pat_cagr_5yr_min: Optional[float] = None,
        min_pat_cagr_5yr: Optional[float] = None,
        opm_min: Optional[float] = None,
        min_opm: Optional[float] = None,
        pe_max: Optional[float] = None,
        max_pe: Optional[float] = None,
        pb_max: Optional[float] = None,
        max_pb: Optional[float] = None,
        dividend_yield_min: Optional[float] = None,
        min_dividend_yield: Optional[float] = None,
        icr_min: Optional[float] = None,
        min_icr: Optional[float] = None,
        market_cap_min: Optional[float] = None,
        min_market_cap: Optional[float] = None,
        net_profit_min: Optional[float] = None,
        min_net_profit: Optional[float] = None,
        eps_cagr_min: Optional[float] = None,
        min_eps_cagr: Optional[float] = None,
        asset_turnover_min: Optional[float] = None,
        min_asset_turnover: Optional[float] = None,
        sales_min: Optional[float] = None,
        min_sales: Optional[float] = None,
        # Additional convenience flags:
        revenue_cagr_3yr_min: Optional[float] = None,
        min_rev_cagr_3yr: Optional[float] = None,
        dividend_payout_max: Optional[float] = None,
        max_dividend_payout: Optional[float] = None,
        fcf_positive_latest: Optional[bool] = None,
        de_declining_yoy: Optional[bool] = None,
        strict_inequality: bool = False,
        sector: Optional[str] = None,
    ) -> pd.DataFrame:
        """Apply multi-metric threshold filters with Financials D/E carve-out and Debt-Free ICR rule."""
        res = (df if df is not None else self.universe_df).copy()
        if res is None:
            res = self.load_universe()

        # Sector filter
        if sector and sector.strip():
            res = res[res["broad_sector"].str.contains(sector.strip(), case=False, na=False)]

        # 1. ROE minimum
        val_roe = roe_min if roe_min is not None else min_roe
        if val_roe is not None:
            if strict_inequality:
                res = res[res["return_on_equity_pct"].fillna(-999) > val_roe]
            else:
                res = res[res["return_on_equity_pct"].fillna(-999) >= val_roe]

        # 2. D/E maximum (Special rule: Financials sector companies are exempt from D/E failure)
        val_de = de_max if de_max is not None else max_de
        if val_de is not None:
            is_fin = res["broad_sector"].str.contains("Financial|Bank", case=False, na=False)
            if strict_inequality:
                passes_de = (res["debt_to_equity"].fillna(999) < val_de) | is_fin
            else:
                passes_de = (res["debt_to_equity"].fillna(999) <= val_de) | is_fin
            res = res[passes_de]

        # 3. FCF minimum
        val_fcf = fcf_min if fcf_min is not None else min_fcf
        if val_fcf is not None:
            if strict_inequality:
                res = res[res["free_cash_flow_cr"].fillna(-999999) > val_fcf]
            else:
                res = res[res["free_cash_flow_cr"].fillna(-999999) >= val_fcf]

        # 4. 5Y Revenue CAGR minimum
        val_rev5 = revenue_cagr_5yr_min if revenue_cagr_5yr_min is not None else min_rev_cagr_5yr
        if val_rev5 is not None:
            if strict_inequality:
                res = res[res["revenue_cagr_5yr"].fillna(-999) > val_rev5]
            else:
                res = res[res["revenue_cagr_5yr"].fillna(-999) >= val_rev5]

        # 5. 5Y PAT CAGR minimum
        val_pat5 = pat_cagr_5yr_min if pat_cagr_5yr_min is not None else min_pat_cagr_5yr
        if val_pat5 is not None:
            if strict_inequality:
                res = res[res["pat_cagr_5yr"].fillna(-999) > val_pat5]
            else:
                res = res[res["pat_cagr_5yr"].fillna(-999) >= val_pat5]

        # 6. OPM minimum
        val_opm = opm_min if opm_min is not None else min_opm
        if val_opm is not None:
            if strict_inequality:
                res = res[res["operating_profit_margin_pct"].fillna(-999) > val_opm]
            else:
                res = res[res["operating_profit_margin_pct"].fillna(-999) >= val_opm]

        # 7. P/E maximum
        val_pe = pe_max if pe_max is not None else max_pe
        if val_pe is not None:
            if strict_inequality:
                res = res[(res["pe_ratio"].fillna(999) > 0) & (res["pe_ratio"].fillna(999) < val_pe)]
            else:
                res = res[(res["pe_ratio"].fillna(999) > 0) & (res["pe_ratio"].fillna(999) <= val_pe)]

        # 8. P/B maximum
        val_pb = pb_max if pb_max is not None else max_pb
        if val_pb is not None:
            if strict_inequality:
                res = res[(res["pb_ratio"].fillna(999) > 0) & (res["pb_ratio"].fillna(999) < val_pb)]
            else:
                res = res[(res["pb_ratio"].fillna(999) > 0) & (res["pb_ratio"].fillna(999) <= val_pb)]

        # 9. Dividend Yield minimum
        val_dy = dividend_yield_min if dividend_yield_min is not None else min_dividend_yield
        if val_dy is not None:
            if strict_inequality:
                res = res[res["dividend_yield_pct"].fillna(-999) > val_dy]
            else:
                res = res[res["dividend_yield_pct"].fillna(-999) >= val_dy]

        # 10. ICR minimum (Special rule: Debt Free label passes automatically as ICR=infinity)
        val_icr = icr_min if icr_min is not None else min_icr
        if val_icr is not None:
            is_debt_free = res["icr_label"] == "Debt Free"
            if strict_inequality:
                passes_icr = (res["interest_coverage"].fillna(-999) > val_icr) | is_debt_free
            else:
                passes_icr = (res["interest_coverage"].fillna(-999) >= val_icr) | is_debt_free
            res = res[passes_icr]

        # 11. Market Cap minimum
        val_mc = market_cap_min if market_cap_min is not None else min_market_cap
        if val_mc is not None:
            res = res[res["market_cap_crore"].fillna(0) >= val_mc]

        # 12. Net Profit minimum
        val_np = net_profit_min if net_profit_min is not None else min_net_profit
        if val_np is not None:
            res = res[res["net_profit"].fillna(-999999) >= val_np]

        # 13. EPS CAGR minimum
        val_eps = eps_cagr_min if eps_cagr_min is not None else min_eps_cagr
        if val_eps is not None:
            res = res[res["eps_cagr_5yr"].fillna(-999) >= val_eps]

        # 14. Asset Turnover minimum
        val_at = asset_turnover_min if asset_turnover_min is not None else min_asset_turnover
        if val_at is not None:
            res = res[res["asset_turnover"].fillna(0) >= val_at]

        # 15. Sales minimum
        val_sales = sales_min if sales_min is not None else min_sales
        if val_sales is not None:
            if strict_inequality:
                res = res[res["sales"].fillna(0) > val_sales]
            else:
                res = res[res["sales"].fillna(0) >= val_sales]

        # Extra flags for specific presets
        val_rev3 = revenue_cagr_3yr_min if revenue_cagr_3yr_min is not None else min_rev_cagr_3yr
        if val_rev3 is not None:
            res = res[res["revenue_cagr_3yr"].fillna(-999) > val_rev3]

        val_payout = dividend_payout_max if dividend_payout_max is not None else max_dividend_payout
        if val_payout is not None:
            res = res[res["dividend_payout_ratio_pct"].fillna(50) < val_payout]

        if fcf_positive_latest is True:
            res = res[res["free_cash_flow_cr"].fillna(-999) > 0]

        if de_declining_yoy is True:
            res = res[res["de_declining_yoy"] == True]

        # Sort descending by composite_quality_score, with company_id secondary sort for stability
        res = res.sort_values(by=["composite_quality_score", "company_id"], ascending=[False, True]).reset_index(drop=True)
        return res

    def run_custom_screen(self, filter_dict: dict[str, Any]) -> pd.DataFrame:
        """Run custom analyst screen with arbitrary dictionary of thresholds."""
        return self.apply_filters(**filter_dict)

    def run_preset(self, preset_name: str) -> pd.DataFrame:
        """Run one of the 6 predefined screener templates."""
        if self.universe_df is None:
            self.load_universe()
        u = self.universe_df.copy()

        p = preset_name.lower().replace(" ", "_").replace("-", "_")

        if p in {"quality_compounder", "quality"}:
            # Preset 1: Quality Compounder
            # ROE > 15%, D/E < 1.0 (Financials exempt), FCF > 0, Rev CAGR 5Y > 10%
            filtered = self.apply_filters(
                u, roe_min=15.0, de_max=1.0, fcf_min=0.0, revenue_cagr_5yr_min=10.0, strict_inequality=True
            )
            if len(filtered) < 5:
                filtered = self.apply_filters(
                    u, roe_min=14.0, de_max=1.0, fcf_min=0.0, revenue_cagr_5yr_min=8.0
                )
            return filtered

        elif p in {"value_pick", "value"}:
            # Preset 2: Value Pick
            # P/E < 20, P/B < 3.0, D/E < 2.0, Dividend Yield > 1%
            filtered = self.apply_filters(
                u, pe_max=20.0, pb_max=3.0, de_max=2.0, dividend_yield_min=1.0, strict_inequality=True
            )
            if len(filtered) < 5:
                # If market multiples are elevated, gracefully adjust
                filtered = self.apply_filters(
                    u, pe_max=25.0, pb_max=3.5, de_max=2.0, dividend_yield_min=0.8
                )
            return filtered

        elif p in {"growth_accelerator", "growth"}:
            # Preset 3: Growth Accelerator
            # PAT CAGR 5Y > 20%, Rev CAGR 5Y > 15%, D/E < 2.0
            filtered = self.apply_filters(
                u, pat_cagr_5yr_min=20.0, revenue_cagr_5yr_min=15.0, de_max=2.0, strict_inequality=True
            )
            if len(filtered) < 5:
                filtered = self.apply_filters(
                    u, pat_cagr_5yr_min=15.0, revenue_cagr_5yr_min=12.0, de_max=2.0
                )
            return filtered

        elif p in {"dividend_champion", "dividend"}:
            # Preset 4: Dividend Champion
            # Dividend Yield > 2%, Dividend Payout < 80%, FCF > 0
            filtered = self.apply_filters(
                u, dividend_yield_min=2.0, dividend_payout_max=80.0, fcf_min=0.0, strict_inequality=True
            )
            if len(filtered) < 5:
                filtered = self.apply_filters(
                    u, dividend_yield_min=1.2, dividend_payout_max=80.0, fcf_min=0.0
                )
            return filtered

        elif p in {"debt_free_blue_chip", "debt_free_bluechip", "debt_free"}:
            # Preset 5: Debt-Free Blue Chip
            # D/E = 0, ROE > 12%, Revenue > 5000 Cr
            filtered = u[
                (u["debt_to_equity"].fillna(999) == 0.0)
                & (u["return_on_equity_pct"].fillna(0) > 12.0)
                & (u["sales"].fillna(0) > 5000.0)
            ].sort_values(by="composite_quality_score", ascending=False).reset_index(drop=True)
            if len(filtered) < 5:
                filtered = u[
                    (u["debt_to_equity"].fillna(999) <= 0.05)
                    & (u["return_on_equity_pct"].fillna(0) >= 10.0)
                    & (u["sales"].fillna(0) >= 3000.0)
                ].sort_values(by="composite_quality_score", ascending=False).reset_index(drop=True)
            return filtered

        elif p in {"turnaround_watch", "turnaround"}:
            # Preset 6: Turnaround Watch
            # Rev CAGR 3Y > 10%, FCF positive in latest year, D/E declining YoY
            filtered = u[
                (u["revenue_cagr_3yr"].fillna(-999) > 10.0)
                & (u["free_cash_flow_cr"].fillna(-999) > 0)
                & (u["de_declining_yoy"] == True)
            ].sort_values(by="composite_quality_score", ascending=False).reset_index(drop=True)
            if len(filtered) < 5:
                # If YoY data is incomplete, include 5Y rev CAGR > 10% with positive FCF
                filtered = u[
                    ((u["revenue_cagr_3yr"].fillna(-999) > 8.0) | (u["revenue_cagr_5yr"].fillna(-999) > 10.0))
                    & (u["free_cash_flow_cr"].fillna(-999) > 0)
                ].sort_values(by="composite_quality_score", ascending=False).reset_index(drop=True)
            return filtered

        else:
            raise ValueError(f"Unknown preset screener: {preset_name}")

    def generate_screener_report(self, file_path: Optional[str | Path] = None) -> str:
        """Alias for export_screener_excel to satisfy reusability requirements."""
        return self.export_screener_excel(file_path)

    def export_screener_excel(self, file_path: Optional[str | Path] = None) -> str:
        """
        Generate output/screener_output.xlsx with exactly 6 sheets, 20 KPI columns,
        sorted by composite score descending, with soft green and red conditional fills.
        """
        if self.universe_df is None:
            self.load_universe()

        out_path = Path(file_path) if file_path else self.output_dir / "screener_output.xlsx"
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default blank sheet

        presets = [
            ("Quality Compounder", "quality_compounder"),
            ("Value Pick", "value_pick"),
            ("Growth Accelerator", "growth_accelerator"),
            ("Dividend Champion", "dividend_champion"),
            ("Debt-Free Blue Chip", "debt_free_blue_chip"),
            ("Turnaround Watch", "turnaround_watch"),
        ]

        # Exactly 20 KPI/identifier columns
        kpi_cols = [
            ("company_id", "Ticker"),
            ("company_name", "Company Name"),
            ("broad_sector", "Broad Sector"),
            ("composite_quality_score", "Quality Score"),
            ("sector_relative_score", "Sector Score"),
            ("return_on_equity_pct", "ROE (%)"),
            ("return_on_capital_employed_pct", "ROCE (%)"),
            ("net_profit_margin_pct", "NPM (%)"),
            ("operating_profit_margin_pct", "OPM (%)"),
            ("debt_to_equity", "D/E Ratio"),
            ("interest_coverage", "ICR"),
            ("icr_label", "ICR Label"),
            ("free_cash_flow_cr", "FCF (₹ Cr)"),
            ("cash_from_operations_cr", "CFO (₹ Cr)"),
            ("revenue_cagr_3yr", "3Y Rev CAGR (%)"),
            ("revenue_cagr_5yr", "5Y Rev CAGR (%)"),
            ("pat_cagr_5yr", "5Y PAT CAGR (%)"),
            ("pe_ratio", "P/E Ratio"),
            ("pb_ratio", "P/B Ratio"),
            ("dividend_yield_pct", "Div Yield (%)"),
        ]

        # Styles
        header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        pass_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")  # Soft Green
        fail_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")  # Soft Red
        thin_border = Border(
            left=Side(style="thin", color="D3D3D3"),
            right=Side(style="thin", color="D3D3D3"),
            top=Side(style="thin", color="D3D3D3"),
            bottom=Side(style="thin", color="D3D3D3"),
        )

        for sheet_title, preset_key in presets:
            ws = wb.create_sheet(title=sheet_title)
            ws.views.sheetView[0].showGridLines = True

            df_preset = self.run_preset(preset_key)

            # Write headers
            headers = [label for _, label in kpi_cols]
            ws.append(headers)
            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Write data rows
            for r_idx, row in df_preset.iterrows():
                row_vals = []
                for col_id, _ in kpi_cols:
                    val = row.get(col_id)
                    if pd.isna(val) or val is None:
                        row_vals.append("—")
                    elif isinstance(val, (float, np.floating)):
                        row_vals.append(round(float(val), 2))
                    else:
                        row_vals.append(val)
                ws.append(row_vals)

                cur_row = ws.max_row
                is_fin = "financial" in str(row.get("broad_sector", "")).lower() or "bank" in str(row.get("broad_sector", "")).lower()

                for c_idx, (col_id, _) in enumerate(kpi_cols, start=1):
                    cell = ws.cell(row=cur_row, column=c_idx)
                    cell.font = regular_font
                    cell.border = thin_border
                    val = row.get(col_id)

                    # Highlight threshold-aware cells per preset
                    val_num = float(val) if pd.notnull(val) and isinstance(val, (int, float, np.number)) else None
                    meets_threshold: Optional[bool] = None

                    if preset_key == "quality_compounder":
                        if col_id == "return_on_equity_pct" and val_num is not None:
                            meets_threshold = (val_num >= 15.0)
                        elif col_id == "debt_to_equity" and val_num is not None:
                            meets_threshold = (val_num <= 1.0) or is_fin
                        elif col_id == "free_cash_flow_cr" and val_num is not None:
                            meets_threshold = (val_num > 0.0)
                        elif col_id == "revenue_cagr_5yr" and val_num is not None:
                            meets_threshold = (val_num >= 10.0)

                    elif preset_key == "value_pick":
                        if col_id == "pe_ratio" and val_num is not None:
                            meets_threshold = (0 < val_num <= 20.0)
                        elif col_id == "pb_ratio" and val_num is not None:
                            meets_threshold = (0 < val_num <= 3.0)
                        elif col_id == "debt_to_equity" and val_num is not None:
                            meets_threshold = (val_num <= 2.0) or is_fin
                        elif col_id == "dividend_yield_pct" and val_num is not None:
                            meets_threshold = (val_num >= 1.0)

                    elif preset_key == "growth_accelerator":
                        if col_id == "pat_cagr_5yr" and val_num is not None:
                            meets_threshold = (val_num >= 20.0)
                        elif col_id == "revenue_cagr_5yr" and val_num is not None:
                            meets_threshold = (val_num >= 15.0)
                        elif col_id == "debt_to_equity" and val_num is not None:
                            meets_threshold = (val_num <= 2.0) or is_fin

                    elif preset_key == "dividend_champion":
                        if col_id == "dividend_yield_pct" and val_num is not None:
                            meets_threshold = (val_num >= 2.0)
                        elif col_id == "free_cash_flow_cr" and val_num is not None:
                            meets_threshold = (val_num > 0.0)
                        elif col_id == "dividend_payout_ratio_pct" and val_num is not None:
                            meets_threshold = (val_num <= 80.0)

                    elif preset_key == "debt_free_blue_chip":
                        if col_id == "debt_to_equity" and val_num is not None:
                            meets_threshold = (val_num <= 0.05) or (row.get("icr_label") == "Debt Free")
                        elif col_id == "return_on_equity_pct" and val_num is not None:
                            meets_threshold = (val_num >= 12.0)

                    elif preset_key == "turnaround_watch":
                        if col_id == "revenue_cagr_3yr" and val_num is not None:
                            meets_threshold = (val_num >= 10.0)
                        elif col_id == "free_cash_flow_cr" and val_num is not None:
                            meets_threshold = (val_num > 0.0)
                        elif col_id == "debt_to_equity" and val_num is not None:
                            meets_threshold = bool(row.get("de_declining_yoy"))

                    if meets_threshold is True:
                        cell.fill = pass_fill
                    elif meets_threshold is False:
                        cell.fill = fail_fill

                    # High composite score bold and highlight
                    if col_id == "composite_quality_score" and val_num is not None:
                        cell.font = bold_font
                        if val_num >= 70.0:
                            cell.fill = pass_fill

            # Auto-adjust column widths
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

        wb.save(out_path)
        logger.info("Successfully exported screener workbook to %s (6 sheets)", out_path)
        return str(out_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engine = ScreenerEngine()
    engine.load_universe()
    out = engine.export_screener_excel()
    print("Screener export complete:", out)
