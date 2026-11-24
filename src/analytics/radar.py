"""
Nifty 100 Financial Intelligence Platform · Radar / Polar Chart Generator
Generates 8-axis institutional radar charts for all constituents vs peer group averages.
Sprint 3 · Day 19
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.analytics.peer import DEFAULT_PEER_GROUPS

RADAR_AXES = [
    {"id": "return_on_equity_pct", "name": "ROE", "scale": 50.0},
    {"id": "return_on_capital_employed_pct", "name": "ROCE", "scale": 50.0},
    {"id": "net_profit_margin_pct", "name": "NPM", "scale": 30.0},
    {"id": "de_score", "name": "D/E Score", "scale": 100.0},
    {"id": "fcf_score", "name": "FCF Score", "scale": 100.0},
    {"id": "pat_cagr_5yr", "name": "PAT Growth", "scale": 30.0},
    {"id": "revenue_cagr_5yr", "name": "Rev Growth", "scale": 25.0},
    {"id": "composite_quality_score", "name": "Quality Score", "scale": 100.0},
]


def generate_company_radar_chart(
    company_id: str,
    company_metrics: Dict[str, float],
    peer_avg_metrics: Dict[str, float],
    peer_group_name: str,
    output_dir: Path = Path("reports/radar_charts")
) -> Path:
    """
    Renders an 8-axis polar radar chart for a company against its peer group average.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{company_id}_radar.png"

    labels = [axis["name"] for axis in RADAR_AXES]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Close polygons
    angles += angles[:1]

    # Normalize metrics to 0-100 scale for plotting
    def norm_val(axis_info, val):
        if val is None or np.isnan(val):
            return 20.0
        scale = axis_info["scale"]
        return max(5.0, min(100.0, (val / scale) * 100.0))

    comp_values = [norm_val(axis, company_metrics.get(axis["id"], 20.0)) for axis in RADAR_AXES]
    comp_values += comp_values[:1]

    peer_values = [norm_val(axis, peer_avg_metrics.get(axis["id"], 20.0)) for axis in RADAR_AXES]
    peer_values += peer_values[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), facecolor="white")
    ax.set_facecolor("white")

    # Set angles and labels
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=11, weight="bold", color="#1c2833")

    # Grid lines and styling
    ax.set_rlabel_position(22.5)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], color="#7f8c8d", size=9)
    ax.set_ylim(0, 105)
    ax.grid(color="#d5d8dc", linestyle=":", linewidth=0.8)

    # Plot company filled polygon
    ax.plot(angles, comp_values, color="#1b4f72", linewidth=2.2, label=company_id)
    ax.fill(angles, comp_values, color="#2e86c1", alpha=0.25)

    # Plot peer average dashed overlay
    ax.plot(angles, peer_values, color="#cb4335", linewidth=2.0, linestyle="--", label=f"{peer_group_name} Avg")

    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), frameon=True, facecolor="white", edgecolor="#eaeded")
    plt.title(f"{company_id} — Financial Health vs Peers", size=14, weight="bold", pad=25, color="#1b4f72")

    plt.tight_layout()
    plt.savefig(out_file, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return out_file


def generate_all_radar_charts(
    db_path: str = "data/nifty100.db",
    output_dir: str = "reports/radar_charts"
):
    """Batch generate radar charts for all constituents."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        df_ratios = pd.read_sql_query(
            "SELECT * FROM financial_ratios WHERE year = (SELECT MAX(year) FROM financial_ratios);", conn
        )
    finally:
        conn.close()

    if df_ratios.empty:
        return

    # Add synthetic scores if missing
    if "de_score" not in df_ratios.columns:
        df_ratios["de_score"] = np.where(df_ratios["debt_to_equity"] <= 0.1, 95.0, np.maximum(10.0, 100.0 - (df_ratios["debt_to_equity"] * 25.0)))
    if "fcf_score" not in df_ratios.columns:
        df_ratios["fcf_score"] = np.where(df_ratios["free_cash_flow_cr"] > 0, 85.0, 25.0)

    for group_name, info in DEFAULT_PEER_GROUPS.items():
        members = info["members"]
        sub = df_ratios[df_ratios["company_id"].isin(members)]
        if sub.empty:
            continue

        # Compute group averages
        avg_metrics = {}
        for axis in RADAR_AXES:
            col = axis["id"]
            if col in sub.columns:
                avg_metrics[col] = float(sub[col].dropna().mean()) if not sub[col].dropna().empty else 20.0
            else:
                avg_metrics[col] = 20.0

        for _, row in sub.iterrows():
            cid = row["company_id"]
            comp_metrics = {axis["id"]: (float(row[axis["id"]]) if pd.notnull(row.get(axis["id"])) else 20.0) for axis in RADAR_AXES}
            generate_company_radar_chart(cid, comp_metrics, avg_metrics, group_name, out_path)


if __name__ == "__main__":
    generate_all_radar_charts()
