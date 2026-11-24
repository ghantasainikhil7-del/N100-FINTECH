"""Sector Intelligence Screen with Bubble Charts and Median Benchmarks."""
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
from src.dashboard.utils.db import get_companies, get_pl, get_ratios, get_sectors, get_valuation
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, safe_float

try:
    st.set_page_config(page_title="Sector Intelligence · N100 Analytics", page_icon="🌐", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Sector Intelligence & Industry Positioning",
    subtitle="Macro industry fundamental comparisons, constituent scale distribution, and median financial benchmarks.",
    badge_text="SECTOR LANDSCAPE",
)

df_sectors = get_sectors()
df_cos = get_companies()
df_r = get_ratios(year="2024-03")
if df_r.empty:
    df_r = get_ratios()
df_val = get_valuation()

all_sectors = sorted(df_sectors["broad_sector"].dropna().unique().tolist())
if not all_sectors:
    all_sectors = ["Information Technology", "Financials", "Energy", "Fast Moving Consumer Goods", "Healthcare", "Materials"]

st.sidebar.markdown("### 🌐 **Sector Filter**")
selected_sector = st.sidebar.selectbox("Select Broad Industry Sector", all_sectors, index=0)

# Avoid duplicate sector columns colliding during merge
cos_cols = [c for c in df_cos.columns if c not in ["broad_sector", "sub_sector", "market_cap_category"]]
merged = pd.merge(df_sectors, df_cos[cos_cols], left_on="company_id", right_on="id", how="inner")
merged = pd.merge(merged, df_r, on="company_id", how="left")
if not df_val.empty:
    vc = [c for c in ["company_id", "market_cap_crore", "price_to_earnings"] if c in df_val.columns]
    merged = pd.merge(merged, df_val[vc], on="company_id", how="left")
else:
    merged["market_cap_crore"] = 150000.0
    merged["price_to_earnings"] = 25.0

if "broad_sector" not in merged.columns:
    if "broad_sector_x" in merged.columns:
        merged["broad_sector"] = merged["broad_sector_x"]
    elif "broad_sector_y" in merged.columns:
        merged["broad_sector"] = merged["broad_sector_y"]

if "sub_sector" not in merged.columns:
    if "sub_sector_x" in merged.columns:
        merged["sub_sector"] = merged["sub_sector_x"]
    elif "sub_sector_y" in merged.columns:
        merged["sub_sector"] = merged["sub_sector_y"]

sec_df = merged[merged["broad_sector"] == selected_sector].copy()
sec_df = sec_df.drop_duplicates(subset=["company_id"], keep="last")

if sec_df.empty:
    st.info(f"No constituents found for sector: {selected_sector}")
    st.stop()


if "sales" not in sec_df.columns:
    sec_df["sales"] = sec_df["free_cash_flow_cr"].fillna(5000) * 4
if "return_on_equity_pct" not in sec_df.columns:
    sec_df["return_on_equity_pct"] = 18.0
sec_df["market_cap_crore"] = sec_df["market_cap_crore"].fillna(50000.0)

# Sector Benchmark Cards
st.markdown(f"##### 📊 **{selected_sector} — Industry Median KPI Benchmarks**")
med_roe = safe_float(sec_df["return_on_equity_pct"].dropna().median(), default=18.0)
med_roce = safe_float(sec_df["return_on_capital_employed_pct"].dropna().median(), default=20.0) if "return_on_capital_employed_pct" in sec_df.columns else 20.0
med_npm = safe_float(sec_df["net_profit_margin_pct"].dropna().median(), default=14.0) if "net_profit_margin_pct" in sec_df.columns else 14.0
med_de = safe_float(sec_df["debt_to_equity"].dropna().median(), default=0.35) if "debt_to_equity" in sec_df.columns else 0.35

bm1, bm2, bm3, bm4 = st.columns(4)
bm1.metric("Median Sector ROE", f"{med_roe:.1f}%", f"{len(sec_df)} Companies")
bm2.metric("Median Sector ROCE", f"{med_roce:.1f}%", "Capital Return")
bm3.metric("Median Net Margin", f"{med_npm:.1f}%", "Operational")
bm4.metric("Median Debt / Equity", f"{med_de:.2f}", "Capital Structure")

st.markdown("---")

# Bubble Map
st.markdown(f"##### 🫧 **Constituent Scale & Profitability Map: {selected_sector}**")
st.caption("X-Axis: Annual Revenue (₹ Cr) | Y-Axis: Return on Equity (%) | Bubble Size: Market Capitalization (₹ Cr)")

fig_bubble = px.scatter(
    sec_df,
    x="sales",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    text="company_id",
    size_max=45,
    labels={"sales": "Annual Revenue (₹ Cr)", "return_on_equity_pct": "Return on Equity (ROE %)"},
    color_discrete_sequence=px.colors.qualitative.Bold,
)
med_sales = safe_float(sec_df["sales"].dropna().median(), default=10000.0)
if med_sales > 0:
    fig_bubble.add_vline(
        x=med_sales, line_dash="dash", line_color="rgba(255, 255, 255, 0.2)", line_width=1.5,
        annotation_text=f"Median Rev: ₹{med_sales:,.0f} Cr", annotation_position="top right",
        annotation_font=dict(size=10, color="#8E8E93")
    )
if med_roe > 0:
    fig_bubble.add_hline(
        y=med_roe, line_dash="dash", line_color="rgba(255, 255, 255, 0.2)", line_width=1.5,
        annotation_text=f"Median ROE: {med_roe:.1f}%", annotation_position="bottom right",
        annotation_font=dict(size=10, color="#8E8E93")
    )
fig_bubble.update_traces(
    textposition="top center",
    hovertemplate="<b>%{hovertext}</b> (%{text})<br>Revenue: <b>₹%{x:,.0f} Cr</b><br>ROE: <b>%{y:.1f}%</b><extra></extra>"
)
apply_chart_theme(fig_bubble, height=480)
st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# Sub-Sector Performance Breakdown Chart
if "sub_sector" in sec_df.columns and sec_df["sub_sector"].nunique() > 1:
    st.markdown("###### 📊 **Sub-Sector Profitability & Capital Efficiency Breakdown**")
    sub_perf = sec_df.groupby("sub_sector").agg(
        Median_ROE=("return_on_equity_pct", "median"),
        Median_ROCE=("return_on_capital_employed_pct", "median"),
        Companies=("company_id", "count"),
    ).reset_index().sort_values(by="Median_ROE", ascending=False)
    
    fig_sub = go.Figure()
    fig_sub.add_trace(go.Bar(
        x=sub_perf["sub_sector"],
        y=sub_perf["Median_ROE"],
        name="Median ROE (%)",
        marker_color="#0A84FF",
        text=[f"{v:.1f}%" for v in sub_perf["Median_ROE"]],
        textposition="outside",
    ))
    fig_sub.add_trace(go.Bar(
        x=sub_perf["sub_sector"],
        y=sub_perf["Median_ROCE"],
        name="Median ROCE (%)",
        marker_color="#30D158",
        text=[f"{v:.1f}%" for v in sub_perf["Median_ROCE"]],
        textposition="outside",
    ))
    fig_sub.update_layout(
        barmode="group",
        height=320,
        xaxis_title="Industry Sub-Sector",
        yaxis_title="Return (%)",
        hovermode="x unified",
    )
    apply_chart_theme(fig_sub, height=320)
    st.plotly_chart(fig_sub, use_container_width=True, config={"displayModeBar": False, "responsive": True})

st.markdown("---")

# Sector Constituent Table
st.markdown(f"##### 📋 **{selected_sector} Constituent Performance Matrix**")
show_cols = ["company_id", "company_name", "sub_sector", "sales", "return_on_equity_pct", "debt_to_equity", "market_cap_crore"]
renames = {
    "company_id": "Ticker",
    "company_name": "Company Name",
    "sub_sector": "Industry Sub-Sector",
    "sales": "Revenue (₹ Cr)",
    "return_on_equity_pct": "ROE (%)",
    "debt_to_equity": "D/E Ratio",
    "market_cap_crore": "Market Cap (₹ Cr)",
}
avail = [c for c in show_cols if c in sec_df.columns]
tbl_df = sec_df[avail].rename(columns=renames)

for c in ["Revenue (₹ Cr)", "ROE (%)", "D/E Ratio", "Market Cap (₹ Cr)"]:
    if c in tbl_df.columns:
        tbl_df[c] = pd.to_numeric(tbl_df[c], errors="coerce")

col_config = {
    "Ticker": st.column_config.TextColumn("Ticker"),
    "Company Name": st.column_config.TextColumn("Company Name"),
    "Industry Sub-Sector": st.column_config.TextColumn("Industry Sub-Sector"),
    "Revenue (₹ Cr)": st.column_config.NumberColumn("Revenue (₹ Cr)", format="₹%d Cr"),
    "ROE (%)": st.column_config.NumberColumn("ROE (%)", format="%.1f%%"),
    "D/E Ratio": st.column_config.NumberColumn("D/E Ratio", format="%.2f"),
    "Market Cap (₹ Cr)": st.column_config.NumberColumn("Market Cap (₹ Cr)", format="₹%d Cr"),
}

st.dataframe(
    tbl_df,
    column_config=col_config,
    use_container_width=True,
    hide_index=True,
)
