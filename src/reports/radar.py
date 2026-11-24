"""Radar / Polar Chart Generator for Peer Comparison Engine."""
from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CLI execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analytics.peer import DEFAULT_PEER_GROUPS, load_peer_groups

logger = logging.getLogger(__name__)

# Exactly 8 radar axes as required by specification
RADAR_METRICS = [
    ("return_on_equity_pct", "ROE", 0, 50),
    ("return_on_capital_employed_pct", "ROCE", 0, 50),
    ("net_profit_margin_pct", "NPM", 0, 40),
    ("debt_to_equity", "D/E Score", 0, 100),  # Inverted into 0-100 score
    ("free_cash_flow_cr", "FCF Score", 0, 100),
    ("pat_cagr_5yr", "PAT Growth", 0, 40),
    ("revenue_cagr_5yr", "Rev Growth", 0, 40),
    ("composite_quality_score", "Quality Score", 0, 100),
]


class RadarChartGenerator:
    """Generates 8-axis polar radar charts with peer group average overlay."""

    def __init__(
        self,
        db_path: str | Path = "data/nifty100.db",
        output_dir: str | Path = "reports/radar_charts",
    ):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            alt = Path("nifty100.db")
            if alt.exists():
                self.db_path = alt
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.peer_groups = load_peer_groups(self.db_path)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize ticker or company name for safe filesystem storage."""
        return re.sub(r'[\\/*?:"<>|]', "", name).strip().upper()

    def _normalize_radar_val(self, metric_id: str, val: Any) -> float:
        """Normalize metric value onto a standard 0 to 100 scale for visual plotting."""
        if pd.isna(val) or val is None:
            return 20.0  # baseline placeholder

        v = float(val)
        if metric_id == "debt_to_equity":
            # Invert: D/E = 0 -> 100, D/E = 1 -> 75, D/E = 2 -> 50, D/E >= 4 -> 10
            return max(5.0, min(100.0, 100.0 - (v * 25.0)))
        elif metric_id == "free_cash_flow_cr":
            return 80.0 if v > 0 else 20.0
        elif metric_id in {"return_on_equity_pct", "return_on_capital_employed_pct"}:
            return max(0.0, min(100.0, (v / 40.0) * 100.0))
        elif metric_id in {"net_profit_margin_pct", "pat_cagr_5yr", "revenue_cagr_5yr"}:
            return max(0.0, min(100.0, (v / 30.0) * 100.0))
        elif metric_id == "composite_quality_score":
            return max(0.0, min(100.0, v))
        return 50.0

    def generate_chart_for_ticker(
        self,
        ticker: str,
        df_ratios: pd.DataFrame,
        peer_group_name: Optional[str] = None,
        peer_members: Optional[list[str]] = None,
    ) -> str:
        """Render polar radar chart for a company with peer average overlay."""
        clean_ticker = self.sanitize_filename(ticker)
        out_file = self.output_dir / f"{clean_ticker}_radar.png"

        # Ticker values
        co_row = df_ratios[df_ratios["company_id"] == ticker]
        if co_row.empty:
            try:
                conn = sqlite3.connect(self.db_path)
                df_fallback = pd.read_sql_query(
                    "SELECT * FROM financial_ratios WHERE company_id = ? AND return_on_equity_pct IS NOT NULL ORDER BY year DESC LIMIT 1;",
                    conn,
                    params=(ticker,),
                )
                conn.close()
                if not df_fallback.empty:
                    co_row = df_fallback
            except Exception:
                pass

        if co_row.empty:
            co_vals = [50.0] * len(RADAR_METRICS)
        else:
            co_vals = [
                self._normalize_radar_val(m_id, co_row.iloc[0].get(m_id))
                for m_id, _, _, _ in RADAR_METRICS
            ]

        # Peer average values
        if peer_members:
            sub = df_ratios[df_ratios["company_id"].isin(peer_members)]
            peer_vals = []
            for m_id, _, _, _ in RADAR_METRICS:
                avg_m = sub[m_id].dropna().mean() if m_id in sub.columns else 50.0
                peer_vals.append(self._normalize_radar_val(m_id, avg_m))
        else:
            # Universe average fallback for companies without peer group
            peer_vals = []
            for m_id, _, _, _ in RADAR_METRICS:
                avg_m = df_ratios[m_id].dropna().mean() if m_id in df_ratios.columns else 50.0
                peer_vals.append(self._normalize_radar_val(m_id, avg_m))

        # Close polar polygons
        labels = [name for _, name, _, _ in RADAR_METRICS]
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        co_plot = co_vals + [co_vals[0]]
        peer_plot = peer_vals + [peer_vals[0]]
        angles_plot = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        plt.subplots_adjust(top=0.85, bottom=0.15)

        # Plot company polygon (Filled)
        ax.plot(angles_plot, co_plot, color="#1B365D", linewidth=2.0, label=ticker)
        ax.fill(angles_plot, co_plot, color="#1B365D", alpha=0.25)

        # Plot peer average (Dashed outline)
        peer_label = f"{peer_group_name} Avg" if peer_group_name else "Nifty 100 Avg"
        ax.plot(angles_plot, peer_plot, color="#D9534F", linewidth=1.8, linestyle="--", label=peer_label)

        # Polish polar axes
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles), labels, fontsize=9, fontweight="bold", color="#333333")
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color="#888888")
        ax.grid(color="#E0E0E0", linestyle=":", linewidth=0.8)

        # Title and legend
        ax.set_title(f"{ticker} — Financial Health vs Peers", size=12, fontweight="bold", y=1.1, color="#1B365D")
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8, frameon=True)

        fig.savefig(out_file, dpi=120, bbox_inches="tight")
        plt.close(fig)
        return str(out_file)

    def generate_all_radar_charts(self, year: Optional[str] = None) -> int:
        """Generate radar chart PNGs across all constituents, handling unassigned peers gracefully."""
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
            df_companies = pd.read_sql_query("SELECT id FROM companies", conn)
            all_tickers = df_companies["id"].tolist()

            # Map ticker to peer group
            ticker_to_group: dict[str, str] = {}
            for gname, ginfo in self.peer_groups.items():
                for m in ginfo["members"]:
                    ticker_to_group[m.upper()] = gname

            count = 0
            for ticker in all_tickers:
                t = ticker.upper()
                gname = ticker_to_group.get(t)
                members = self.peer_groups[gname]["members"] if gname else None
                self.generate_chart_for_ticker(t, df_ratios, gname, members)
                count += 1

            logger.info("Generated %d radar charts in %s", count, self.output_dir)
            return count
        finally:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    gen = RadarChartGenerator()
    cnt = gen.generate_all_radar_charts()
    print("Radar chart generation complete. Total charts:", cnt)
