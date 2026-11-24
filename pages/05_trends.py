"""Trend Analysis Screen with Multi-Metric Overlays and YoY Annotations."""
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
import plotly.graph_objects as go
import streamlit as st
from src.dashboard.utils.db import get_companies, get_pl, get_ratios
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css

try:
    st.set_page_config(page_title="Trend Analysis · N100 Analytics", page_icon="📈", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Multi-Year Fundamental Trend Analysis",
    subtitle="Inspect 10-year growth trajectories, overlay multiple metrics, and analyze year-over-year operational inflections.",
    badge_text="TREND TRAJECTORY",
)

df_cos = get_companies()
if df_cos.empty:
    st.error("No companies found.")
    st.stop()

# Company Search
st.sidebar.markdown("### 🔍 **Target Company**")
tickers = df_cos["id"].unique().tolist()
ticker_to_name = {r["id"]: f"{r['company_name']} ({r['id']})" for _, r in df_cos.iterrows()}
qp_co = ""
try:
    if hasattr(st, "query_params"):
        qp_co = str(st.query_params.get("company", "") or st.query_params.get("ticker", "")).strip().lower()
except Exception:
    pass

default_idx = 0
if qp_co:
    for i, t in enumerate(tickers):
        if t.lower() == qp_co or qp_co in ticker_to_name.get(t, "").lower() or ticker_to_name.get(t, "").lower().startswith(qp_co):
            default_idx = i
            break

selected_ticker = st.sidebar.selectbox(
    "Select Target Company",
    tickers,
    format_func=lambda t: ticker_to_name.get(t, t),
    index=default_idx,
)


df_pl = get_pl(ticker=selected_ticker)
df_r = get_ratios(ticker=selected_ticker)

merged_history = pd.merge(df_pl, df_r, on=["company_id", "year"], how="outer").sort_values(by="year")

if merged_history.empty:
    st.warning("No multi-year financial history available for this company.")
    st.stop()

# Data-availability note if fewer than 10 years (Sprint 4 Section 37)
if len(merged_history) < 10:
    st.info(f"ℹ️ Note: {len(merged_history)} years of historical financial data are available for {selected_ticker} (fewer than 10 years available).")

# Multi-metric selector (Up to 3)
available_metrics = {
    "Sales / Revenue (₹ Cr)": "sales",
    "Operating Profit (₹ Cr)": "operating_profit",
    "Net Profit (PAT) (₹ Cr)": "net_profit",
    "Return on Equity (%)": "return_on_equity_pct",
    "ROCE (%)": "return_on_capital_employed_pct",
    "Operating Margin (%)": "operating_profit_margin_pct",
    "Free Cash Flow (₹ Cr)": "free_cash_flow_cr",
    "Debt-to-Equity": "debt_to_equity",
}

col_sel, col_mode = st.columns([2.2, 1.2])

with col_sel:
    chosen_metric_labels = st.multiselect(
        "Choose up to 3 Fundamental Metrics to Overlay on Trajectory",
        list(available_metrics.keys()),
        default=["Sales / Revenue (₹ Cr)", "Net Profit (PAT) (₹ Cr)"],
        max_selections=3,
    )

with col_mode:
    view_mode = st.radio(
        "Trajectory Visualization Mode",
        ["Absolute Financial Values", "Indexed Growth (Base 100)"],
        horizontal=True,
    )

if not chosen_metric_labels:
    st.info("Please select at least one metric to display trends.")
    st.stop()

fig = go.Figure()
colors_list = ["#0A84FF", "#30D158", "#FF9F0A"]

for idx, label in enumerate(chosen_metric_labels):
    col_name = available_metrics[label]
    if col_name in merged_history.columns:
        series = pd.to_numeric(merged_history[col_name], errors="coerce").fillna(0)
        years = merged_history["year"]

        if view_mode == "Indexed Growth (Base 100)":
            base_val = float(series.iloc[0]) if len(series) > 0 and series.iloc[0] != 0 else 1.0
            norm_series = (series / abs(base_val)) * 100.0
            
            idx_annotations = []
            for i in range(len(norm_series)):
                idx_annotations.append(f"{norm_series.iloc[i]:.0f}")

            fig.add_trace(go.Scatter(
                x=years,
                y=norm_series,
                mode="lines+markers+text",
                name=f"{label} (Indexed)",
                text=idx_annotations,
                textposition="top center",
                line=dict(color=colors_list[idx % len(colors_list)], width=3),
                marker=dict(size=8),
                hovertemplate="<b>%{x}</b><br>Indexed Level: <b>%{y:.1f}</b> (FY15=100)<extra></extra>",
            ))
        else:
            annotations_text = []
            for i in range(len(series)):
                if i == 0 or series.iloc[i-1] == 0:
                    annotations_text.append(f"{series.iloc[i]:,.0f}")
                else:
                    pct_yoy = ((series.iloc[i] - series.iloc[i-1]) / abs(series.iloc[i-1])) * 100.0
                    annotations_text.append(f"{series.iloc[i]:,.0f} ({pct_yoy:+.1f}%)")

            fig.add_trace(go.Scatter(
                x=years,
                y=series,
                mode="lines+markers+text",
                name=label,
                text=annotations_text,
                textposition="top center",
                line=dict(color=colors_list[idx % len(colors_list)], width=3),
                marker=dict(size=8),
                hovertemplate="<b>%{x}</b><br>Value: <b>%{y:,.1f}</b><extra></extra>",
            ))

apply_chart_theme(fig, height=480)
fig.update_layout(
    yaxis_title="Normalized Level (FY15=100)" if view_mode == "Indexed Growth (Base 100)" else "Financial Metric Value",
    xaxis_title="Audited Fiscal Period",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# Quantitative Compounding Diagnostics Ribbon
first_col = available_metrics[chosen_metric_labels[0]]
if first_col in merged_history.columns:
    s = pd.to_numeric(merged_history[first_col], errors="coerce").dropna()
    if len(s) >= 2:
        val_start = float(s.iloc[0])
        val_end = float(s.iloc[-1])
        n_years = len(s) - 1
        
        cagr_full = None
        if val_start > 0 and val_end > 0 and n_years > 0:
            cagr_full = ((val_end / val_start) ** (1.0 / n_years) - 1.0) * 100.0
            
        cagr_3yr = None
        if len(s) >= 4:
            v_3 = float(s.iloc[-4])
            if v_3 > 0 and val_end > 0:
                cagr_3yr = ((val_end / v_3) ** (1.0 / 3.0) - 1.0) * 100.0
                
        cagr_5yr = None
        if len(s) >= 6:
            v_5 = float(s.iloc[-6])
            if v_5 > 0 and val_end > 0:
                cagr_5yr = ((val_end / v_5) ** (1.0 / 5.0) - 1.0) * 100.0
                
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        c_col1.metric("3-Year Trajectory CAGR", f"{cagr_3yr:+.1f}%" if cagr_3yr is not None else "—", chosen_metric_labels[0])
        c_col2.metric("5-Year Compounding CAGR", f"{cagr_5yr:+.1f}%" if cagr_5yr is not None else "—", "Medium-Term Growth")
        c_col3.metric("Full Period Trajectory CAGR", f"{cagr_full:+.1f}%" if cagr_full is not None else "—", "Decade Expansion")
        c_col4.metric("Peak to Trough Spread", f"{s.max() - s.min():,.0f}", f"Peak: {s.max():,.0f} | Min: {s.min():,.0f}")

st.markdown("---")

st.markdown("##### 📋 **Tabular Multi-Year Financial Series**")
rev_map = {available_metrics[m]: m for m in chosen_metric_labels if available_metrics[m] in merged_history.columns}
display_cols = ["year"] + list(rev_map.keys())
clean_df = merged_history[display_cols].copy().rename(columns={"year": "Fiscal Year", **rev_map})
st.dataframe(clean_df, use_container_width=True, hide_index=True)

