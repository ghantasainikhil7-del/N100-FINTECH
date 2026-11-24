"""Valuation Analytics Module: FCF Yield, Sector-Relative Multiples, and Overvaluation/Discount Flags."""
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


class ValuationEngine:
    """Computes valuation multiples, FCF yields, sector-relative P/E premiums, and risk flags."""

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

    def run_valuation_analysis(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Execute full valuation pipeline across all 92 companies."""
        conn = sqlite3.connect(self.db_path)
        try:
            df_companies = pd.read_sql_query("SELECT id, company_name FROM companies ORDER BY id ASC", conn)
            df_sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
            df_mkt = pd.read_sql_query("SELECT * FROM market_cap ORDER BY company_id, year ASC", conn)
            df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id, year ASC", conn)
        finally:
            conn.close()

        sector_map = dict(zip(df_sectors["company_id"], df_sectors["broad_sector"]))
        mkt_groups = {cid: g.reset_index(drop=True) for cid, g in df_mkt.groupby("company_id")} if not df_mkt.empty else {}
        ratios_groups = {cid: g.reset_index(drop=True) for cid, g in df_ratios.groupby("company_id")} if not df_ratios.empty else {}

        summary_rows: list[dict[str, Any]] = []

        for _, co_row in df_companies.iterrows():
            cid = str(co_row["id"])
            cname = str(co_row["company_name"])
            sec = sector_map.get(cid, "Diversified")

            m_df = mkt_groups.get(cid, pd.DataFrame())
            r_df = ratios_groups.get(cid, pd.DataFrame())

            latest_m = m_df.iloc[-1] if not m_df.empty else {}
            latest_r = r_df.iloc[-1] if not r_df.empty else {}

            # P/E ratio
            pe = latest_m.get("pe_ratio")
            if pe is None or pd.isna(pe):
                pe = latest_m.get("price_to_earnings")

            # P/B ratio
            pb = latest_m.get("pb_ratio")
            if pb is None or pd.isna(pb):
                pb = latest_m.get("price_to_book")

            # EV/EBITDA
            ev_ebitda = latest_m.get("ev_ebitda")
            if ev_ebitda is None or pd.isna(ev_ebitda):
                ev_ebitda = latest_m.get("ev_to_ebitda")

            # Market Cap Crore
            mcap = latest_m.get("market_cap_crore")

            # Free Cash Flow Crore
            fcf = latest_r.get("free_cash_flow_cr")
            if fcf is None or pd.isna(fcf):
                fcf = latest_r.get("free_cash_flow_crore")

            # Compute FCF yield: (FCF / market_cap) * 100
            # Negative FCF Yield is legitimately preserved; do not clamp to zero
            fcf_yield: Optional[float] = None
            if mcap is not None and pd.notnull(mcap) and float(mcap) > 0 and fcf is not None and pd.notnull(fcf):
                fcf_yield = round((float(fcf) / float(mcap)) * 100.0, 2)

            # 5-year median PE from historical records
            pe_5yr_median: Optional[float] = None
            if not m_df.empty:
                pe_col = "pe_ratio" if "pe_ratio" in m_df.columns else "price_to_earnings"
                if pe_col in m_df.columns:
                    recent_pes = m_df[pe_col].dropna().tail(5)
                    if not recent_pes.empty:
                        pe_5yr_median = round(float(recent_pes.median()), 1)

            pe_val = round(float(pe), 1) if pe is not None and pd.notnull(pe) else None
            pb_val = round(float(pb), 2) if pb is not None and pd.notnull(pb) else None
            ev_val = round(float(ev_ebitda), 1) if ev_ebitda is not None and pd.notnull(ev_ebitda) else None

            summary_rows.append({
                "company_id": cid,
                "company_name": cname,
                "sector": sec,
                "P/E": pe_val,
                "P/B": pb_val,
                "EV/EBITDA": ev_val,
                "FCF_yield_pct": fcf_yield,
                "5yr_median_PE": pe_5yr_median,
            })

        df_summary = pd.DataFrame(summary_rows)

        # Calculate sector median P/E across valid latest P/E values
        sector_pe_medians = df_summary.groupby("sector")["P/E"].median().to_dict()

        # Compute PE vs sector median & assign flags
        flags: list[str] = []
        pe_vs_medians: list[Optional[float]] = []

        for _, row in df_summary.iterrows():
            sec_med = sector_pe_medians.get(row["sector"])
            pe_val = row["P/E"]

            if pe_val is not None and sec_med is not None and sec_med > 0:
                # Formula: ((P/E / sector_median_PE) - 1.0) * 100.0
                pct_vs_med = round(((pe_val / sec_med) - 1.0) * 100.0, 1)
                pe_vs_medians.append(pct_vs_med)

                # Flag rules:
                # Caution: P/E > sector_median_P/E * 1.5
                # Discount: P/E < sector_median_P/E * 0.7
                # Fair: otherwise
                if pe_val > (sec_med * 1.5):
                    flags.append("Caution")
                elif pe_val < (sec_med * 0.7):
                    flags.append("Discount")
                else:
                    flags.append("Fair")
            else:
                pe_vs_medians.append(None)
                flags.append("Fair")

        df_summary["PE_vs_sector_median_pct"] = pe_vs_medians
        df_summary["flag"] = flags

        # Export Excel: output/valuation_summary.xlsx with exact 10 required columns
        excel_path = self.output_dir / "valuation_summary.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Valuation Summary"
        ws.views.sheetView[0].showGridLines = True

        headers = [
            "company_id", "company_name", "sector", "P/E", "P/B", "EV/EBITDA",
            "FCF_yield_pct", "5yr_median_PE", "PE_vs_sector_median_pct", "flag"
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
        caution_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
        discount_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for _, row in df_summary.iterrows():
            row_vals = [
                row["company_id"],
                row["company_name"],
                row["sector"],
                row["P/E"] if pd.notnull(row["P/E"]) else "—",
                row["P/B"] if pd.notnull(row["P/B"]) else "—",
                row["EV/EBITDA"] if pd.notnull(row["EV/EBITDA"]) else "—",
                row["FCF_yield_pct"] if pd.notnull(row["FCF_yield_pct"]) else "—",
                row["5yr_median_PE"] if pd.notnull(row["5yr_median_PE"]) else "—",
                row["PE_vs_sector_median_pct"] if pd.notnull(row["PE_vs_sector_median_pct"]) else "—",
                row["flag"],
            ]
            ws.append(row_vals)
            cur_r = ws.max_row
            for c_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=cur_r, column=c_idx)
                cell.font = regular_font
                cell.border = thin_border
                if c_idx == 10:
                    cell.font = bold_font
                    if row["flag"] == "Caution":
                        cell.fill = caution_fill
                    elif row["flag"] == "Discount":
                        cell.fill = discount_fill

        for col in ws.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(excel_path)
        logger.info("Saved %d rows to %s", len(df_summary), excel_path)

        # Export output/valuation_flags.csv (Only Caution and Discount companies)
        df_flags = df_summary[df_summary["flag"].isin(["Caution", "Discount"])].copy()
        flags_csv = self.output_dir / "valuation_flags.csv"
        df_flags.to_csv(flags_csv, index=False)
        logger.info("Saved %d Caution & Discount flags to %s", len(df_flags), flags_csv)

        return df_summary, df_flags


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engine = ValuationEngine()
    summary_df, flags_df = engine.run_valuation_analysis()
    print(f"Valuation analysis complete: {len(summary_df)} companies analyzed, {len(flags_df)} flags raised.")
