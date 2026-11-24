"""Peer Comparison Engine: percentile rankings, benchmark analysis, and Excel reporting."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional, Tuple
import numpy as np
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd

logger = logging.getLogger(__name__)

# Standard 11 peer group definitions & benchmarks
DEFAULT_PEER_GROUPS: dict[str, dict[str, Any]] = {
    "Private Banks": {
        "benchmark": "HDFCBANK",
        "members": ["HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "INDUSINDBK"],
    },
    "Public Banks": {
        "benchmark": "SBIN",
        "members": ["SBIN", "BANKBARODA", "CANBK", "PNB"],
    },
    "IT Services": {
        "benchmark": "TCS",
        "members": ["TCS", "INFY", "HCLTECH", "TECHM", "LTIM"],
    },
    "Pharmaceuticals": {
        "benchmark": "SUNPHARMA",
        "members": ["SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB", "TORNTPHARM"],
    },
    "Automobiles": {
        "benchmark": "MARUTI",
        "members": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR"],
    },
    "Life Insurance": {
        "benchmark": "LICI",
        "members": ["LICI", "HDFCLIFE", "SBILIFE", "ICICIPRULI"],
    },
    "Oil & Gas": {
        "benchmark": "RELIANCE",
        "members": ["RELIANCE", "ONGC", "BPCL", "IOC", "GAIL"],
    },
    "Power & Utilities": {
        "benchmark": "NTPC",
        "members": ["NTPC", "POWERGRID", "TATAPOWER", "ADANIPOWER", "NHPC", "JSWENERGY", "ADANIGREEN"],
    },
    "Steel & Metals": {
        "benchmark": "TATASTEEL",
        "members": ["TATASTEEL", "JSWSTEEL", "JINDALSTEL", "HINDALCO"],
    },
    "FMCG": {
        "benchmark": "HINDUNILVR",
        "members": ["HINDUNILVR", "ITC", "BRITANNIA", "DABUR", "NESTLEIND", "GODREJCP", "TATACONSUM"],
    },
    "Consumer Finance": {
        "benchmark": "BAJFINANCE",
        "members": ["BAJFINANCE", "CHOLAFIN", "SHRIRAMFIN"],
    },
}

# Exactly 10 ranking metrics required by specification
RANKING_METRICS: list[dict[str, Any]] = [
    {"id": "return_on_equity_pct", "name": "ROE (%)", "invert": False},
    {"id": "return_on_capital_employed_pct", "name": "ROCE (%)", "invert": False},
    {"id": "net_profit_margin_pct", "name": "NPM (%)", "invert": False},
    {"id": "debt_to_equity", "name": "D/E Ratio", "invert": True},  # Lower D/E is better!
    {"id": "free_cash_flow_cr", "name": "FCF (₹ Cr)", "invert": False},
    {"id": "pat_cagr_5yr", "name": "5Y PAT CAGR (%)", "invert": False},
    {"id": "revenue_cagr_5yr", "name": "5Y Rev CAGR (%)", "invert": False},
    {"id": "eps_cagr_5yr", "name": "5Y EPS CAGR (%)", "invert": False},
    {"id": "interest_coverage", "name": "Interest Coverage", "invert": False},
    {"id": "asset_turnover", "name": "Asset Turnover", "invert": False},
]


def load_peer_groups(db_path: Optional[str | Path] = None, excel_path: Optional[str | Path] = None) -> dict[str, dict[str, Any]]:
    """Load peer groups and benchmark definitions from Excel, database, or canonical fallback."""
    # 1. Try Excel file if available
    excel_candidates = [
        excel_path,
        Path("data/supporting/peer_groups.xlsx"),
        Path("peer_groups.xlsx"),
    ]
    for c in excel_candidates:
        if c and Path(c).exists():
            try:
                df = pd.read_excel(c)
                if not df.empty and "peer_group_name" in df.columns:
                    groups: dict[str, dict[str, Any]] = {}
                    for gname, grp in df.groupby("peer_group_name"):
                        benchmarks = grp[grp["is_benchmark"] == 1]["company_id"].tolist()
                        bench = benchmarks[0] if benchmarks else grp["company_id"].iloc[0]
                        groups[str(gname)] = {
                            "benchmark": str(bench),
                            "members": [str(m) for m in grp["company_id"].tolist()],
                        }
                    if len(groups) >= 11:
                        return groups
            except Exception as ex:
                logger.debug("Failed reading peer_groups excel from %s: %s", c, ex)

    # 2. Try database
    if db_path:
        p = Path(db_path)
        if p.exists():
            try:
                conn = sqlite3.connect(p)
                df = pd.read_sql_query("SELECT * FROM peer_groups", conn)
                conn.close()
                if not df.empty:
                    groups = {}
                    for gname, grp in df.groupby("peer_group_name"):
                        benchmarks = grp[grp["is_benchmark"] == 1]["company_id"].tolist()
                        bench = benchmarks[0] if benchmarks else grp["company_id"].iloc[0]
                        groups[str(gname)] = {
                            "benchmark": str(bench),
                            "members": [str(m) for m in grp["company_id"].tolist()],
                        }
                    if len(groups) >= 11:
                        return groups
            except Exception as ex:
                logger.debug("Using DEFAULT_PEER_GROUPS fallback: %s", ex)

    # 3. Canonical fallback
    return DEFAULT_PEER_GROUPS


def calculate_percentile(series: pd.Series, invert: bool = False) -> pd.Series:
    """Calculate PERCENT_RANK for a metric series. Invert if lower is better."""
    s = pd.to_numeric(series, errors="coerce")
    valid_cnt = s.dropna().count()
    if valid_cnt > 1:
        ranks = s.rank(pct=True, method="average")
        if invert:
            ranks = 1.0 - ranks
    elif valid_cnt == 1:
        ranks = pd.Series(1.0 if not invert else 0.0, index=s.index)
    else:
        ranks = pd.Series(np.nan, index=s.index)
    return ranks.round(3)


class PeerComparisonEngine:
    """Computes intra-group percentile rankings, radar data, and peer comparison reports."""

    def __init__(
        self,
        db_path: str | Path = "data/nifty100.db",
        output_dir: str | Path = "output",
    ):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            alt = Path("nifty100.db")
            if alt.exists():
                self.db_path = alt
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.peer_groups = load_peer_groups(self.db_path)

    def get_peer_group_for_ticker(self, ticker: str) -> Optional[str]:
        """Return the peer group name for a company, or None if unassigned."""
        t = str(ticker).strip().upper()
        for group_name, info in self.peer_groups.items():
            if t in [m.upper() for m in info["members"]]:
                return group_name
        return None

    def calculate_peer_percentiles(self, year: Optional[str] = None) -> pd.DataFrame:
        """Alias for compute_peer_percentiles to satisfy reusability requirements."""
        return self.compute_peer_percentiles(year)

    def compute_peer_percentiles(self, year: Optional[str] = None) -> pd.DataFrame:
        """
        Compute percentiles across all 11 peer groups and 10 metrics.
        Populates SQLite peer_percentiles table idempotently.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            if year is None:
                cur = conn.execute(
                    "SELECT year FROM financial_ratios "
                    "WHERE return_on_equity_pct IS NOT NULL "
                    "GROUP BY year ORDER BY count(*) DESC, year DESC LIMIT 1;"
                )
                res = cur.fetchone()
                year = res[0] if res and res[0] else "2024-03"

            df_ratios = pd.read_sql_query(f"SELECT * FROM financial_ratios WHERE year = '{year}'", conn)
            percentile_rows: list[dict[str, Any]] = []

            for group_name, info in self.peer_groups.items():
                members = info["members"]
                sub_ratios = df_ratios[df_ratios["company_id"].isin(members)].copy()

                if sub_ratios.empty:
                    continue

                for metric_info in RANKING_METRICS:
                    m_col = metric_info["id"]
                    invert = metric_info["invert"]

                    # Extract numeric series
                    s = pd.to_numeric(sub_ratios[m_col], errors="coerce").copy()

                    # ICR: Treat Debt Free as highest value (passes as infinity)
                    if m_col == "interest_coverage":
                        debt_free_mask = sub_ratios["icr_label"] == "Debt Free"
                        s.loc[debt_free_mask] = 999999.0

                    ranks = calculate_percentile(s, invert=invert)

                    for idx, row in sub_ratios.iterrows():
                        cid = row["company_id"]
                        val = row.get(m_col)
                        pct_rank = float(ranks.loc[idx]) if pd.notnull(ranks.loc[idx]) else None

                        percentile_rows.append({
                            "company_id": cid,
                            "peer_group_name": group_name,
                            "metric": m_col,
                            "value": round(float(val), 2) if pd.notnull(val) else None,
                            "percentile_rank": pct_rank,
                            "year": year,
                        })

            df_pct = pd.DataFrame(percentile_rows)

            # Insert into SQLite peer_percentiles table
            self.save_peer_percentiles(df_pct, year, conn)
            return df_pct
        finally:
            conn.close()

    def save_peer_percentiles(self, df_pct: pd.DataFrame, year: str, conn: Optional[sqlite3.Connection] = None) -> None:
        """Idempotently save percentile calculations to peer_percentiles table."""
        should_close = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS peer_percentiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id VARCHAR(16) NOT NULL,
                peer_group_name VARCHAR(100) NOT NULL,
                metric VARCHAR(50) NOT NULL,
                value NUMERIC,
                percentile_rank NUMERIC,
                year VARCHAR(7) NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
            """)
            conn.execute("DELETE FROM peer_percentiles WHERE year = ?;", (year,))
            df_pct.to_sql("peer_percentiles", conn, if_exists="append", index=False)
            conn.commit()
            logger.info("Saved %d peer percentile records to peer_percentiles for year %s", len(df_pct), year)
        finally:
            if should_close:
                conn.close()

    def get_company_peer_analysis(self, ticker: str, year: Optional[str] = None) -> dict[str, Any]:
        """Return detailed peer ranking, best-in-class badge, and watchlist status for a company."""
        group_name = self.get_peer_group_for_ticker(ticker)
        if not group_name:
            return {"status": "NO_PEER_GROUP", "message": "No peer group assigned"}

        conn = sqlite3.connect(self.db_path)
        try:
            if year is None:
                cur = conn.execute("SELECT MAX(year) FROM peer_percentiles WHERE company_id = ?;", (ticker,))
                res = cur.fetchone()
                year = res[0] if res and res[0] else "2024-03"

            df = pd.read_sql_query(
                "SELECT metric, value, percentile_rank FROM peer_percentiles WHERE company_id = ? AND year = ?;",
                conn,
                params=(ticker, year),
            )
            if df.empty:
                self.compute_peer_percentiles(year)
                df = pd.read_sql_query(
                    "SELECT metric, value, percentile_rank FROM peer_percentiles WHERE company_id = ? AND year = ?;",
                    conn,
                    params=(ticker, year),
                )

            pct_dict = dict(zip(df["metric"], df["percentile_rank"]))
            high_count = sum(1 for p in pct_dict.values() if p is not None and p >= 0.75)
            low_count = sum(1 for p in pct_dict.values() if p is not None and p <= 0.25)

            is_best_in_class = high_count >= 6
            is_watchlist = low_count >= 4

            return {
                "company_id": ticker,
                "peer_group": group_name,
                "benchmark_company": self.peer_groups[group_name]["benchmark"],
                "year": year,
                "metrics": pct_dict,
                "best_in_class": is_best_in_class,
                "watchlist": is_watchlist,
                "high_quartile_metrics_count": high_count,
                "low_quartile_metrics_count": low_count,
            }
        finally:
            conn.close()

    def generate_peer_report(self, file_path: Optional[str | Path] = None) -> str:
        """Alias for export_peer_comparison_excel to satisfy reusability requirements."""
        return self.export_peer_comparison_excel(file_path)

    def export_peer_comparison_excel(self, file_path: Optional[str | Path] = None) -> str:
        """
        Generate output/peer_comparison.xlsx with exactly 11 sheets (one per peer group).
        Colour-coded percentiles (>=75th green, 25th-75th yellow, <=25th red),
        benchmark company highlighted in gold/amber, and bottom median summary row.
        """
        out_path = Path(file_path) if file_path else self.output_dir / "peer_comparison.xlsx"
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default blank sheet

        conn = sqlite3.connect(self.db_path)
        try:
            # Query latest representative full annual year
            cur = conn.execute(
                "SELECT year FROM financial_ratios "
                "WHERE return_on_equity_pct IS NOT NULL "
                "GROUP BY year ORDER BY count(*) DESC, year DESC LIMIT 1;"
            )
            res = cur.fetchone()
            year = res[0] if res and res[0] else "2024-03"

            df_ratios = pd.read_sql_query(f"SELECT * FROM financial_ratios WHERE year = '{year}'", conn)
            df_companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
            co_name_map = dict(zip(df_companies["id"], df_companies["company_name"]))
            ratios_map = df_ratios.set_index("company_id")

            # Styles
            header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            benchmark_fill = PatternFill(start_color="FFEBAA", end_color="FFEBAA", fill_type="solid")  # Gold/Amber
            green_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")      # >= 75th
            yellow_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")     # 25th - <75th
            red_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")        # <= 25th
            summary_fill = PatternFill(start_color="E2E3E5", end_color="E2E3E5", fill_type="solid")    # Median Gray
            bold_font = Font(name="Calibri", size=10, bold=True)
            regular_font = Font(name="Calibri", size=10)
            thin_border = Border(
                left=Side(style="thin", color="D3D3D3"),
                right=Side(style="thin", color="D3D3D3"),
                top=Side(style="thin", color="D3D3D3"),
                bottom=Side(style="thin", color="D3D3D3"),
            )

            # Pre-compute percentiles to ensure SQLite table is populated
            self.compute_peer_percentiles(year)
            df_all_pct = pd.read_sql_query(f"SELECT * FROM peer_percentiles WHERE year = '{year}'", conn)

            for group_name, info in self.peer_groups.items():
                ws = wb.create_sheet(title=group_name[:31])  # Excel 31 char sheet title limit
                ws.views.sheetView[0].showGridLines = True
                members = info["members"]
                benchmark = info["benchmark"]

                # Header construction: Company ID, Name, Role, followed by 10 metrics with values and percentiles
                headers = ["Company ID", "Company Name", "Role"]
                for m in RANKING_METRICS:
                    headers.append(m["name"])
                    headers.append(f"{m['name']} Percentile")

                ws.append(headers)
                for col_idx in range(1, len(headers) + 1):
                    cell = ws.cell(row=1, column=col_idx)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                # Member data rows
                metric_values_by_col: dict[str, list[float]] = {m["id"]: [] for m in RANKING_METRICS}

                for ticker in members:
                    is_bench = (ticker == benchmark)
                    co_name = co_name_map.get(ticker, f"{ticker} Limited")
                    role = "Benchmark" if is_bench else "Member"

                    row_vals = [ticker, co_name, role]
                    row_pcts = []

                    row_ratios = ratios_map.loc[ticker] if ticker in ratios_map.index else None

                    for m in RANKING_METRICS:
                        m_id = m["id"]
                        val = row_ratios.get(m_id) if row_ratios is not None else None
                        val_num = float(val) if pd.notnull(val) else None
                        if val_num is not None:
                            metric_values_by_col[m_id].append(val_num)

                        # Lookup percentile rank
                        p_match = df_all_pct[
                            (df_all_pct["company_id"] == ticker) &
                            (df_all_pct["peer_group_name"] == group_name) &
                            (df_all_pct["metric"] == m_id)
                        ]
                        pct = p_match.iloc[0]["percentile_rank"] if not p_match.empty else None

                        row_vals.append(round(val_num, 2) if val_num is not None else "—")
                        row_vals.append(f"{round(pct * 100, 1)}%" if pct is not None else "—")
                        row_pcts.append(pct)

                    ws.append(row_vals)
                    cur_row = ws.max_row

                    # Apply row styles
                    for c_idx in range(1, len(headers) + 1):
                        cell = ws.cell(row=cur_row, column=c_idx)
                        cell.font = bold_font if is_bench else regular_font
                        cell.border = thin_border
                        if is_bench:
                            cell.fill = benchmark_fill

                    # Apply percentile color coding (every even column starting at 5)
                    for m_idx, pct in enumerate(row_pcts):
                        pct_col_idx = 4 + (m_idx * 2) + 1
                        cell = ws.cell(row=cur_row, column=pct_col_idx)
                        if pct is not None:
                            if pct >= 0.75:
                                cell.fill = green_fill
                            elif pct >= 0.25:
                                cell.fill = yellow_fill
                            else:
                                cell.fill = red_fill

                # Bottom Summary Row: Peer Group Median
                median_vals = ["MEDIAN", f"{group_name} Median", "Summary"]
                for m in RANKING_METRICS:
                    m_id = m["id"]
                    arr = metric_values_by_col[m_id]
                    med = float(np.median(arr)) if arr else None
                    median_vals.append(round(med, 2) if med is not None else "—")
                    median_vals.append("50.0%")

                ws.append(median_vals)
                sum_row = ws.max_row
                for c_idx in range(1, len(headers) + 1):
                    cell = ws.cell(row=sum_row, column=c_idx)
                    cell.fill = summary_fill
                    cell.font = bold_font
                    cell.border = thin_border

                # Adjust column widths
                for col in ws.columns:
                    max_len = max(len(str(c.value or "")) for c in col)
                    col_letter = get_column_letter(col[0].column)
                    ws.column_dimensions[col_letter].width = max(max_len + 2, 11)

            wb.save(out_path)
            logger.info("Saved 11-sheet peer comparison workbook to %s", out_path)
            return str(out_path)
        finally:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engine = PeerComparisonEngine()
    engine.compute_peer_percentiles()
    out = engine.export_peer_comparison_excel()
    print("Peer comparison export complete:", out)
