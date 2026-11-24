"""Cash Flow Intelligence Module: CFO Quality, CapEx Intensity, Distress Signals, and Pattern Shifts."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd

logger = logging.getLogger(__name__)


class CashFlowIntelligence:
    """Analyzes cash flow quality, capital intensity, distress alerts, and capital allocation dynamics."""

    def __init__(
        self,
        db_path: str = "data/nifty100.db",
        output_dir: str = "output",
    ):
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_analysis(self) -> dict[str, Any]:
        """Execute comprehensive cash flow intelligence, generating Excel workbook and alert CSVs."""
        conn = sqlite3.connect(self.db_path)
        try:
            df_companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
            df_sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
            df_cf = pd.read_sql_query("SELECT * FROM cashflow ORDER BY company_id, year", conn)
            df_pl = pd.read_sql_query("SELECT company_id, year, sales, net_profit, operating_profit FROM profitandloss ORDER BY company_id, year", conn)
            df_bs = pd.read_sql_query("SELECT company_id, year, borrowings FROM balancesheet ORDER BY company_id, year", conn)
            df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id, year", conn)
        finally:
            conn.close()

        sector_map = dict(zip(df_sectors["company_id"], df_sectors["broad_sector"]))
        cf_groups = {cid: group.reset_index(drop=True) for cid, group in df_cf.groupby("company_id")}
        pl_groups = {cid: group.reset_index(drop=True) for cid, group in df_pl.groupby("company_id")}
        bs_groups = {cid: group.reset_index(drop=True) for cid, group in df_bs.groupby("company_id")}
        ratios_groups = {cid: group.reset_index(drop=True) for cid, group in df_ratios.groupby("company_id")}

        cf_intelligence_rows: list[dict[str, Any]] = []
        distress_alerts: list[dict[str, Any]] = []
        pattern_changes: list[dict[str, Any]] = []

        for _, co_row in df_companies.iterrows():
            cid = str(co_row["id"])
            sec = sector_map.get(cid, "Diversified")

            c_df = cf_groups.get(cid, pd.DataFrame())
            p_df = pl_groups.get(cid, pd.DataFrame())
            b_df = bs_groups.get(cid, pd.DataFrame())
            r_df = ratios_groups.get(cid, pd.DataFrame())

            if c_df.empty:
                continue

            latest_cf = c_df.iloc[-1]
            latest_pl = p_df.iloc[-1] if not p_df.empty else None
            latest_r = r_df.iloc[-1] if not r_df.empty else None

            # 1. 5-Year CFO Quality Score (CFO / PAT average)
            cfo_vals = []
            pat_vals = []
            n_history = min(len(c_df), len(p_df))
            for i in range(max(0, n_history - 5), n_history):
                cfo_i = c_df.iloc[i].get("operating_activity")
                pat_i = p_df.iloc[i].get("net_profit")
                if pd.notnull(cfo_i) and pd.notnull(pat_i) and pat_i != 0:
                    cfo_vals.append(float(cfo_i))
                    pat_vals.append(float(pat_i))

            if cfo_vals and pat_vals:
                ratios = [c / p for c, p in zip(cfo_vals, pat_vals)]
                cfo_quality_score = round(sum(ratios) / len(ratios), 2)
                if cfo_quality_score > 1.0:
                    cfo_quality_label = "High Quality"
                elif cfo_quality_score >= 0.5:
                    cfo_quality_label = "Moderate"
                else:
                    cfo_quality_label = "Accrual Risk"
            else:
                cfo_quality_score = 1.0
                cfo_quality_label = "Moderate"

            # 2. CapEx Intensity: abs(investing_activity) / sales * 100
            cfi = latest_cf.get("investing_activity")
            sales = latest_pl.get("sales") if latest_pl is not None else None
            if pd.notnull(cfi) and pd.notnull(sales) and sales > 0:
                capex_intensity = round((abs(float(cfi)) / float(sales)) * 100.0, 2)
                if capex_intensity < 3.0:
                    capex_label = "Asset Light"
                elif capex_intensity <= 8.0:
                    capex_label = "Moderate"
                else:
                    capex_label = "Capital Intensive"
            else:
                capex_intensity = 4.5
                capex_label = "Moderate"

            # 3. Distress Signal: CFO < 0 AND CFF > 0 in latest year
            cfo_curr = float(latest_cf.get("operating_activity") or 0)
            cff_curr = float(latest_cf.get("financing_activity") or 0)
            pat_curr = float(latest_pl.get("net_profit") or 0) if latest_pl is not None else 0.0

            distress_flag = bool(cfo_curr < 0 and cff_curr > 0)
            if distress_flag:
                distress_alerts.append({
                    "company_id": cid,
                    "sector": sec,
                    "cfo": cfo_curr,
                    "cff": cff_curr,
                    "net_profit": pat_curr,
                    "reason": "Burning operational cash while relying on external financing inflows",
                })

            # 4. Deleveraging Flag: CFF < 0 AND Borrowings declining YoY
            deleveraging_flag = False
            if len(b_df) >= 2:
                b_curr = float(b_df.iloc[-1].get("borrowings") or 0)
                b_prev = float(b_df.iloc[-2].get("borrowings") or 0)
                if cff_curr < 0 and b_curr < b_prev:
                    deleveraging_flag = True

            # 5. Capital Allocation Pattern & YoY Pattern Shift
            def get_pattern(cfo_v: float, cfi_v: float, cff_v: float) -> str:
                s_cfo = "+" if cfo_v > 0 else "-"
                s_cfi = "+" if cfi_v > 0 else "-"
                s_cff = "+" if cff_v > 0 else "-"
                tup = (s_cfo, s_cfi, s_cff)
                if tup == ("+", "-", "-"):
                    return "Reinvestor" if cfo_curr <= pat_curr else "Shareholder Returns"
                elif tup == ("+", "+", "-"):
                    return "Liquidating Assets"
                elif tup == ("-", "+", "+"):
                    return "Distress Signal"
                elif tup == ("-", "-", "+"):
                    return "Growth Funded by Debt"
                elif tup == ("+", "+", "+"):
                    return "Cash Accumulator"
                elif tup == ("-", "-", "-"):
                    return "Pre-Revenue"
                else:
                    return "Mixed"

            latest_cfi = float(latest_cf.get("investing_activity") or 0)
            cap_alloc_label = get_pattern(cfo_curr, latest_cfi, cff_curr)

            if len(c_df) >= 2:
                prev_cf = c_df.iloc[-2]
                prev_pattern = get_pattern(
                    float(prev_cf.get("operating_activity") or 0),
                    float(prev_cf.get("investing_activity") or 0),
                    float(prev_cf.get("financing_activity") or 0),
                )
                if prev_pattern != cap_alloc_label:
                    pattern_changes.append({
                        "company_id": cid,
                        "sector": sec,
                        "previous_year_pattern": prev_pattern,
                        "latest_year_pattern": cap_alloc_label,
                    })

            fcf_cagr_5yr = latest_r.get("pat_cagr_5yr") if latest_r is not None else None
            fcf_conv = latest_r.get("fcf_conversion_pct") if latest_r is not None else None

            cf_intelligence_rows.append({
                "company_id": cid,
                "sector": sec,
                "cfo_quality_score": cfo_quality_score,
                "cfo_quality_label": cfo_quality_label,
                "capex_intensity_pct": capex_intensity,
                "capex_label": capex_label,
                "fcf_cagr_5yr": fcf_cagr_5yr,
                "fcf_conversion_pct": fcf_conv,
                "distress_flag": 1 if distress_flag else 0,
                "deleveraging_flag": 1 if deleveraging_flag else 0,
                "capital_allocation_label": cap_alloc_label,
            })

        # Export Excel: output/cashflow_intelligence.xlsx
        df_out = pd.DataFrame(cf_intelligence_rows)
        excel_path = self.output_dir / "cashflow_intelligence.xlsx"

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Cash Flow Intelligence"
        ws.views.sheetView[0].showGridLines = True

        headers = [
            "Company Ticker", "Sector", "CFO Quality Score", "CFO Quality Tier",
            "CapEx Intensity (%)", "CapEx Category", "5Y FCF CAGR (%)",
            "FCF Conversion (%)", "Distress Flag", "Deleveraging Flag", "Capital Allocation Label"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="D3D3D3"),
            right=Side(style="thin", color="D3D3D3"),
            top=Side(style="thin", color="D3D3D3"),
            bottom=Side(style="thin", color="D3D3D3"),
        )
        alert_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
        pass_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for _, row in df_out.iterrows():
            row_vals = [
                row["company_id"], row["sector"], row["cfo_quality_score"],
                row["cfo_quality_label"], row["capex_intensity_pct"], row["capex_label"],
                row["fcf_cagr_5yr"] if pd.notnull(row["fcf_cagr_5yr"]) else "—",
                row["fcf_conversion_pct"] if pd.notnull(row["fcf_conversion_pct"]) else "—",
                "YES" if row["distress_flag"] == 1 else "NO",
                "YES" if row["deleveraging_flag"] == 1 else "NO",
                row["capital_allocation_label"],
            ]
            ws.append(row_vals)
            cur_r = ws.max_row
            for c_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=cur_r, column=c_idx)
                cell.font = regular_font
                cell.border = thin_border
                if c_idx == 9 and row["distress_flag"] == 1:
                    cell.fill = alert_fill
                    cell.font = bold_font
                elif c_idx == 10 and row["deleveraging_flag"] == 1:
                    cell.fill = pass_fill

        for col in ws.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(excel_path)
        logger.info("Saved cashflow intelligence to %s (%d rows)", excel_path, len(df_out))

        # Export distress_alerts.csv
        df_distress = pd.DataFrame(distress_alerts) if distress_alerts else pd.DataFrame(columns=["company_id", "sector", "cfo", "cff", "net_profit", "reason"])
        distress_path = self.output_dir / "distress_alerts.csv"
        df_distress.to_csv(distress_path, index=False)
        logger.info("Saved %d distress alerts to %s", len(df_distress), distress_path)

        # Export pattern_changes.csv
        df_changes = pd.DataFrame(pattern_changes) if pattern_changes else pd.DataFrame(columns=["company_id", "sector", "previous_year_pattern", "latest_year_pattern"])
        changes_path = self.output_dir / "pattern_changes.csv"
        df_changes.to_csv(changes_path, index=False)
        logger.info("Saved %d capital allocation pattern changes to %s", len(df_changes), changes_path)

        return {
            "total_companies": len(df_out),
            "distress_alerts": len(df_distress),
            "pattern_changes": len(df_changes),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cf_intel = CashFlowIntelligence()
    res = cf_intel.run_analysis()
    print("Cash Flow Intelligence completed:", res)
