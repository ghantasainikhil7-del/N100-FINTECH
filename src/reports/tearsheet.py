"""ReportLab 2-Page Company Tearsheet Generator for Nifty 100 constituents."""
from __future__ import annotations

import io
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

# Color palette
NAVY = colors.HexColor("#1B365D")
LIGHT_BG = colors.HexColor("#F8F9FA")
BORDER_COLOR = colors.HexColor("#D3D3D3")
GREEN = colors.HexColor("#2E7D32")
RED = colors.HexColor("#C62828")
DARK_GRAY = colors.HexColor("#333333")
LIGHT_GRAY = colors.HexColor("#777777")
CARD_BG = colors.HexColor("#EEF2F7")


class TearsheetGenerator:
    """Generates professional 2-page publication-grade PDF tearsheets for companies."""

    def __init__(
        self,
        db_path: str = "data/nifty100.db",
        output_dir: str = "reports/tearsheets",
    ):
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self) -> None:
        self.styles.add(ParagraphStyle(
            name="TearsheetTitle",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=colors.white,
        ))
        self.styles.add(ParagraphStyle(
            name="TearsheetSub",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#CBD5E1"),
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=NAVY,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="TileLabel",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=LIGHT_GRAY,
            alignment=1,  # Center
        ))
        self.styles.add(ParagraphStyle(
            name="TileValue",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=15,
            textColor=NAVY,
            alignment=1,  # Center
        ))
        self.styles.add(ParagraphStyle(
            name="ProBullet",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=GREEN,
        ))
        self.styles.add(ParagraphStyle(
            name="ConBullet",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=RED,
        ))
        self.styles.add(ParagraphStyle(
            name="BadgeText",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#0C5460"),
            alignment=1,
        ))

    def _create_chart_p1_revenue_profit(self, df_pl: pd.DataFrame) -> io.BytesIO:
        """Create 10-year Revenue & Net Profit comparative bar chart."""
        fig, ax = plt.subplots(figsize=(6.8, 2.3), dpi=130)
        if df_pl is None or df_pl.empty or "year" not in df_pl.columns:
            ax.text(0.5, 0.5, "P&L history not available", ha="center", va="center", fontsize=9, color="#757575", style="italic")
            ax.set_axis_off()
        else:
            df_valid = df_pl[df_pl["sales"].notnull()] if "sales" in df_pl.columns else df_pl
            df_sub = df_valid.tail(10).copy()
            years = [str(y).split("-")[0] for y in df_sub["year"]]
            sales = df_sub.get("sales", pd.Series(0, index=df_sub.index)).fillna(0) / 1000.0  # Convert to '000 Cr for compact axis
            pat = df_sub.get("net_profit", pd.Series(0, index=df_sub.index)).fillna(0) / 1000.0

            x = np.arange(len(years))
            width = 0.38

            ax.bar(x - width/2, sales, width, label="Revenue (Rs. k Cr)", color="#1B365D", alpha=0.9)
            ax.bar(x + width/2, pat, width, label="Net Profit (Rs. k Cr)", color="#2E7D32", alpha=0.9)

            ax.set_xticks(x)
            ax.set_xticklabels(years, fontsize=7.5, color="#333333")
            ax.tick_params(axis="y", labelsize=7.5)
            ax.legend(fontsize=7, frameon=False, loc="upper left")
            ax.set_title("10-Year Revenue & Net Profit Trajectory", fontsize=9, fontweight="bold", color="#1B365D", pad=5)
            ax.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_chart_p1_roe_roce(self, df_ratios: pd.DataFrame) -> io.BytesIO:
        """Create ROE and ROCE trend line chart."""
        fig, ax = plt.subplots(figsize=(6.8, 2.1), dpi=130)
        if df_ratios is None or df_ratios.empty or "year" not in df_ratios.columns:
            ax.text(0.5, 0.5, "Return ratios history not available", ha="center", va="center", fontsize=9, color="#757575", style="italic")
            ax.set_axis_off()
        else:
            df_valid = df_ratios[df_ratios["return_on_equity_pct"].notnull()] if "return_on_equity_pct" in df_ratios.columns else df_ratios
            df_sub = df_valid.tail(10).copy()
            years = [str(y).split("-")[0] for y in df_sub["year"]]
            roe = df_sub.get("return_on_equity_pct", pd.Series(0, index=df_sub.index)).fillna(0)
            roce = df_sub.get("return_on_capital_employed_pct", pd.Series(0, index=df_sub.index)).fillna(0)

            ax.plot(years, roe, marker="o", markersize=4, color="#1B365D", linewidth=1.8, label="ROE (%)")
            ax.plot(years, roce, marker="s", markersize=4, color="#D9534F", linewidth=1.8, linestyle="--", label="ROCE (%)")

            ax.tick_params(axis="both", labelsize=7.5)
            ax.set_ylim(bottom=0)
            ax.legend(fontsize=7, frameon=False, loc="upper right")
            ax.set_title("Return on Equity (ROE) & Return on Capital Employed (ROCE) Trend", fontsize=9, fontweight="bold", color="#1B365D", pad=5)
            ax.grid(axis="both", linestyle=":", alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_chart_p2_bs_composition(self, df_bs: pd.DataFrame) -> io.BytesIO:
        """Create Balance Sheet composition stacked bar chart."""
        fig, ax = plt.subplots(figsize=(6.8, 2.2), dpi=130)
        if df_bs is None or df_bs.empty or "year" not in df_bs.columns:
            ax.text(0.5, 0.5, "Balance Sheet history not available or bank reporting format", ha="center", va="center", fontsize=9, color="#757575", style="italic")
            ax.set_axis_off()
        else:
            df_sub = df_bs.tail(8).copy()
            years = [str(y).split("-")[0] for y in df_sub["year"]]
            equity = (df_sub.get("equity_capital", pd.Series(0, index=df_sub.index)).fillna(0) + df_sub.get("reserves", pd.Series(0, index=df_sub.index)).fillna(0)) / 1000.0
            debt = df_sub.get("borrowings", pd.Series(0, index=df_sub.index)).fillna(0) / 1000.0
            other = df_sub.get("other_liabilities", pd.Series(0, index=df_sub.index)).fillna(0) / 1000.0

            x = np.arange(len(years))
            width = 0.45

            ax.bar(x, equity, width, label="Net Worth / Equity", color="#1B365D")
            ax.bar(x, debt, width, bottom=equity, label="Borrowings (Debt)", color="#C62828")
            ax.bar(x, other, width, bottom=equity+debt, label="Other Liabilities", color="#757575")

            ax.set_xticks(x)
            ax.set_xticklabels(years, fontsize=7.5)
            ax.tick_params(axis="y", labelsize=7.5)
            ax.legend(fontsize=7, frameon=False, loc="upper left")
            ax.set_title("Capital Structure & Liabilities Breakdown (Rs. k Cr)", fontsize=9, fontweight="bold", color="#1B365D", pad=5)
            ax.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_chart_p2_cf_waterfall(self, cfo: float, cfi: float, cff: float, ncf: float) -> io.BytesIO:
        """Create Cash Flow component chart."""
        fig, ax = plt.subplots(figsize=(6.8, 2.0), dpi=130)
        labels = ["CFO (Ops)", "CFI (Capex)", "CFF (Financing)", "Net Cash Flow"]
        values = [cfo, cfi, cff, ncf]
        colors_bar = ["#2E7D32" if v >= 0 else "#C62828" for v in values]

        bars = ax.bar(labels, values, color=colors_bar, width=0.45)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.tick_params(axis="both", labelsize=7.5)
        ax.set_title("Latest Fiscal Cash Flow Distribution (Rs. Cr)", fontsize=9, fontweight="bold", color="#1B365D", pad=5)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        for bar in bars:
            yval = bar.get_height()
            offset = 15 if yval >= 0 else -25
            ax.annotate(f"Rs. {int(yval):,} Cr",
                        xy=(bar.get_x() + bar.get_width() / 2, yval),
                        xytext=(0, offset),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=7, fontweight="bold")

        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_tearsheet(
        self,
        ticker: str,
        co_meta: dict[str, Any],
        df_pl: pd.DataFrame,
        df_bs: pd.DataFrame,
        df_cf: pd.DataFrame,
        df_ratios: pd.DataFrame,
        pros: list[str],
        cons: list[str],
        cap_alloc_label: str = "Reinvestor",
    ) -> str:
        """Render publication-grade 2-page tearsheet PDF."""
        out_pdf = self.output_dir / f"{ticker}_tearsheet.pdf"
        doc = SimpleDocTemplate(
            str(out_pdf),
            pagesize=A4,
            leftMargin=28,
            rightMargin=28,
            topMargin=25,
            bottomMargin=25,
        )

        story = []
        uw = 538  # Usable width in points

        # ======================================================================
        # PAGE 1: HEADER, TILES, & PERFORMANCE CHARTS
        # ======================================================================

        # Navy Header Table
        co_name = co_meta.get("company_name", f"{ticker} Limited")
        sector = co_meta.get("broad_sector", "Nifty 100 Constituent")
        header_text = f"<b>{co_name} ({ticker})</b><br/><font size=8>{sector} | Nifty 100 Financial Tearsheet</font>"
        header_table = Table(
            [[Paragraph(header_text, self.styles["TearsheetTitle"]),
              Paragraph(datetime.now().strftime("As of %b %Y<br/>All Values in Rs. Cr"), self.styles["TearsheetSub"])]],
            colWidths=[uw * 0.75, uw * 0.25],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # KPI Tiles (6 Tiles in 2 Rows of 3)
        r_annual = df_ratios[df_ratios["return_on_equity_pct"].notnull()] if not df_ratios.empty and "return_on_equity_pct" in df_ratios.columns else df_ratios
        latest_r = r_annual.iloc[-1] if not r_annual.empty else (df_ratios.iloc[-1] if not df_ratios.empty else {})
        pl_annual = df_pl[df_pl["sales"].notnull()] if not df_pl.empty and "sales" in df_pl.columns else df_pl
        latest_pl = pl_annual.iloc[-1] if not pl_annual.empty else (df_pl.iloc[-1] if not df_pl.empty else {})

        def _safe_cr(val):
            try:
                return f"Rs. {int(float(val)):,} Cr" if pd.notnull(val) else "—"
            except Exception:
                return "—"

        def _safe_pct(val):
            try:
                return f"{float(val):.1f}%" if pd.notnull(val) else "—"
            except Exception:
                return "—"

        def _safe_num(val):
            try:
                return f"{float(val):.2f}" if pd.notnull(val) else "—"
            except Exception:
                return "—"

        rev_val = _safe_cr(latest_pl.get("sales"))
        np_val = _safe_cr(latest_pl.get("net_profit"))
        roe_val = _safe_pct(latest_r.get("return_on_equity_pct"))
        roce_val = _safe_pct(latest_r.get("return_on_capital_employed_pct"))
        de_val = _safe_num(latest_r.get("debt_to_equity"))
        fcf_val = _safe_cr(latest_r.get("free_cash_flow_cr"))

        tile_data = [
            [
                [Paragraph("ANNUAL REVENUE", self.styles["TileLabel"]), Paragraph(rev_val, self.styles["TileValue"])],
                [Paragraph("NET PROFIT (PAT)", self.styles["TileLabel"]), Paragraph(np_val, self.styles["TileValue"])],
                [Paragraph("RETURN ON EQUITY", self.styles["TileLabel"]), Paragraph(roe_val, self.styles["TileValue"])],
            ],
            [
                [Paragraph("ROCE", self.styles["TileLabel"]), Paragraph(roce_val, self.styles["TileValue"])],
                [Paragraph("DEBT-TO-EQUITY", self.styles["TileLabel"]), Paragraph(de_val, self.styles["TileValue"])],
                [Paragraph("FREE CASH FLOW", self.styles["TileLabel"]), Paragraph(fcf_val, self.styles["TileValue"])],
            ]
        ]

        tile_table = Table(tile_data, colWidths=[uw/3, uw/3, uw/3])
        tile_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tile_table)
        story.append(Spacer(1, 12))

        # Chart 1: 10-Year Revenue & Net Profit
        chart1_buf = self._create_chart_p1_revenue_profit(df_pl)
        story.append(Image(chart1_buf, width=uw, height=170))
        story.append(Spacer(1, 10))

        # Chart 2: ROE & ROCE Dual Trend
        chart2_buf = self._create_chart_p1_roe_roce(df_ratios)
        story.append(Image(chart2_buf, width=uw, height=160))

        # ======================================================================
        # PAGE 2: BALANCE SHEET, CASH FLOW, PROS/CONS & BADGES
        # ======================================================================
        story.append(PageBreak())

        # Page 2 Sub-Header
        p2_header = Table(
            [[Paragraph(f"<b>{co_name} ({ticker}) — Financial Structure & Qualitative Insights</b>", self.styles["SectionHeader"])]],
            colWidths=[uw]
        )
        p2_header.setStyle(TableStyle([
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -1), 1.5, NAVY),
        ]))
        story.append(p2_header)
        story.append(Spacer(1, 8))

        # Chart 3: Balance Sheet Composition
        chart3_buf = self._create_chart_p2_bs_composition(df_bs)
        story.append(Image(chart3_buf, width=uw, height=165))
        story.append(Spacer(1, 8))

        # Chart 4: Cash Flow Component Breakdown
        latest_cf = df_cf.iloc[-1] if not df_cf.empty else {}
        cfo = 0.0
        cfi = 0.0
        cff = 0.0
        try:
            cfo = float(latest_cf.get("operating_activity", 0) or 0)
        except Exception:
            pass
        try:
            cfi = float(latest_cf.get("investing_activity", 0) or 0)
        except Exception:
            pass
        try:
            cff = float(latest_cf.get("financing_activity", 0) or 0)
        except Exception:
            pass
        ncf = cfo + cfi + cff
        try:
            if pd.notnull(latest_cf.get("net_cash_flow")) and latest_cf.get("net_cash_flow") != 0:
                ncf = float(latest_cf.get("net_cash_flow"))
        except Exception:
            pass

        chart4_buf = self._create_chart_p2_cf_waterfall(cfo, cfi, cff, ncf)
        story.append(Image(chart4_buf, width=uw, height=155))
        story.append(Spacer(1, 8))

        # Capital Allocation Badge
        badge_table = Table(
            [[Paragraph(f"<b>CAPITAL ALLOCATION PROFILE:</b> {cap_alloc_label.upper()}", self.styles["BadgeText"])]],
            colWidths=[uw]
        )
        badge_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D1ECF1")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BEE5EB")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(badge_table)
        story.append(Spacer(1, 8))

        # Pros & Cons Side-by-Side Table with WORDWRAP
        pros_paragraphs = [Paragraph(f"• {p}", self.styles["ProBullet"]) for p in pros[:4]]
        cons_paragraphs = [Paragraph(f"• {c}", self.styles["ConBullet"]) for c in cons[:4]]

        pros_cell = [Paragraph("<b>KEY STRENGTHS (PROS)</b>", self.styles["SectionHeader"])] + pros_paragraphs
        cons_cell = [Paragraph("<b>KEY RISKS / WATCHOUTS (CONS)</b>", self.styles["SectionHeader"])] + cons_paragraphs

        side_by_side = Table(
            [[pros_cell, cons_cell]],
            colWidths=[(uw/2) - 5, (uw/2) - 5],
        )
        side_by_side.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F4FAF4")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FDF5F5")),
            ("BOX", (0, 0), (0, 0), 1, colors.HexColor("#C3E6CB")),
            ("BOX", (1, 0), (1, 0), 1, colors.HexColor("#F5C6CB")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(side_by_side)

        # Build Document
        doc.build(story)
        logger.info("Generated tearsheet PDF for %s at %s", ticker, out_pdf)
        return str(out_pdf)

    def generate_all_tearsheets(self) -> tuple[int, list[str]]:
        """Batch-generate tearsheets for all 92 companies, skipping those with < 3 years history."""
        conn = sqlite3.connect(self.db_path)
        try:
            df_companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
            df_sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
            df_pl = pd.read_sql_query("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
            df_bs = pd.read_sql_query("SELECT * FROM balancesheet ORDER BY company_id, year", conn)
            df_cf = pd.read_sql_query("SELECT * FROM cashflow ORDER BY company_id, year", conn)
            df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id, year", conn)
            df_pc = pd.read_sql_query("SELECT * FROM prosandcons", conn) if "prosandcons" in [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()] else pd.DataFrame()
        finally:
            conn.close()

        sector_map = {str(k).strip().upper(): v for k, v in zip(df_sectors["company_id"], df_sectors["broad_sector"])}
        pl_groups = {str(cid).strip().upper(): g.reset_index(drop=True) for cid, g in df_pl.groupby("company_id")}
        bs_groups = {str(cid).strip().upper(): g.reset_index(drop=True) for cid, g in df_bs.groupby("company_id")}
        cf_groups = {str(cid).strip().upper(): g.reset_index(drop=True) for cid, g in df_cf.groupby("company_id")}
        ratios_groups = {str(cid).strip().upper(): g.reset_index(drop=True) for cid, g in df_ratios.groupby("company_id")}

        # Load generated pros/cons if available
        pc_csv = Path("output/pros_cons_generated.csv")
        pc_map_pros: dict[str, list[str]] = {}
        pc_map_cons: dict[str, list[str]] = {}
        if pc_csv.exists():
            df_pc_gen = pd.read_csv(pc_csv)
            for cid, g in df_pc_gen.groupby("company_id"):
                pc_map_pros[str(cid).strip().upper()] = g[g["type"] == "pro"]["text"].tolist()
                pc_map_cons[str(cid).strip().upper()] = g[g["type"] == "con"]["text"].tolist()

        count = 0
        skipped: list[str] = []

        for _, row in df_companies.iterrows():
            ticker = str(row["id"]).strip().upper()
            co_pl = pl_groups.get(ticker, pd.DataFrame())
            co_bs = bs_groups.get(ticker, pd.DataFrame())
            co_cf = cf_groups.get(ticker, pd.DataFrame())
            co_ratios = ratios_groups.get(ticker, pd.DataFrame())

            if co_pl.empty or len(co_pl) < 3:
                skipped.append(ticker)
                continue

            co_meta = {
                "company_name": row["company_name"],
                "broad_sector": sector_map.get(ticker, "Diversified"),
            }

            pros = pc_map_pros.get(ticker, [
                "Strong historical profitability and sustained market presence.",
                "Robust franchise leadership within key industry segments."
            ])
            cons = pc_map_cons.get(ticker, [
                "Vulnerable to raw material price volatility and macro demand cycles.",
                "High competitive intensity from domestic and global peers."
            ])

            # Get capital allocation badge from latest row
            latest_cfo, latest_cfi, latest_cff = 0.0, 0.0, 0.0
            if not co_cf.empty:
                try:
                    latest_cfo = float(co_cf.iloc[-1].get("operating_activity", 0) or 0)
                except Exception:
                    pass
                try:
                    latest_cfi = float(co_cf.iloc[-1].get("investing_activity", 0) or 0)
                except Exception:
                    pass
                try:
                    latest_cff = float(co_cf.iloc[-1].get("financing_activity", 0) or 0)
                except Exception:
                    pass
            cap_badge = "Reinvestor" if latest_cfo > 0 and latest_cfi < 0 and latest_cff < 0 else "Capital Allocator"

            self.generate_tearsheet(
                ticker=ticker,
                co_meta=co_meta,
                df_pl=co_pl,
                df_bs=co_bs,
                df_cf=co_cf,
                df_ratios=co_ratios,
                pros=pros,
                cons=cons,
                cap_alloc_label=cap_badge,
            )
            count += 1

        # Write skipped tickers log
        if skipped:
            skip_df = pd.DataFrame({"company_id": skipped, "reason": "Less than 3 years financial history"})
            skip_df.to_csv("output/skipped_tearsheets.csv", index=False)

        logger.info("Completed tearsheet batch generation: %d generated, %d skipped", count, len(skipped))
        return count, skipped


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gen = TearsheetGenerator()
    c, s = gen.generate_all_tearsheets()
    print("Tearsheet generation complete. Generated:", c, "Skipped:", len(s))
