"""Interactive Investment Screener Screen with 10 Sliders and 6 Presets."""
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
from src.dashboard.utils.db import get_companies, get_ratios, get_valuation
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, render_raw_html

try:
    st.set_page_config(page_title="Investment Screener · N100 Analytics", page_icon="🔍", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Institutional Investment Screener",
    subtitle="Filter 92 constituents dynamically across 10 fundamental ratios with sector-aware carve-outs and pre-built investment themes.",
    badge_text="EQUITY SCREENER",
)

# Preset definitions
presets = {
    "Quality Compounder": {"roe": 15.0, "de": 1.0, "fcf": 0.0, "rev_cagr": 10.0, "pat_cagr": 10.0, "opm": 15.0, "pe": 40.0, "pb": 8.0, "div": 0.5, "icr": 3.0},
    "Value Opportunity": {"roe": 10.0, "de": 2.0, "fcf": 0.0, "rev_cagr": 5.0, "pat_cagr": 5.0, "opm": 10.0, "pe": 20.0, "pb": 3.0, "div": 1.0, "icr": 2.0},
    "Growth Accelerator": {"roe": 18.0, "de": 2.0, "fcf": 0.0, "rev_cagr": 15.0, "pat_cagr": 20.0, "opm": 15.0, "pe": 50.0, "pb": 10.0, "div": 0.0, "icr": 2.5},
    "Dividend Champion": {"roe": 12.0, "de": 1.5, "fcf": 0.0, "rev_cagr": 5.0, "pat_cagr": 5.0, "opm": 12.0, "pe": 30.0, "pb": 5.0, "div": 2.0, "icr": 3.0},
    "Debt-Free Bluechip": {"roe": 12.0, "de": 0.0, "fcf": 0.0, "rev_cagr": 8.0, "pat_cagr": 8.0, "opm": 12.0, "pe": 45.0, "pb": 8.0, "div": 0.5, "icr": 10.0},
    "Turnaround Watch": {"roe": 8.0, "de": 2.5, "fcf": 100.0, "rev_cagr": 10.0, "pat_cagr": 12.0, "opm": 8.0, "pe": 35.0, "pb": 4.0, "div": 0.0, "icr": 1.5},
}

for k in ["roe", "de", "fcf", "rev_cagr", "pat_cagr", "opm", "pe", "pb", "div", "icr"]:
    if k not in st.session_state:
        st.session_state[k] = presets["Quality Compounder"][k]

# Presets Quick-Filter Bar
st.markdown("##### ⚡ **One-Click Institutional Filter Presets**")
preset_cols = st.columns(6)
for idx, (pname, pvals) in enumerate(presets.items()):
    if preset_cols[idx].button(f"🎯 {pname}", use_container_width=True):
        for k, v in pvals.items():
            st.session_state[k] = v
        st.rerun()

st.markdown("---")

# Sliders in Sidebar organized by category
st.sidebar.markdown("### 🎛️ **Ratio Filter Sliders**")

with st.sidebar.expander("📈 **1. Profitability & Returns**", expanded=True):
    roe_min = st.slider("Min ROE (%)", 0.0, 50.0, float(st.session_state["roe"]), 1.0)
    opm_min = st.slider("Min OPM (%)", 0.0, 50.0, float(st.session_state["opm"]), 1.0)

with st.sidebar.expander("💸 **2. Leverage & Solvency**", expanded=True):
    de_max = st.slider("Max Debt-to-Equity", 0.0, 5.0, float(st.session_state["de"]), 0.1)
    icr_min = st.slider("Min Interest Coverage (ICR)", 0.0, 25.0, float(st.session_state["icr"]), 0.5)

with st.sidebar.expander("🚀 **3. Cash Flow & 5Y Growth**", expanded=True):
    fcf_min = st.slider("Min FCF (₹ Cr)", -1000.0, 10000.0, float(st.session_state["fcf"]), 500.0)
    rev_cagr_min = st.slider("Min 5Y Rev CAGR (%)", 0.0, 40.0, float(st.session_state["rev_cagr"]), 1.0)
    pat_cagr_min = st.slider("Min 5Y PAT CAGR (%)", 0.0, 40.0, float(st.session_state["pat_cagr"]), 1.0)

with st.sidebar.expander("🏷️ **4. Valuation & Dividends**", expanded=True):
    pe_max = st.slider("Max P/E Multiple", 5.0, 120.0, float(st.session_state["pe"]), 5.0)
    pb_max = st.slider("Max P/B Multiple", 1.0, 20.0, float(st.session_state["pb"]), 0.5)
    div_min = st.slider("Min Dividend Yield (%)", 0.0, 6.0, float(st.session_state["div"]), 0.2)

df_cos = get_companies()
all_sectors_list = sorted([str(s) for s in df_cos["broad_sector"].dropna().unique()]) if not df_cos.empty else []

with st.sidebar.expander("🌐 **5. Sector Universe Focus**", expanded=False):
    selected_sectors = st.multiselect(
        "Filter by Broad Sector",
        all_sectors_list,
        default=all_sectors_list,
        help="Select one or multiple industry sectors to focus your investment screening.",
    )

# Preserve slider values
st.session_state.update({
    "roe": roe_min, "opm": opm_min, "de": de_max, "icr": icr_min,
    "fcf": fcf_min, "rev_cagr": rev_cagr_min, "pat_cagr": pat_cagr_min,
    "pe": pe_max, "pb": pb_max, "div": div_min
})

# Load and Filter Data
df_ratios = get_ratios(latest_only=True)
if df_ratios.empty:
    df_ratios = get_ratios()
if not df_ratios.empty and "year" in df_ratios.columns:
    df_ratios = df_ratios.sort_values("year").groupby("company_id", as_index=False).last()

df_val = get_valuation(latest_only=True)

df_m = pd.merge(df_cos, df_ratios, left_on="id", right_on="company_id", how="inner")
if not df_val.empty:
    val_cols = ["company_id", "price_to_earnings", "price_to_book", "dividend_yield_pct"]
    avail_vc = [c for c in val_cols if c in df_val.columns]
    df_m = pd.merge(df_m, df_val[avail_vc], on="company_id", how="left")
else:
    df_m["price_to_earnings"] = 25.0
    df_m["price_to_book"] = 4.0
    df_m["dividend_yield_pct"] = 1.2

df_m = df_m.drop_duplicates(subset=["id"], keep="last")

# Apply Threshold Filtering
filtered = df_m.copy()

if selected_sectors:
    filtered = filtered[filtered["broad_sector"].isin(selected_sectors)]

if "return_on_equity_pct" in filtered.columns:
    filtered = filtered[filtered["return_on_equity_pct"].fillna(0) >= roe_min]

if "debt_to_equity" in filtered.columns:
    is_fin = filtered["broad_sector"].astype(str).str.contains("Financial|Bank", case=False, na=False)
    filtered = filtered[(filtered["debt_to_equity"].fillna(0) <= de_max) | is_fin]

if "free_cash_flow_cr" in filtered.columns:
    filtered = filtered[filtered["free_cash_flow_cr"].fillna(0) >= fcf_min]

if "revenue_cagr_5yr" in filtered.columns:
    filtered = filtered[filtered["revenue_cagr_5yr"].fillna(0) >= rev_cagr_min]

if "pat_cagr_5yr" in filtered.columns:
    filtered = filtered[filtered["pat_cagr_5yr"].fillna(0) >= pat_cagr_min]

if "operating_profit_margin_pct" in filtered.columns:
    filtered = filtered[filtered["operating_profit_margin_pct"].fillna(0) >= opm_min]

if "price_to_earnings" in filtered.columns:
    filtered = filtered[filtered["price_to_earnings"].fillna(999) <= pe_max]

if "price_to_book" in filtered.columns:
    filtered = filtered[filtered["price_to_book"].fillna(999) <= pb_max]

if "dividend_yield_pct" in filtered.columns:
    filtered = filtered[filtered["dividend_yield_pct"].fillna(0) >= div_min]

if "interest_coverage" in filtered.columns:
    is_debt_free = filtered.get("icr_label", "") == "Debt Free"
    filtered = filtered[(filtered["interest_coverage"].fillna(0) >= icr_min) | is_debt_free]

match_count = len(filtered)
total_count = len(df_cos) if not df_cos.empty else 92
match_pct = (match_count / max(1, total_count)) * 100

render_raw_html(
    f"""
    <div class="dash-card" style="margin-bottom: 18px; padding: 16px 22px; border-left: 4px solid #30D158; display: flex; justify-content: space-between; align-items: center; background: #1C1C1E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;">
        <div>
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                <span class="pulse-dot"></span>
                <span>Active Screener Filter Match</span>
            </div>
            <div style="font-size: 12.5px; color: #8E8E93; margin-top: 2px;">
                Filtered down from <b style="color: #FFFFFF;">{total_count}</b> audited index members based on institutional risk & profitability hurdles
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="badge badge-green" style="font-size: 12px; padding: 6px 14px; background: rgba(48, 209, 88, 0.16); color: #30D158; border: 1px solid rgba(48, 209, 88, 0.3);">
                ✓ {match_count} of {total_count} Matches ({match_pct:.1f}%)
            </span>
        </div>
    </div>
    """
)

if not filtered.empty:
    m1, m2, m3, m4 = st.columns(4)
    med_roe = float(filtered["return_on_equity_pct"].dropna().median()) if "return_on_equity_pct" in filtered.columns and not filtered["return_on_equity_pct"].dropna().empty else 0.0
    med_pe = float(filtered["price_to_earnings"].dropna().median()) if "price_to_earnings" in filtered.columns and not filtered["price_to_earnings"].dropna().empty else 0.0
    tot_fcf = float(filtered["free_cash_flow_cr"].dropna().sum()) if "free_cash_flow_cr" in filtered.columns else 0.0
    tot_mcap = float(filtered["market_cap_crore"].dropna().sum()) if "market_cap_crore" in filtered.columns else 0.0

    m1.metric("Screened Median ROE", f"{med_roe:.1f}%", "Capital Productivity")
    m2.metric("Screened Median P/E", f"{med_pe:.1f}x", "Cohort Valuation Multiple")
    m3.metric("Aggregate FCF", f"₹{tot_fcf:,.0f} Cr", "Discretionary Cash Flow")
    m4.metric("Aggregate Market Cap", f"₹{tot_mcap:,.0f} Cr", "Screened Universe Scale")
    st.markdown("---")

# Innovative 2D Valuation vs. Quality Opportunity Map
if not filtered.empty and "price_to_earnings" in filtered.columns and "return_on_equity_pct" in filtered.columns:
    st.markdown("##### 🗺️ **2D Valuation vs. Quality Matrix (Constituent Opportunity Map)**")
    plot_df = filtered.copy()
    plot_df["display_pe"] = plot_df["price_to_earnings"].clip(lower=0, upper=85)
    plot_df["display_roe"] = plot_df["return_on_equity_pct"].clip(lower=0, upper=60)
    plot_df["fcf_size"] = plot_df["free_cash_flow_cr"].fillna(1000).clip(lower=100)

    fig_map = px.scatter(
        plot_df,
        x="display_pe",
        y="display_roe",
        size="fcf_size",
        color="broad_sector",
        hover_name="company_name",
        text="company_id",
        size_max=32,
        labels={"display_pe": "P/E Multiple (x)", "display_roe": "Return on Equity (ROE %)", "broad_sector": "Sector"},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    # Add Sweet Spot Reference Box
    fig_map.add_hrect(
        y0=15, y1=60, x0=0, x1=35,
        fillcolor="rgba(48, 209, 88, 0.08)",
        line_width=1, line_color="#30D158", line_dash="dash",
        annotation_text="🎯 Institutional Sweet Spot (ROE > 15%, P/E < 35x)",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#30D158", family="-apple-system, BlinkMacSystemFont, sans-serif"),
    )
    fig_map.update_traces(
        textposition="top center",
        hovertemplate="<b>%{hovertext}</b> (%{text})<br>P/E: <b>%{x:.1f}x</b><br>ROE: <b>%{y:.1f}%</b><extra></extra>",
    )
    fig_map.update_layout(
        xaxis=dict(title="Price-to-Earnings Ratio (P/E Multiple)", range=[0, 90]),
        yaxis=dict(title="Return on Equity (ROE %)", range=[0, 65]),
    )
    apply_chart_theme(fig_map, height=440)
    st.plotly_chart(fig_map, use_container_width=True)

cols_show = [
    "company_id", "company_name", "broad_sector", "return_on_equity_pct",
    "debt_to_equity", "free_cash_flow_cr", "revenue_cagr_5yr",
    "price_to_earnings", "price_to_book", "composite_quality_score"
]
renames = {
    "company_id": "Ticker",
    "company_name": "Company Name",
    "broad_sector": "Sector",
    "return_on_equity_pct": "ROE (%)",
    "debt_to_equity": "D/E",
    "free_cash_flow_cr": "FCF (₹ Cr)",
    "revenue_cagr_5yr": "5Y Rev CAGR (%)",
    "price_to_earnings": "P/E",
    "price_to_book": "P/B",
    "composite_quality_score": "Score",
}

available_cols = [c for c in cols_show if c in filtered.columns]
display_df = filtered[available_cols].rename(columns=renames)

for c in ["ROE (%)", "D/E", "FCF (₹ Cr)", "5Y Rev CAGR (%)", "P/E", "P/B", "Score"]:
    if c in display_df.columns:
        display_df[c] = pd.to_numeric(display_df[c], errors="coerce")

col_config = {
    "Ticker": st.column_config.TextColumn("Ticker", help="NSE / BSE Ticker Symbol"),
    "Company Name": st.column_config.TextColumn("Company Name", help="Constituent Name"),
    "Sector": st.column_config.TextColumn("Sector"),
    "ROE (%)": st.column_config.NumberColumn("ROE", format="%.1f%%", help="Return on Equity"),
    "D/E": st.column_config.NumberColumn("D/E", format="%.2f", help="Debt to Equity Ratio"),
    "FCF (₹ Cr)": st.column_config.NumberColumn("FCF (₹ Cr)", format="₹%d Cr", help="Free Cash Flow in ₹ Crore"),
    "5Y Rev CAGR (%)": st.column_config.NumberColumn("5Y Rev CAGR", format="%.1f%%", help="5-Year Revenue CAGR"),
    "P/E": st.column_config.NumberColumn("P/E", format="%.1fx", help="Price to Earnings Multiple"),
    "P/B": st.column_config.NumberColumn("P/B", format="%.2fx", help="Price to Book Multiple"),
    "Score": st.column_config.ProgressColumn(
        "Quality Score",
        help="Bluestock Multi-Factor Composite Quality Score (0-100)",
        format="%.1f",
        min_value=0,
        max_value=100,
    ),
}

st.dataframe(
    display_df,
    column_config=col_config,
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

col_dl, col_space = st.columns([1, 3])
with col_dl:
    csv_data = filtered[available_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download Screener Results (.CSV)",
        data=csv_data,
        file_name="n100_screener_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
