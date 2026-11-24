"""Portfolio Summary PDF Generator creating a multi-page compilation of all 92 companies with trend indicators."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

NAVY = colors.HexColor("#1B365D")
BORDER_COLOR = colors.HexColor("#D3D3D3")
CARD_BG = colors.HexColor("#EEF2F7")
LIGHT_GRAY = colors.HexColor("#777777")
GREEN = colors.HexColor("#2E7D32")
RED = colors.HexColor("#C62828")


class PortfolioReportGenerator:
    """Generates a comprehensive master portfolio summary PDF with one page per company and trend indicators."""

    def __init__(
        self,
        db_path: str = "data/nifty100.db",
        output_dir: str = "reports/portfolio",
    ):
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._init_styles()

    def _init_styles(self) -> None:
        self.styles.add(ParagraphStyle(
            name="PortTitle",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=colors.white,
        ))
        self.styles.add(ParagraphStyle(
            name="PortSub",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#CBD5E1"),
            alignment=2,  # Right
        ))
        self.styles.add(ParagraphStyle(
            name="PortCoHeader",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            textColor=NAVY,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="PortMeta",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=LIGHT_GRAY,
            spaceAfter=10,
        ))
        self.styles.add(ParagraphStyle(
            name="TableHdr",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="TableTxt",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="ArrowUp",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=GREEN,
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="ArrowDown",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=RED,
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="ArrowFlat",
            fontName="Helvetica",
            fontSize=11,
            leading=13,
            textColor=LIGHT_GRAY,
            alignment=1,
        ))

    @staticmethod
    def _get_trend_arrow(curr: Optional[float], prev: Optional[float], tolerance_pct: float = 2.0, reverse: bool = False) -> tuple[str, str]:
        """Return (arrow_symbol, style_name) based on YoY movement. Reversed for leverage/debt."""
        if curr is None or prev is None or prev == 0:
            return ("—", "ArrowFlat")
        pct_change = ((curr - prev) / abs(prev)) * 100.0
        if pct_change > tolerance_pct:
            return ("↑", "ArrowDown" if reverse else "ArrowUp")
        elif pct_change < -tolerance_pct:
            return ("↓", "ArrowUp" if reverse else "ArrowDown")
        else:
            return ("→", "ArrowFlat")

    def generate_portfolio_pdf(self) -> str:
        """Generate one-page-per-company portfolio summary PDF."""
        out_pdf = self.output_dir / "portfolio_summary.pdf"
        conn = sqlite3.connect(self.db_path)
        try:
            df_companies = pd.read_sql_query("SELECT id, company_name, about_company FROM companies ORDER BY id ASC", conn)
            df_sectors = pd.read_sql_query("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)
            df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id, year ASC", conn)
            df_pl = pd.read_sql_query("SELECT company_id, year, sales, net_profit FROM profitandloss ORDER BY company_id, year ASC", conn)
        finally:
            conn.close()

        sector_map = dict(zip(df_sectors["company_id"], df_sectors["broad_sector"]))
        sub_sector_map = dict(zip(df_sectors["company_id"], df_sectors["sub_sector"]))
        ratios_groups = {cid: g.reset_index(drop=True) for cid, g in df_ratios.groupby("company_id")}
        pl_groups = {cid: g.reset_index(drop=True) for cid, g in df_pl.groupby("company_id")}

        doc = SimpleDocTemplate(
            str(out_pdf),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        uw = 523

        n_cos = len(df_companies)
        for idx, co_row in df_companies.iterrows():
            ticker = str(co_row["id"])
            co_name = str(co_row["company_name"])
            sector = sector_map.get(ticker, "Constituent")
            sub_sec = sub_sector_map.get(ticker, "")
            about = str(co_row.get("about_company", "")) or f"{co_name} is a leading constituent of the Nifty 100 index."

            r_df = ratios_groups.get(ticker, pd.DataFrame())
            p_df = pl_groups.get(ticker, pd.DataFrame())

            # Filter to rows where annual metrics are computed
            r_annual = r_df[r_df["return_on_equity_pct"].notnull()] if not r_df.empty and "return_on_equity_pct" in r_df.columns else r_df
            p_annual = p_df[p_df["sales"].notnull()] if not p_df.empty and "sales" in p_df.columns else p_df

            curr_r = r_annual.iloc[-1] if not r_annual.empty else (r_df.iloc[-1] if not r_df.empty else {})
            prev_r = r_annual.iloc[-2] if len(r_annual) >= 2 else (r_df.iloc[-2] if len(r_df) >= 2 else curr_r)

            curr_p = p_annual.iloc[-1] if not p_annual.empty else (p_df.iloc[-1] if not p_df.empty else {})
            prev_p = p_annual.iloc[-2] if len(p_annual) >= 2 else (p_df.iloc[-2] if len(p_df) >= 2 else curr_p)

            # Top Header Bar
            header_table = Table(
                [[Paragraph(f"<b>NIFTY 100 PORTFOLIO SUMMARY — {ticker}</b>", self.styles["PortTitle"]),
                  Paragraph(f"Company {idx+1} of {n_cos}<br/>{datetime.now().strftime('%B %Y')}", self.styles["PortSub"])]],
                colWidths=[uw * 0.70, uw * 0.30],
            )
            header_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 14))

            # Company Details
            story.append(Paragraph(f"<b>{co_name}</b>", self.styles["PortCoHeader"]))
            story.append(Paragraph(f"<b>Sector:</b> {sector} | <b>Sub-Sector:</b> {sub_sec}", self.styles["PortMeta"]))
            story.append(Paragraph(f"<i>{about[:300]}...</i>", self.styles["PortMeta"]))
            story.append(Spacer(1, 10))

            # Top 6 Core KPIs Table with Trend Arrows
            kpi_configs = [
                ("Revenue", curr_p.get("sales"), prev_p.get("sales"), "Rs. {:,.0f} Cr", False),
                ("Net Profit", curr_p.get("net_profit"), prev_p.get("net_profit"), "Rs. {:,.0f} Cr", False),
                ("Return on Equity", curr_r.get("return_on_equity_pct"), prev_r.get("return_on_equity_pct"), "{:.1f}%", False),
                ("ROCE", curr_r.get("return_on_capital_employed_pct"), prev_r.get("return_on_capital_employed_pct"), "{:.1f}%", False),
                ("Debt to Equity", curr_r.get("debt_to_equity"), prev_r.get("debt_to_equity"), "{:.2f}", True),
                ("Free Cash Flow", curr_r.get("free_cash_flow_cr"), prev_r.get("free_cash_flow_cr"), "Rs. {:,.0f} Cr", False),
            ]

            table_data = [
                [
                    Paragraph("<b>Key Performance Indicator</b>", self.styles["TableHdr"]),
                    Paragraph("<b>Previous Year</b>", self.styles["TableHdr"]),
                    Paragraph("<b>Latest Year</b>", self.styles["TableHdr"]),
                    Paragraph("<b>YoY Change</b>", self.styles["TableHdr"]),
                    Paragraph("<b>Trend</b>", self.styles["TableHdr"]),
                ]
            ]

            for name, c_val, p_val, fmt, rev_flag in kpi_configs:
                arrow, style_name = self._get_trend_arrow(c_val, p_val, reverse=rev_flag)
                p_str = fmt.format(p_val) if pd.notnull(p_val) else "—"
                c_str = fmt.format(c_val) if pd.notnull(c_val) else "—"

                if pd.notnull(c_val) and pd.notnull(p_val) and p_val != 0:
                    diff_pct = ((c_val - p_val) / abs(p_val)) * 100.0
                    change_str = f"{diff_pct:+.1f}%"
                else:
                    change_str = "—"

                table_data.append([
                    Paragraph(f"<b>{name}</b>", self.styles["TableTxt"]),
                    Paragraph(p_str, self.styles["TableTxt"]),
                    Paragraph(c_str, self.styles["TableTxt"]),
                    Paragraph(change_str, self.styles["TableTxt"]),
                    Paragraph(arrow, self.styles[style_name]),
                ])

            kpi_table = Table(table_data, colWidths=[uw * 0.35, uw * 0.18, uw * 0.18, uw * 0.15, uw * 0.14])
            kpi_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CARD_BG]),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 14))

            # Composite Score and Quality Summary Box
            comp_score = curr_r.get("composite_quality_score", 65.0)
            score_box = Table(
                [[Paragraph(f"<b>COMPOSITE QUALITY SCORE: {comp_score:.1f} / 100</b>", self.styles["PortTitle"]),
                  Paragraph("<b>METHODOLOGY:</b> 35% Profitability, 30% Cash Quality, 20% Growth, 15% Leverage", self.styles["PortSub"])]],
                colWidths=[uw * 0.5, uw * 0.5]
            )
            score_box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(score_box)

            # Page break between companies (except on last)
            if idx < n_cos - 1:
                story.append(PageBreak())

        doc.build(story)
        logger.info("Generated master portfolio summary PDF at %s (%d companies)", out_pdf, n_cos)
        return str(out_pdf)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gen = PortfolioReportGenerator()
    out = gen.generate_portfolio_pdf()
    print("Portfolio summary generated:", out)
