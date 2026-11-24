"""Sector PDF Report Generator creating 11 publication-grade Sector Intelligence Reports."""
from __future__ import annotations

import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import numpy as np
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
LIGHT_BG = colors.HexColor("#F8F9FA")
BORDER_COLOR = colors.HexColor("#D3D3D3")
GOLD = colors.HexColor("#FFEBAA")
CARD_BG = colors.HexColor("#EEF2F7")


class SectorReportGenerator:
    """Generates 11 sector PDF intelligence reports with median benchmarks and constituent comparisons."""

    def __init__(
        self,
        db_path: str = "data/nifty100.db",
        output_dir: str = "reports/sector",
    ):
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._init_styles()

    def _init_styles(self) -> None:
        self.styles.add(ParagraphStyle(
            name="SecTitle",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=17,
            textColor=colors.white,
        ))
        self.styles.add(ParagraphStyle(
            name="SecSub",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#CBD5E1"),
        ))
        self.styles.add(ParagraphStyle(
            name="SecHeader",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=NAVY,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="CellText",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=1,  # Center
        ))
        self.styles.add(ParagraphStyle(
            name="CellBold",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=1,
        ))

    def generate_sector_pdf(
        self,
        sector_name: str,
        df_constituents: pd.DataFrame,
        medians: dict[str, Any],
    ) -> str:
        """Render publication-grade PDF report for a sector."""
        safe_name = re.sub(r"[^\w\-]", "_", sector_name)
        out_pdf = self.output_dir / f"{safe_name}_report.pdf"

        doc = SimpleDocTemplate(
            str(out_pdf),
            pagesize=A4,
            leftMargin=28,
            rightMargin=28,
            topMargin=25,
            bottomMargin=25,
        )

        story = []
        uw = 538

        # Sector Banner
        banner_text = f"<b>SECTOR INTELLIGENCE REPORT: {sector_name.upper()}</b><br/><font size=8>Nifty 100 Industry Benchmark & Constituent Profiling</font>"
        meta_text = f"Generated: {datetime.now().strftime('%b %Y')}<br/>Companies: {len(df_constituents)}"
        header_table = Table(
            [[Paragraph(banner_text, self.styles["SecTitle"]),
              Paragraph(meta_text, self.styles["SecSub"])]],
            colWidths=[uw * 0.75, uw * 0.25],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # Sector Median Benchmark Tiles
        story.append(Paragraph("<b>1. SECTOR BENCHMARKS (MEDIANS)</b>", self.styles["SecHeader"]))
        med_tiles = [
            [
                Paragraph("<b>MEDIAN ROE</b><br/>" + f"{medians.get('roe', 0):.1f}%", self.styles["CellBold"]),
                Paragraph("<b>MEDIAN ROCE</b><br/>" + f"{medians.get('roce', 0):.1f}%", self.styles["CellBold"]),
                Paragraph("<b>MEDIAN NPM</b><br/>" + f"{medians.get('npm', 0):.1f}%", self.styles["CellBold"]),
                Paragraph("<b>MEDIAN D/E</b><br/>" + f"{medians.get('de', 0):.2f}", self.styles["CellBold"]),
            ]
        ]
        med_table = Table(med_tiles, colWidths=[uw/4]*4)
        med_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(med_table)
        story.append(Spacer(1, 12))

        # Sector Constituent Comparative Table
        story.append(Paragraph("<b>2. CONSTITUENT PEER COMPARISON</b>", self.styles["SecHeader"]))
        headers = [
            Paragraph("<b>Ticker</b>", self.styles["CellBold"]),
            Paragraph("<b>Company</b>", self.styles["CellBold"]),
            Paragraph("<b>Sales (Cr)</b>", self.styles["CellBold"]),
            Paragraph("<b>PAT (Cr)</b>", self.styles["CellBold"]),
            Paragraph("<b>ROE (%)</b>", self.styles["CellBold"]),
            Paragraph("<b>ROCE (%)</b>", self.styles["CellBold"]),
            Paragraph("<b>D/E</b>", self.styles["CellBold"]),
            Paragraph("<b>FCF (Cr)</b>", self.styles["CellBold"]),
            Paragraph("<b>Score</b>", self.styles["CellBold"]),
        ]
        table_rows = [headers]

        for _, row in df_constituents.iterrows():
            table_rows.append([
                Paragraph(str(row["company_id"]), self.styles["CellBold"]),
                Paragraph(str(row.get("company_name", ""))[:18], self.styles["CellText"]),
                Paragraph(f"Rs. {int(float(row.get('sales', 0))):,}" if pd.notnull(row.get('sales')) else "—", self.styles["CellText"]),
                Paragraph(f"Rs. {int(float(row.get('net_profit', 0))):,}" if pd.notnull(row.get('net_profit')) else "—", self.styles["CellText"]),
                Paragraph(f"{float(row.get('return_on_equity_pct', 0)):.1f}%" if pd.notnull(row.get('return_on_equity_pct')) else "—", self.styles["CellText"]),
                Paragraph(f"{float(row.get('return_on_capital_employed_pct', 0)):.1f}%" if pd.notnull(row.get('return_on_capital_employed_pct')) else "—", self.styles["CellText"]),
                Paragraph(f"{float(row.get('debt_to_equity', 0)):.2f}" if pd.notnull(row.get('debt_to_equity')) else "—", self.styles["CellText"]),
                Paragraph(f"Rs. {int(float(row.get('free_cash_flow_cr', 0))):,}" if pd.notnull(row.get('free_cash_flow_cr')) else "—", self.styles["CellText"]),
                Paragraph(f"{float(row.get('composite_quality_score', 0)):.1f}" if pd.notnull(row.get('composite_quality_score')) else "—", self.styles["CellBold"]),
            ])

        col_w = [50, 110, 58, 55, 45, 45, 40, 55, 45]
        comp_table = Table(table_rows, colWidths=col_w, repeatRows=1)
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        story.append(comp_table)

        doc.build(story)
        logger.info("Generated sector report for %s at %s", sector_name, out_pdf)
        return str(out_pdf)

    def generate_all_sector_reports(self) -> int:
        """Generate all 11 sector PDF reports."""
        conn = sqlite3.connect(self.db_path)
        try:
            df_companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
            df_sectors = pd.read_sql_query("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)
            
            # Select latest audited annual rows per company
            df_ratios_all = pd.read_sql_query(
                "SELECT * FROM financial_ratios WHERE return_on_equity_pct IS NOT NULL ORDER BY company_id, year ASC", 
                conn
            )
            df_pl_all = pd.read_sql_query(
                "SELECT company_id, year, sales, net_profit FROM profitandloss WHERE sales IS NOT NULL ORDER BY company_id, year ASC", 
                conn
            )
            df_ratios = df_ratios_all.groupby("company_id").last().reset_index()
            df_pl = df_pl_all.groupby("company_id").last().reset_index()
        finally:
            conn.close()

        df_merged = pd.merge(df_companies, df_sectors, left_on="id", right_on="company_id")
        df_merged = pd.merge(df_merged, df_ratios, on="company_id", how="left")
        df_merged = pd.merge(df_merged, df_pl, on="company_id", how="left")

        unique_sectors = sorted(df_merged["broad_sector"].dropna().unique())
        count = 0

        for sec in unique_sectors:
            sec_df = df_merged[df_merged["broad_sector"] == sec].copy()
            if sec_df.empty:
                continue

            medians = {
                "roe": float(sec_df["return_on_equity_pct"].dropna().median() or 0),
                "roce": float(sec_df["return_on_capital_employed_pct"].dropna().median() or 0),
                "npm": float(sec_df["net_profit_margin_pct"].dropna().median() or 0),
                "de": float(sec_df["debt_to_equity"].dropna().median() or 0),
            }

            self.generate_sector_pdf(sec, sec_df, medians)
            count += 1

        logger.info("Generated %d sector PDF reports in %s", count, self.output_dir)
        return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gen = SectorReportGenerator()
    cnt = gen.generate_all_sector_reports()
    print("Generated sector reports:", cnt)
