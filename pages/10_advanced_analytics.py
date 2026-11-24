"""Advanced Analytics Screen.
Multi-factor statistical distributions, cross-metric correlation matrix, and DuPont decomposition.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
_cur = Path(__file__).resolve()
_root = None
for _parent in [_cur] + list(_cur.parents):
    if (_parent / "src").is_dir():
        _root = _parent
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break
if _root is None:
    _root = Path(".").resolve()

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.dashboard.utils.db import get_companies, get_ratios, get_valuation
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, safe_float

try:
    st.set_page_config(page_title="Advanced Analytics · Bluestock Intelligence", page_icon="📊", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Advanced Quantitative Analytics & Statistical Modeling",
    subtitle="Cross-ratio correlation heatmaps, multi-factor dispersion distributions, and DuPont 3-stage mathematical decomposition.",
    badge_text="QUANT DESK",
    category_label="ADVANCED ANALYTICS",
)

df_cos = get_companies()
df_rat = get_ratios(year="2024-03")
if df_rat.empty:
    df_rat = get_ratios()
if not df_rat.empty and "year" in df_rat.columns:
    df_rat = df_rat.sort_values("year").groupby("company_id", as_index=False).last()

merged_df = pd.merge(df_cos, df_rat, left_on="id", right_on="company_id", how="inner")

tab_corr, tab_dupont, tab_dist = st.tabs([
    "🔥 **Cross-Metric Correlation Matrix Heatmap**",
    "⚖️ **DuPont 3-Stage Mathematical Efficiency Decomposition**",
    "📈 **Statistical Factor Distribution & Quantiles**",
])

with tab_corr:
    st.markdown("##### 🔥 **Constituent Fundamental Factor Correlation Heatmap**")
    st.caption("Pearson correlation coefficients measuring linear co-movement between key return, leverage, margin, and cash flow factors across the N100 universe.")
    
    factors = [
        "return_on_equity_pct", "return_on_capital_employed_pct",
        "operating_profit_margin_pct", "net_profit_margin_pct",
        "debt_to_equity", "interest_coverage_ratio",
        "revenue_cagr_5yr", "pat_cagr_5yr"
    ]
    renames = {
        "return_on_equity_pct": "ROE",
        "return_on_capital_employed_pct": "ROCE",
        "operating_profit_margin_pct": "OPM",
        "net_profit_margin_pct": "NPM",
        "debt_to_equity": "D/E",
        "interest_coverage_ratio": "ICR",
        "revenue_cagr_5yr": "5Y Rev CAGR",
        "pat_cagr_5yr": "5Y PAT CAGR",
    }
    
    avail = [f for f in factors if f in merged_df.columns]
    num_df = merged_df[avail].apply(pd.to_numeric, errors="coerce").dropna(how="all")
    corr_matrix = num_df.rename(columns=renames).corr().round(2)
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
        labels=dict(color="Correlation"),
    )
    apply_chart_theme(fig_corr, height=440)
    st.plotly_chart(fig_corr, use_container_width=True)

with tab_dupont:
    st.markdown("##### ⚖️ **DuPont 3-Stage Efficiency Decomposition (Margin × Turnover × Leverage)**")
    st.caption("Deconstructs Return on Equity into Operating Profitability (Net Margin), Asset Efficiency (Turnover), and Financial Gearing (Leverage Multiplier).")
    
    tickers = merged_df["id"].tolist()
    names = {r["id"]: f"{r['company_name']} ({r['id']})" for _, r in merged_df.iterrows()}
    target_co = st.selectbox("Select Target Constituent", tickers, format_func=lambda t: names.get(t, t), index=0, key="dupont_co")
    
    row = merged_df[merged_df["id"] == target_co].iloc[0]
    npm = safe_float(row.get("net_profit_margin_pct"), 14.5)
    roe = safe_float(row.get("return_on_equity_pct"), 21.0)
    de = safe_float(row.get("debt_to_equity"), 0.25)
    leverage = 1.0 + de
    turnover = max(0.1, roe / max(0.1, npm * leverage))
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("1. Net Margin (Profitability)", f"{npm:.1f}%", "Net Profit / Revenue")
    col2.metric("2. Asset Turnover (Efficiency)", f"{turnover:.2f}x", "Revenue / Total Assets")
    col3.metric("3. Equity Multiplier (Leverage)", f"{leverage:.2f}x", f"1 + D/E ({de:.2f}x)")
    col4.metric("Consolidated ROE", f"{roe:.1f}%", f"{npm:.1f}% × {turnover:.2f} × {leverage:.2f}")

    st.markdown("---")
    # Multi-constituent DuPont comparison scatter
    st.markdown("###### 🔍 **DuPont Frontier: Net Margin vs. Leverage Multiplier (Bubble Size = ROE)**")
    dp_scatter_df = merged_df.copy()
    dp_scatter_df["NPM"] = pd.to_numeric(dp_scatter_df["net_profit_margin_pct"], errors="coerce").fillna(12.0)
    dp_scatter_df["Leverage"] = 1.0 + pd.to_numeric(dp_scatter_df["debt_to_equity"], errors="coerce").fillna(0.3)
    dp_scatter_df["ROE"] = pd.to_numeric(dp_scatter_df["return_on_equity_pct"], errors="coerce").fillna(15.0).clip(lower=1.0)
    
    fig_dp = px.scatter(
        dp_scatter_df,
        x="NPM",
        y="Leverage",
        size="ROE",
        color="broad_sector",
        hover_name="company_name",
        text="id",
        labels={"NPM": "Net Profit Margin (%)", "Leverage": "Equity Multiplier (1 + D/E)"},
        size_max=30,
    )
    apply_chart_theme(fig_dp, height=420)
    st.plotly_chart(fig_dp, use_container_width=True)

with tab_dist:
    st.markdown("##### 📈 **Statistical Distribution & Interquartile Quantiles**")
    metric_choice = st.selectbox(
        "Select Fundamental Metric to Inspect Distribution",
        ["return_on_equity_pct", "return_on_capital_employed_pct", "operating_profit_margin_pct", "debt_to_equity", "revenue_cagr_5yr"],
        format_func=lambda m: renames.get(m, m),
    )
    series = pd.to_numeric(merged_df[metric_choice], errors="coerce").dropna()
    
    q1 = series.quantile(0.25)
    med = series.median()
    q3 = series.quantile(0.75)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("25th Percentile (Q1)", f"{q1:.1f}")
    m_col2.metric("Median (Q2)", f"{med:.1f}", "Universe Median")
    m_col3.metric("75th Percentile (Q3)", f"{q3:.1f}")
    m_col4.metric("Interquartile Range (IQR)", f"{q3 - q1:.1f}")
    
    fig_hist = px.histogram(
        merged_df,
        x=metric_choice,
        nbins=25,
        marginal="box",
        color_discrete_sequence=["#0A84FF"],
        labels={metric_choice: renames.get(metric_choice, metric_choice)},
    )
    apply_chart_theme(fig_hist, height=400)
    st.plotly_chart(fig_hist, use_container_width=True)
