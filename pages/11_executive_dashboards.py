"""Executive Dashboards Screen.
Boardroom-grade overview for CIOs, institutional portfolio managers, and research directors.
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

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.dashboard.utils.db import get_companies, get_ratios, get_valuation, get_sectors
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, safe_float, CHART_COLORS

try:
    st.set_page_config(page_title="Executive Dashboards · Bluestock Intelligence", page_icon="💻", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Executive & CIO Boardroom Intelligence",
    subtitle="Macro market capital distribution, corporate profit pool concentration, aggregate index health indicators, and risk surveillance.",
    badge_text="EXECUTIVE DESK",
    category_label="EXECUTIVE DASHBOARDS",
)

df_cos = get_companies()
df_val = get_valuation()
df_rat = get_ratios(year="2024-03")
if df_rat.empty:
    df_rat = get_ratios()
if not df_rat.empty and "year" in df_rat.columns:
    df_rat = df_rat.sort_values("year").groupby("company_id", as_index=False).last()

merged = pd.merge(df_cos, df_rat, left_on="id", right_on="company_id", how="left")
if not df_val.empty:
    vc = [c for c in ["company_id", "market_cap_crore", "price_to_earnings"] if c in df_val.columns]
    merged = pd.merge(merged, df_val[vc], on="company_id", how="left")
else:
    merged["market_cap_crore"] = 85000.0

total_mcap = merged["market_cap_crore"].fillna(0).sum()
med_roe = safe_float(merged["return_on_equity_pct"].dropna().median(), 18.2)
med_roce = safe_float(merged["return_on_capital_employed_pct"].dropna().median(), 20.4)
total_fcf = merged["free_cash_flow_cr"].fillna(0).sum()

# Executive Summary Tiles
e1, e2, e3, e4 = st.columns(4)
e1.metric("N100 Aggregate Market Value", f"₹{total_mcap/100000:,.1f} Lakh Cr", "92 Constituents")
e2.metric("Index Median ROE", f"{med_roe:.1f}%", "Capital Productivity")
e3.metric("Index Median ROCE", f"{med_roce:.1f}%", "Operating Yield")
e4.metric("Discretionary Cash Flow Pool", f"₹{total_fcf:,.0f} Cr", "Annual Operating Surplus")

st.markdown("---")

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown("##### 🏛️ **Top 15 Market Cap Giants & Index Concentration**")
    top_15 = merged.sort_values(by="market_cap_crore", ascending=False).head(15)
    
    fig_top = px.bar(
        top_15,
        x="market_cap_crore",
        y="company_name",
        orientation="h",
        color="broad_sector",
        hover_name="id",
        text=top_15["market_cap_crore"].apply(lambda v: f"₹{v:,.0f} Cr"),
        labels={"market_cap_crore": "Market Cap (₹ Crore)", "company_name": "Constituent"},
    )
    fig_top.update_layout(yaxis=dict(autorange="reversed"), height=480)
    apply_chart_theme(fig_top, height=480)
    st.plotly_chart(fig_top, use_container_width=True)

with col_right:
    st.markdown("##### 🌐 **Sector Profit Pool vs. Market Weight Allocation**")
    sec_agg = merged.groupby("broad_sector").agg(
        Market_Cap=("market_cap_crore", "sum"),
        Constituents=("id", "count"),
        Median_ROE=("return_on_equity_pct", "median"),
    ).reset_index().sort_values(by="Market_Cap", ascending=False)
    
    fig_pie = px.pie(
        sec_agg,
        values="Market_Cap",
        names="broad_sector",
        hole=0.45,
        color_discrete_sequence=CHART_COLORS,
    )
    fig_pie.update_traces(textinfo="percent+label", hovertemplate="<b>%{label}</b><br>Market Cap: ₹%{value:,.0f} Cr (%{percent})<extra></extra>")
    apply_chart_theme(fig_pie, height=480)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Executive Watchlist Table
st.markdown("##### 📋 **Institutional Leaderboard (Top 25 Constituents by Comprehensive Scale)**")
table_cols = ["id", "company_name", "broad_sector", "market_cap_crore", "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr"]
renames = {
    "id": "Ticker", "company_name": "Company Name", "broad_sector": "Sector",
    "market_cap_crore": "Market Cap (₹ Cr)", "return_on_equity_pct": "ROE (%)",
    "debt_to_equity": "D/E Ratio", "free_cash_flow_cr": "FCF (₹ Cr)",
}
disp_tbl = merged[table_cols].sort_values(by="market_cap_crore", ascending=False).head(25).rename(columns=renames)
st.dataframe(disp_tbl, use_container_width=True, hide_index=True)
