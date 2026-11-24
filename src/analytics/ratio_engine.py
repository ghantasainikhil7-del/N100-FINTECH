"""Financial Ratio Engine Orchestrator for Nifty 100 Financial Intelligence Platform.

Computes 50+ KPIs across all 92 companies and available years, populates SQLite
database (financial_ratios table), and generates audit deliverables.
"""
from __future__ import annotations

import logging
import os
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import pandas as pd

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
    classify_pattern,
    export_capital_allocation_csv,
)
from src.analytics.cashflow_kpis import (
    compute_capex_intensity,
    compute_cfo_quality_score,
    compute_fcf_conversion_rate,
    compute_free_cash_flow,
)
from src.analytics.ratio_config import (
    ANOMALY_CAGR_ANOMALY,
    ANOMALY_DATA_SOURCE_ISSUE,
    ANOMALY_DEBT_FREE,
    ANOMALY_FORMULA_DISCREPANCY,
    ANOMALY_LEVERAGE_WARNING,
    ANOMALY_SECTOR_CARVE_OUT,
    ANOMALY_VERSION_DIFFERENCE,
    CAPITAL_ALLOCATION_CSV,
    DEFAULT_DB_PATH,
    DEFAULT_OUTPUT_DIR,
    FINANCIAL_SECTOR_KEYWORDS,
    HIGH_LEVERAGE_THRESHOLD,
    INTEREST_COVERAGE_RISK_THRESHOLD,
    MIRROR_DB_PATH,
    OPM_CROSS_CHECK_TOLERANCE,
    RATIO_EDGE_CASES_LOG,
    ROCE_CROSS_CHECK_TOLERANCE,
    WEIGHT_CASH_QUALITY,
    WEIGHT_GROWTH,
    WEIGHT_LEVERAGE,
    WEIGHT_PROFITABILITY,
)
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

logger = logging.getLogger(__name__)


class RatioEngine:
    """Computes all KPIs across companies and years, populating SQLite and deliverables."""

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
        mirror_db_path: Optional[str | Path] = MIRROR_DB_PATH,
        output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    ):
        self.db_path = Path(db_path)
        self.mirror_db_path = Path(mirror_db_path) if mirror_db_path else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.edge_case_logs: list[str] = []
        self.capital_allocations: list[dict[str, Any]] = []

    def log_edge_case(self, category: str, ticker: str, year: Optional[str], detail: str) -> None:
        """Log formula edge case or anomaly with category and timestamp."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{now_str}] [{category}] [{ticker}] [Year: {year or 'N/A'}] {detail}"
        self.edge_case_logs.append(entry)
        logger.debug(entry)

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Ensure financial_ratios table exists with all required Sprint 2 columns."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS financial_ratios (
            company_id VARCHAR(16) NOT NULL,
            year VARCHAR(7) NOT NULL,
            net_profit_margin_pct NUMERIC,
            operating_profit_margin_pct NUMERIC,
            return_on_equity_pct NUMERIC,
            return_on_capital_employed_pct NUMERIC,
            return_on_assets_pct NUMERIC,
            debt_to_equity NUMERIC,
            high_leverage_flag INTEGER DEFAULT 0,
            interest_coverage NUMERIC,
            icr_label VARCHAR(20) DEFAULT 'Normal',
            asset_turnover NUMERIC,
            net_debt_cr NUMERIC,
            free_cash_flow_cr NUMERIC,
            free_cash_flow_crore NUMERIC,
            capex_cr NUMERIC,
            capex_crore NUMERIC,
            fcf_conversion_pct NUMERIC,
            capex_intensity_pct NUMERIC,
            earnings_per_share NUMERIC,
            book_value_per_share NUMERIC,
            dividend_payout_ratio_pct NUMERIC,
            total_debt_cr NUMERIC,
            total_debt_crore NUMERIC,
            cash_from_operations_cr NUMERIC,
            cash_from_operations_crore NUMERIC,
            revenue_cagr_3yr NUMERIC,
            revenue_cagr_3yr_flag VARCHAR(30),
            revenue_cagr_5yr NUMERIC,
            revenue_cagr_5yr_flag VARCHAR(30),
            revenue_cagr_10yr NUMERIC,
            revenue_cagr_10yr_flag VARCHAR(30),
            pat_cagr_3yr NUMERIC,
            pat_cagr_3yr_flag VARCHAR(30),
            pat_cagr_5yr NUMERIC,
            pat_cagr_5yr_flag VARCHAR(30),
            pat_cagr_10yr NUMERIC,
            pat_cagr_10yr_flag VARCHAR(30),
            eps_cagr_3yr NUMERIC,
            eps_cagr_3yr_flag VARCHAR(30),
            eps_cagr_5yr NUMERIC,
            eps_cagr_5yr_flag VARCHAR(30),
            eps_cagr_10yr NUMERIC,
            eps_cagr_10yr_flag VARCHAR(30),
            cfo_quality_score NUMERIC,
            cfo_quality_label VARCHAR(30),
            composite_quality_score NUMERIC,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
        """
        conn.execute(create_sql)

        # Alter table if existing schema lacks newly added columns
        cursor = conn.execute("PRAGMA table_info(financial_ratios);")
        existing_cols = {row[1] for row in cursor.fetchall()}

        new_columns = [
            ("revenue_cagr_3yr", "NUMERIC"),
            ("revenue_cagr_3yr_flag", "VARCHAR(30)"),
            ("revenue_cagr_10yr", "NUMERIC"),
            ("revenue_cagr_10yr_flag", "VARCHAR(30)"),
            ("pat_cagr_3yr", "NUMERIC"),
            ("pat_cagr_3yr_flag", "VARCHAR(30)"),
            ("pat_cagr_10yr", "NUMERIC"),
            ("pat_cagr_10yr_flag", "VARCHAR(30)"),
            ("eps_cagr_3yr", "NUMERIC"),
            ("eps_cagr_3yr_flag", "VARCHAR(30)"),
            ("eps_cagr_10yr", "NUMERIC"),
            ("eps_cagr_10yr_flag", "VARCHAR(30)"),
            ("cfo_quality_score", "NUMERIC"),
            ("cfo_quality_label", "VARCHAR(30)"),
        ]

        for col_name, col_type in new_columns:
            if col_name not in existing_cols:
                try:
                    conn.execute(f"ALTER TABLE financial_ratios ADD COLUMN {col_name} {col_type};")
                except Exception as ex:
                    logger.debug("Column %s might already exist: %s", col_name, ex)

        conn.commit()

    def run(self) -> dict[str, Any]:
        """Run complete KPI computation pipeline and populate financial_ratios table."""
        start_time = time.time()
        logger.info("Starting Ratio Engine run on %s...", self.db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            self._ensure_schema(conn)

            # Load statement tables into DataFrames
            df_companies = pd.read_sql_query("SELECT * FROM companies", conn)
            df_sectors = pd.read_sql_query("SELECT * FROM sectors", conn)
            df_pl = pd.read_sql_query("SELECT * FROM profitandloss", conn)
            df_bs = pd.read_sql_query("SELECT * FROM balancesheet", conn)
            df_cf = pd.read_sql_query("SELECT * FROM cashflow", conn)

            # Sector lookup for Financials carve-outs
            sector_map = dict(zip(df_sectors["company_id"], df_sectors["broad_sector"]))
            financial_tickers = set()
            for cid, sec in sector_map.items():
                sec_lower = str(sec).lower()
                if any(kw in sec_lower for kw in FINANCIAL_SECTOR_KEYWORDS):
                    financial_tickers.add(cid)

            companies_ref = df_companies.set_index("id")

            # Merge statement data on (company_id, year)
            df_merged = pd.merge(df_pl, df_bs, on=["company_id", "year"], how="outer", suffixes=("_pl", "_bs"))
            df_merged = pd.merge(df_merged, df_cf, on=["company_id", "year"], how="outer", suffixes=("", "_cf"))

            # Clean and sort chronologically
            df_merged["year_clean"] = df_merged["year"].astype(str)
            df_merged = df_merged.sort_values(by=["company_id", "year_clean"]).reset_index(drop=True)

            company_groups = {cid: group.reset_index(drop=True) for cid, group in df_merged.groupby("company_id")}

            ratios_records: list[dict[str, Any]] = []

            for cid, group in company_groups.items():
                is_fin = cid in financial_tickers
                co_meta = companies_ref.loc[cid] if cid in companies_ref.index else None
                face_val = float(co_meta["face_value"]) if co_meta is not None and pd.notnull(co_meta.get("face_value")) else 1.0

                n_rows = len(group)
                for idx in range(n_rows):
                    row = group.iloc[idx]
                    yr = str(row["year"])

                    # Extract core raw inputs
                    sales = float(row["sales"]) if pd.notnull(row.get("sales")) else None
                    op = float(row["operating_profit"]) if pd.notnull(row.get("operating_profit")) else None
                    src_opm = float(row["opm_percentage"]) if pd.notnull(row.get("opm_percentage")) else None
                    other_inc = float(row["other_income"]) if pd.notnull(row.get("other_income")) else 0.0
                    interest = float(row["interest"]) if pd.notnull(row.get("interest")) else 0.0
                    deprec = float(row["depreciation"]) if pd.notnull(row.get("depreciation")) else 0.0
                    pat = float(row["net_profit"]) if pd.notnull(row.get("net_profit")) else None
                    eps = float(row["eps"]) if pd.notnull(row.get("eps")) else None
                    div_payout = float(row["dividend_payout"]) if pd.notnull(row.get("dividend_payout")) else None

                    eq_cap = float(row["equity_capital"]) if pd.notnull(row.get("equity_capital")) else None
                    reserves = float(row["reserves"]) if pd.notnull(row.get("reserves")) else 0.0
                    borrowings = float(row["borrowings"]) if pd.notnull(row.get("borrowings")) else 0.0
                    tot_assets = float(row["total_assets"]) if pd.notnull(row.get("total_assets")) else None
                    investments = float(row["investments"]) if pd.notnull(row.get("investments")) else 0.0

                    cfo = float(row["operating_activity"]) if pd.notnull(row.get("operating_activity")) else None
                    cfi = float(row["investing_activity"]) if pd.notnull(row.get("investing_activity")) else None
                    cff = float(row["financing_activity"]) if pd.notnull(row.get("financing_activity")) else None

                    # EBIT = Operating Profit - Depreciation
                    ebit = (op - deprec) if (op is not None and deprec is not None) else op

                    # 1. Profitability & Returns
                    npm = compute_net_profit_margin(pat, sales)
                    opm, opm_mismatch = compute_operating_profit_margin(op, sales, src_opm, tolerance=OPM_CROSS_CHECK_TOLERANCE)
                    if opm_mismatch:
                        self.log_edge_case(
                            ANOMALY_FORMULA_DISCREPANCY, cid, yr,
                            f"OPM cross-check diff > {OPM_CROSS_CHECK_TOLERANCE}%: computed {opm}% vs source {src_opm}%"
                        )

                    roe = compute_roe(pat, eq_cap, reserves)
                    if roe is None and pat is not None and eq_cap is not None and (eq_cap + reserves) <= 0:
                        self.log_edge_case(
                            ANOMALY_DATA_SOURCE_ISSUE, cid, yr,
                            f"Negative total equity ({eq_cap + reserves:.2f} Cr); ROE set to None"
                        )

                    roce = compute_roce(ebit, eq_cap, reserves, borrowings, is_financial=is_fin)
                    roa = compute_roa(pat, tot_assets)

                    # 2. Leverage & Efficiency
                    de, high_leverage = compute_debt_to_equity(borrowings, eq_cap, reserves, is_financial=is_fin)
                    if is_fin and borrowings > 0:
                        self.log_edge_case(
                            ANOMALY_SECTOR_CARVE_OUT, cid, yr,
                            f"Financial sector constituent: D/E warning suppressed for D/E={de:.2f}"
                        )

                    icr, icr_label, icr_warn = compute_interest_coverage(op, other_inc, interest)
                    if icr_label == "Debt Free":
                        self.log_edge_case(ANOMALY_DEBT_FREE, cid, yr, "Zero interest expense detected; ICR label set to 'Debt Free'")
                    elif icr_warn:
                        self.log_edge_case(
                            ANOMALY_LEVERAGE_WARNING, cid, yr,
                            f"ICR {icr:.2f} < {INTEREST_COVERAGE_RISK_THRESHOLD}; interest coverage at risk"
                        )

                    asset_turnover = compute_asset_turnover(sales, tot_assets)
                    net_debt = compute_net_debt(borrowings, investments)
                    bvps = compute_book_value_per_share(eq_cap, reserves, face_val)

                    # 3. Cash Flow KPIs
                    fcf = compute_free_cash_flow(cfo, cfi)
                    capex = abs(cfi) if cfi is not None else 0.0
                    fcf_conv, _ = compute_fcf_conversion_rate(fcf, op)
                    capex_intensity, _ = compute_capex_intensity(cfi, sales)

                    # Capital Allocation Pattern
                    cfo_pat_ratio = (cfo / pat) if (cfo is not None and pat is not None and pat != 0) else None
                    sgn_cfo, sgn_cfi, sgn_cff, pattern_label = classify_pattern(
                        cfo, cfi, cff, cfo_pat_ratio
                    )
                    self.capital_allocations.append({
                        "company_id": cid,
                        "year": yr,
                        "cfo_sign": sgn_cfo,
                        "cfi_sign": sgn_cfi,
                        "cff_sign": sgn_cff,
                        "pattern_label": pattern_label,
                    })

                    # Rolling 5Y CFO Quality Score
                    cfo_window = []
                    pat_window = []
                    start_w = max(0, idx - 4)
                    for w_i in range(start_w, idx + 1):
                        r_w = group.iloc[w_i]
                        cfo_w = float(r_w["operating_activity"]) if pd.notnull(r_w.get("operating_activity")) else None
                        pat_w = float(r_w["net_profit"]) if pd.notnull(r_w.get("net_profit")) else None
                        if cfo_w is not None and pat_w is not None:
                            cfo_window.append(cfo_w)
                            pat_window.append(pat_w)
                    cfo_score, cfo_label = compute_cfo_quality_score(cfo_window, pat_window)

                    # 4. Multi-period CAGR Computations (3Y, 5Y, 10Y)
                    # 3-Year CAGR
                    rev_cagr_3y, rev_flag_3y = (None, CAGR_FLAG_INSUFFICIENT)
                    pat_cagr_3y, pat_flag_3y = (None, CAGR_FLAG_INSUFFICIENT)
                    eps_cagr_3y, eps_flag_3y = (None, CAGR_FLAG_INSUFFICIENT)
                    if idx >= 3:
                        prev3 = group.iloc[idx - 3]
                        rev_cagr_3y, rev_flag_3y = compute_cagr(prev3.get("sales"), sales, 3)
                        pat_cagr_3y, pat_flag_3y = compute_cagr(prev3.get("net_profit"), pat, 3)
                        eps_cagr_3y, eps_flag_3y = compute_cagr(prev3.get("eps"), eps, 3)
                        if rev_flag_3y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"3Y Revenue CAGR edge case: {rev_flag_3y}")
                        if pat_flag_3y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"3Y PAT CAGR edge case: {pat_flag_3y}")

                    # 5-Year CAGR
                    rev_cagr_5y, rev_flag_5y = (None, CAGR_FLAG_INSUFFICIENT)
                    pat_cagr_5y, pat_flag_5y = (None, CAGR_FLAG_INSUFFICIENT)
                    eps_cagr_5y, eps_flag_5y = (None, CAGR_FLAG_INSUFFICIENT)
                    if idx >= 5:
                        prev5 = group.iloc[idx - 5]
                        rev_cagr_5y, rev_flag_5y = compute_cagr(prev5.get("sales"), sales, 5)
                        pat_cagr_5y, pat_flag_5y = compute_cagr(prev5.get("net_profit"), pat, 5)
                        eps_cagr_5y, eps_flag_5y = compute_cagr(prev5.get("eps"), eps, 5)
                        if rev_flag_5y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"5Y Revenue CAGR edge case: {rev_flag_5y}")
                        if pat_flag_5y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"5Y PAT CAGR edge case: {pat_flag_5y}")

                    # 10-Year CAGR
                    rev_cagr_10y, rev_flag_10y = (None, CAGR_FLAG_INSUFFICIENT)
                    pat_cagr_10y, pat_flag_10y = (None, CAGR_FLAG_INSUFFICIENT)
                    eps_cagr_10y, eps_flag_10y = (None, CAGR_FLAG_INSUFFICIENT)
                    if idx >= 10:
                        prev10 = group.iloc[idx - 10]
                        rev_cagr_10y, rev_flag_10y = compute_cagr(prev10.get("sales"), sales, 10)
                        pat_cagr_10y, pat_flag_10y = compute_cagr(prev10.get("net_profit"), pat, 10)
                        eps_cagr_10y, eps_flag_10y = compute_cagr(prev10.get("eps"), eps, 10)
                        if rev_flag_10y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"10Y Revenue CAGR edge case: {rev_flag_10y}")
                        if pat_flag_10y not in (CAGR_FLAG_NORMAL, CAGR_FLAG_INSUFFICIENT):
                            self.log_edge_case(ANOMALY_CAGR_ANOMALY, cid, yr, f"10Y PAT CAGR edge case: {pat_flag_10y}")

                    # 5. Composite Quality Score (0–100)
                    # 35% Profitability, 30% Cash Quality, 20% Growth, 15% Leverage
                    roe_val = roe if roe is not None else 0.0
                    roe_score = max(0.0, min(100.0, (roe_val / 25.0) * 100.0))

                    fcf_score = 100.0 if (fcf is not None and fcf > 0) else 0.0

                    pat_growth = pat_cagr_5y if (pat_cagr_5y is not None and pat_flag_5y == CAGR_FLAG_NORMAL) else 0.0
                    growth_score = max(0.0, min(100.0, (pat_growth / 25.0) * 100.0))

                    if de is None or de == 0:
                        lev_score = 100.0
                    elif de <= 0.5:
                        lev_score = 85.0
                    elif de <= 1.0:
                        lev_score = 70.0
                    elif de <= 2.0:
                        lev_score = 50.0
                    else:
                        lev_score = 20.0 if is_fin else 0.0

                    composite_score = round(
                        (WEIGHT_PROFITABILITY * roe_score)
                        + (WEIGHT_CASH_QUALITY * fcf_score)
                        + (WEIGHT_GROWTH * growth_score)
                        + (WEIGHT_LEVERAGE * lev_score),
                        1,
                    )

                    ratios_records.append({
                        "company_id": cid,
                        "year": yr,
                        "net_profit_margin_pct": npm,
                        "operating_profit_margin_pct": opm,
                        "return_on_equity_pct": roe,
                        "return_on_capital_employed_pct": roce,
                        "return_on_assets_pct": roa,
                        "debt_to_equity": de,
                        "high_leverage_flag": 1 if high_leverage else 0,
                        "interest_coverage": icr,
                        "icr_label": icr_label,
                        "asset_turnover": asset_turnover,
                        "net_debt_cr": net_debt,
                        "free_cash_flow_cr": fcf,
                        "free_cash_flow_crore": fcf,
                        "capex_cr": capex,
                        "capex_crore": capex,
                        "fcf_conversion_pct": fcf_conv,
                        "capex_intensity_pct": capex_intensity,
                        "earnings_per_share": eps,
                        "book_value_per_share": bvps,
                        "dividend_payout_ratio_pct": div_payout,
                        "total_debt_cr": borrowings,
                        "total_debt_crore": borrowings,
                        "cash_from_operations_cr": cfo,
                        "cash_from_operations_crore": cfo,
                        "revenue_cagr_3yr": rev_cagr_3y,
                        "revenue_cagr_3yr_flag": rev_flag_3y,
                        "revenue_cagr_5yr": rev_cagr_5y,
                        "revenue_cagr_5yr_flag": rev_flag_5y,
                        "revenue_cagr_10yr": rev_cagr_10y,
                        "revenue_cagr_10yr_flag": rev_flag_10y,
                        "pat_cagr_3yr": pat_cagr_3y,
                        "pat_cagr_3yr_flag": pat_flag_3y,
                        "pat_cagr_5yr": pat_cagr_5y,
                        "pat_cagr_5yr_flag": pat_flag_5y,
                        "pat_cagr_10yr": pat_cagr_10y,
                        "pat_cagr_10yr_flag": pat_flag_10y,
                        "eps_cagr_3yr": eps_cagr_3y,
                        "eps_cagr_3yr_flag": eps_flag_3y,
                        "eps_cagr_5yr": eps_cagr_5y,
                        "eps_cagr_5yr_flag": eps_flag_5y,
                        "eps_cagr_10yr": eps_cagr_10y,
                        "eps_cagr_10yr_flag": eps_flag_10y,
                        "cfo_quality_score": cfo_score,
                        "cfo_quality_label": cfo_label,
                        "composite_quality_score": composite_score,
                    })

                # Cross-check latest computed metrics vs company metadata
                if co_meta is not None and ratios_records:
                    src_roce = float(co_meta["roce_percentage"]) if pd.notnull(co_meta.get("roce_percentage")) else None
                    src_roe = float(co_meta["roe_percentage"]) if pd.notnull(co_meta.get("roe_percentage")) else None

                    latest_row = ratios_records[-1]
                    calc_roce = latest_row["return_on_capital_employed_pct"]
                    calc_roe = latest_row["return_on_equity_pct"]

                    if src_roce is not None and calc_roce is not None:
                        if abs(src_roce - calc_roce) > ROCE_CROSS_CHECK_TOLERANCE:
                            self.log_edge_case(
                                ANOMALY_VERSION_DIFFERENCE, cid, latest_row["year"],
                                f"ROCE discrepancy > {ROCE_CROSS_CHECK_TOLERANCE}%: computed {calc_roce:.2f}% vs companies snapshot {src_roce:.2f}%"
                            )

                    if src_roe is not None and calc_roe is not None:
                        if src_roe < 1.0 and calc_roe > 10.0:
                            self.log_edge_case(
                                ANOMALY_DATA_SOURCE_ISSUE, cid, latest_row["year"],
                                f"Pre-computed ROE anomaly: source shows {src_roe} (fractional artifact); computed ROE is {calc_roe:.2f}%"
                            )

            # Insert into SQLite financial_ratios table
            df_ratios = pd.DataFrame(ratios_records)
            logger.info("Computed %d ratio records. Populating financial_ratios...", len(df_ratios))

            conn.execute("DELETE FROM financial_ratios;")
            df_ratios.to_sql("financial_ratios", conn, if_exists="append", index=False)
            conn.commit()

            cur = conn.execute("SELECT COUNT(*) FROM financial_ratios;")
            final_count = cur.fetchone()[0]
            logger.info("Successfully populated financial_ratios table with %d records", final_count)

            # Mirror to root nifty100.db if configured
            if self.mirror_db_path and self.mirror_db_path != self.db_path:
                try:
                    conn_m = sqlite3.connect(self.mirror_db_path)
                    try:
                        self._ensure_schema(conn_m)
                        conn_m.execute("DELETE FROM financial_ratios;")
                        df_ratios.to_sql("financial_ratios", conn_m, if_exists="append", index=False)
                        conn_m.commit()
                        logger.info("Successfully mirrored financial_ratios to %s", self.mirror_db_path)
                    finally:
                        conn_m.close()
                except Exception as ex:
                    logger.warning("Could not mirror to %s: %s", self.mirror_db_path, ex)

        finally:
            conn.close()

        # Export capital_allocation.csv
        export_capital_allocation_csv(self.capital_allocations, CAPITAL_ALLOCATION_CSV)

        # Export ratio_edge_cases.log
        with open(RATIO_EDGE_CASES_LOG, "w", encoding="utf-8") as f:
            f.write("# NIFTY 100 RATIO ENGINE — EDGE CASE & ANOMALY AUDIT LOG\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total Anomaly Entries: {len(self.edge_case_logs)}\n\n")
            for line in self.edge_case_logs:
                f.write(line + "\n")
        logger.info("Saved %d ratio edge cases to %s", len(self.edge_case_logs), RATIO_EDGE_CASES_LOG)

        dur = round(time.time() - start_time, 2)
        return {
            "status": "SUCCESS",
            "runtime_s": dur,
            "total_ratio_records": final_count,
            "capital_allocation_records": len(self.capital_allocations),
            "edge_case_count": len(self.edge_case_logs),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engine = RatioEngine()
    engine.run()
