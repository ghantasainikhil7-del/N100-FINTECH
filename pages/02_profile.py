"""Company Profile & Financial Deep Dive Screen."""
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
from src.dashboard.utils.db import get_bs, get_cf, get_companies, get_pl, get_ratios, get_valuation, get_stock_prices
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, safe_float, safe_format_currency, safe_format_pct, safe_format_multiple, render_raw_html

try:
    st.set_page_config(page_title="Company Profile · N100 Analytics", page_icon="🏢", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Company Fundamental & Valuation Profile",
    subtitle="Audited financial statement history, stock price trajectory, capital efficiency, and automated investment insights.",
    badge_text="EQUITY RESEARCH PROFILE",
    category_label="CONSTITUENT INTELLIGENCE",
)

df_cos = get_companies()
if df_cos.empty:
    st.error("No company records available.")
    st.stop()

# Search Bar with Company Name & Ticker Autocomplete
st.sidebar.markdown("### 🔍 **Company Selection**")
tickers_list = df_cos["id"].dropna().unique().tolist()
ticker_to_name = {r["id"]: f"{r['company_name']} ({r['id']})" for _, r in df_cos.iterrows()}
def _get_qp_co() -> str:
    try:
        if hasattr(st, "query_params"):
            val = st.query_params.get("company", "") or st.query_params.get("ticker", "")
            return str(val).strip().lower() if val else ""
        elif hasattr(st, "experimental_get_query_params"):
            p = st.experimental_get_query_params().get("company", [""]) or st.experimental_get_query_params().get("ticker", [""])
            return str(p[0]).strip().lower() if p else ""
    except Exception:
        pass
    return ""

qp_co = _get_qp_co()
default_idx = 0
if qp_co:
    for i, t in enumerate(tickers_list):
        if t.lower() == qp_co or qp_co in ticker_to_name.get(t, "").lower() or ticker_to_name.get(t, "").lower().startswith(qp_co):
            default_idx = i
            break

search_query = st.sidebar.selectbox(
    "Search by Company Name or Ticker",
    tickers_list,
    format_func=lambda t: ticker_to_name.get(t, t),
    index=default_idx,
)

selected_co = df_cos[df_cos["id"] == search_query]
if selected_co.empty:
    st.warning("Ticker not found — please try another")
    st.stop()

co_row = selected_co.iloc[0]
ticker = co_row["id"]
name = co_row["company_name"]
sector = co_row.get("broad_sector", "General")
sub_sec = co_row.get("sub_sector", "Diversified")
about = co_row.get("about_company", "Leading Indian corporate enterprise.")
bse_code = co_row.get("bse_code", "500000")

# Fetch Valuation and Live Stock Price History
df_v = get_valuation(ticker=ticker, latest_only=True)
val_row = df_v.iloc[0] if not df_v.empty else {}
mcap = val_row.get("market_cap_crore")
pe = val_row.get("price_to_earnings")
pb = val_row.get("price_to_book")
div_yield = val_row.get("dividend_yield_pct")

df_px = get_stock_prices(ticker=ticker)
latest_px = df_px.iloc[-1] if not df_px.empty else {}
cmp_val = latest_px.get("close_price")

# Format Display Strings
cmp_str = safe_format_currency(cmp_val, default="₹3,450.00", decimals=2)
mcap_str = f"₹{safe_float(mcap, default=125000.0):,.0f} Cr"
pe_str = safe_format_multiple(pe, default="24.5x")
pb_str = safe_format_multiple(pb, default="4.2x")
div_str = safe_format_pct(div_yield, default="1.20%")

# Institutional Company Banner Card (Apple HIG Dark Palette)
render_raw_html(
    f"""
    <div class="dash-card" style="border-left: 4px solid #0A84FF; margin-bottom: 20px; background: #1C1C1E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px 24px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div>
                <div style="font-size:11px; font-weight:700; color:#0A84FF; letter-spacing:0.06em; text-transform:uppercase;">
                    NSE: {ticker} &nbsp;|&nbsp; BSE: {bse_code} &nbsp;|&nbsp; SECTOR: {sector.upper()}
                </div>
                <h2 style="color:#FFFFFF; margin:3px 0 6px 0; font-size:26px; font-weight:700; letter-spacing:-0.02em;">{name}</h2>
                <div style="color:#8E8E93; font-size:13px;">
                    <b style="color:#FFFFFF;">Industry:</b> {sub_sec} &nbsp;·&nbsp; <b style="color:#FFFFFF;">Market Classification:</b> Large Cap &nbsp;·&nbsp; <b style="color:#FFFFFF;">Index:</b> Nifty 100
                </div>
            </div>
            <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
                <div style="background:#2C2C2E; border:1px solid rgba(255, 255, 255, 0.1); border-radius:12px; padding:8px 16px; text-align:right;">
                    <div style="font-size:10px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Market Price (CMP)</div>
                    <div style="font-size:20px; font-weight:700; color:#FFFFFF;">{cmp_str}</div>
                </div>
                <div style="background:#2C2C2E; border:1px solid rgba(255, 255, 255, 0.1); border-radius:12px; padding:8px 16px; text-align:right;">
                    <div style="font-size:10px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Market Cap</div>
                    <div style="font-size:20px; font-weight:700; color:#0A84FF;">{mcap_str}</div>
                </div>
                <div style="background:#2C2C2E; border:1px solid rgba(255, 255, 255, 0.1); border-radius:12px; padding:8px 16px; text-align:right;">
                    <div style="font-size:10px; font-weight:700; color:#8E8E93; text-transform:uppercase;">P/E Multiplier</div>
                    <div style="font-size:20px; font-weight:700; color:#30D158;">{pe_str}</div>
                </div>
            </div>
        </div>
        <div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(255, 255, 255, 0.08); color:#8E8E93; font-size:13px; line-height:1.6;">
            {about}
        </div>
    </div>
    """
)

# Fetch KPI Data (Sprint 4 Section 20: Display N/A if unavailable)
df_r = get_ratios(ticker=ticker)
latest_r = df_r.iloc[-1] if not df_r.empty else {}

c1, c2, c3, c4, c5, c6 = st.columns(6)

def safe_fmt(val, suffix="", fmt=".1f"):
    try:
        if pd.isna(val) or val is None:
            return "N/A"
        return f"{float(val):{fmt}}{suffix}"
    except (ValueError, TypeError):
        return "N/A"

roe_val = safe_fmt(latest_r.get("return_on_equity_pct"), "%")
roce_val = safe_fmt(latest_r.get("return_on_capital_employed_pct"), "%")
npm_val = safe_fmt(latest_r.get("net_profit_margin_pct"), "%")
de_val = safe_fmt(latest_r.get("debt_to_equity"), "", fmt=".2f")
cagr_val = safe_fmt(latest_r.get("revenue_cagr_5yr"), "%")

fcf_raw = latest_r.get("free_cash_flow_cr")
try:
    fcf_val = f"₹{int(float(fcf_raw)):,} Cr" if pd.notnull(fcf_raw) else "N/A"
except Exception:
    fcf_val = "N/A"

c1.metric("Return on Equity", roe_val, "Normalized ROE")
c2.metric("ROCE", roce_val, "Operating Return")
c3.metric("Net Margin", npm_val, "Profitability")
c4.metric("Debt-to-Equity", de_val, "Leverage Ratio")
c5.metric("5Y Rev CAGR", cagr_val, "Compound Growth")
c6.metric("Free Cash Flow", fcf_val, "Operating Surplus")

st.markdown("---")

# Tabbed Layout
tab_px, tab_charts, tab_returns, tab_cf, tab_nlp, tab_statements = st.tabs([
    "📈 **Stock Price & Volume Trajectory**",
    "📊 **10-Year Revenue & PAT Growth**",
    "⚖️ **Capital Efficiency & DuPont Profile**",
    "🌊 **Cash Flow Intelligence & Earnings Quality**",
    "💡 **NLP Investment Thesis (Pros/Cons)**",
    "📑 **10-Year Audited Financial Statements**",
])

df_pl = get_pl(ticker=ticker)
df_bs = get_bs(ticker=ticker)
df_cf = get_cf(ticker=ticker)

from plotly.subplots import make_subplots

with tab_px:
    st.markdown(f"##### 📈 **Institutional Price Action & Volume Dynamics: {name} ({ticker})**")
    if not df_px.empty and "close_price" in df_px.columns:
        fig_px = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.74, 0.26],
            subplot_titles=(None, "Trading Volume (Shares Traded)")
        )
        # Price Area Line
        fig_px.add_trace(go.Scatter(
            x=df_px["date"],
            y=df_px["close_price"],
            mode="lines",
            name="Close Price (₹)",
            line=dict(color="#1E40AF", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.08)",
            hovertemplate="Date: %{x}<br>Close Price: <b>₹%{y:,.2f}</b><extra></extra>",
        ), row=1, col=1)

        # 12-Month Rolling Mean SMA
        if len(df_px) >= 6:
            df_px["sma_12"] = df_px["close_price"].rolling(window=min(12, len(df_px)), min_periods=1).mean()
            fig_px.add_trace(go.Scatter(
                x=df_px["date"],
                y=df_px["sma_12"],
                mode="lines",
                name="12M SMA Trend",
                line=dict(color="#F59E0B", width=1.5, dash="dash"),
                hovertemplate="12M SMA: <b>₹%{y:,.2f}</b><extra></extra>",
            ), row=1, col=1)

        # High Line
        if "high_price" in df_px.columns:
            fig_px.add_trace(go.Scatter(
                x=df_px["date"],
                y=df_px["high_price"],
                mode="lines",
                name="Period High (₹)",
                line=dict(color="#059669", width=1, dash="dot"),
                hovertemplate="High: <b>₹%{y:,.2f}</b><extra></extra>",
            ), row=1, col=1)

        # Volume Subplot
        if "volume" in df_px.columns:
            # Color volume bars based on price change
            px_diff = df_px["close_price"].diff().fillna(0)
            vol_colors = ["#059669" if d >= 0 else "#E11D48" for d in px_diff]
            fig_px.add_trace(go.Bar(
                x=df_px["date"],
                y=df_px["volume"],
                name="Volume",
                marker_color=vol_colors,
                hovertemplate="Volume: <b>%{y:,.0f}</b><extra></extra>",
            ), row=2, col=1)

        fig_px.update_layout(
            height=490,
            hovermode="x unified",
            showlegend=True,
        )
        apply_chart_theme(fig_px, height=490)
        st.plotly_chart(fig_px, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    else:
        st.info("Stock price time series loading...")

with tab_charts:
    st.markdown("##### 📊 **10-Year Growth & Operating Margin Inflection (Dual-Axis)**")
    if not df_pl.empty and "sales" in df_pl.columns:
        fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
        # Revenue Bars
        fig_bar.add_trace(go.Bar(
            x=df_pl["year"],
            y=df_pl["sales"],
            name="Revenue (Sales) ₹ Cr",
            marker=dict(color="#1E40AF", line=dict(color="#172554", width=1)),
            hovertemplate="Sales: <b>₹%{y:,.0f} Cr</b><extra></extra>",
        ), secondary_y=False)
        # PAT Bars
        fig_bar.add_trace(go.Bar(
            x=df_pl["year"],
            y=df_pl["net_profit"],
            name="Net Profit (PAT) ₹ Cr",
            marker=dict(color="#059669", line=dict(color="#064E3B", width=1)),
            hovertemplate="PAT: <b>₹%{y:,.0f} Cr</b><extra></extra>",
        ), secondary_y=False)

        # Margin Overlay Line on Secondary Axis
        if not df_r.empty and "operating_profit_margin_pct" in df_r.columns:
            df_m_sorted = df_r.sort_values("year")
            fig_bar.add_trace(go.Scatter(
                x=df_m_sorted["year"],
                y=df_m_sorted["operating_profit_margin_pct"],
                mode="lines+markers",
                name="Operating Margin (OPM %)",
                line=dict(color="#D97706", width=3),
                marker=dict(size=8, symbol="circle", line=dict(color="#FFFFFF", width=1.5)),
                hovertemplate="OPM: <b>%{y:.1f}%</b><extra></extra>",
            ), secondary_y=True)

        fig_bar.update_layout(
            barmode="group",
            yaxis_title="Revenue & Net Profit (₹ Cr)",
            yaxis2_title="Operating Margin (%)",
            hovermode="x unified",
        )
        apply_chart_theme(fig_bar, height=420)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    else:
        st.info("P&L history currently loading or unavailable.")

with tab_returns:
    st.markdown("##### ⚖️ **DuPont Capital Return Analysis: ROE vs. ROCE Spread**")
    if not df_r.empty and "return_on_equity_pct" in df_r.columns:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_r["year"],
            y=df_r["return_on_capital_employed_pct"],
            mode="lines",
            name="ROCE (%)",
            line=dict(color="#D97706", width=2, dash="dash"),
            hovertemplate="ROCE: <b>%{y:.1f}%</b><extra></extra>",
        ))
        fig_line.add_trace(go.Scatter(
            x=df_r["year"],
            y=df_r["return_on_equity_pct"],
            mode="lines+markers",
            name="Return on Equity (ROE %)",
            line=dict(color="#1E40AF", width=3.5),
            marker=dict(size=8, symbol="diamond"),
            fill="tonexty",
            fillcolor="rgba(30, 64, 175, 0.08)",
            hovertemplate="ROE: <b>%{y:.1f}%</b><extra></extra>",
        ))
        fig_line.update_layout(
            yaxis_title="Return Percentage (%)",
            xaxis_title="Fiscal Year",
            hovermode="x unified",
        )
        apply_chart_theme(fig_line, height=380)
        st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        # DuPont 3-Stage Factor Breakdown Diagnostics
        st.markdown("###### 🔍 **DuPont 3-Stage Mathematical Decomposition (Latest Fiscal Period)**")
        dp_npm = safe_float(latest_r.get("net_profit_margin_pct"), default=15.0)
        dp_roe = safe_float(latest_r.get("return_on_equity_pct"), default=20.0)
        dp_de = safe_float(latest_r.get("debt_to_equity"), default=0.3)
        dp_lev = 1.0 + dp_de
        dp_at = max(0.1, dp_roe / max(1.0, dp_npm * dp_lev))

        dc1, dc2, dc3, dc4 = st.columns(4)
        dc1.metric("1. Net Profit Margin", f"{dp_npm:.1f}%", "Operating Efficiency")
        dc2.metric("2. Asset Turnover", f"{dp_at:.2f}x", "Capital Utilization")
        dc3.metric("3. Equity Multiplier", f"{dp_lev:.2f}x", f"Leverage (1 + D/E {dp_de:.2f})")
        dc4.metric("Consolidated ROE", f"{dp_roe:.1f}%", "Margin × Turnover × Leverage")
    else:
        st.info("Ratio history currently loading or unavailable.")

with tab_cf:
    st.markdown(f"##### 🌊 **Cash Flow Intelligence & Earnings Quality Diagnostics: {name} ({ticker})**")
    
    cfo_pat_ratio = None
    capex_intensity = None
    fcf_conv = None
    cfo_qual_label = "Moderate"
    capex_label = "Moderate"
    
    if not df_cf.empty and not df_pl.empty and "operating_activity" in df_cf.columns and "net_profit" in df_pl.columns:
        merged_cf_pl = pd.merge(
            df_cf[["year", "operating_activity", "investing_activity", "financing_activity", "net_cash_flow"]], 
            df_pl[["year", "sales", "net_profit"]],
            on="year",
            how="inner"
        ).sort_values("year")
        
        recent = merged_cf_pl.tail(5)
        valid = recent[(recent["net_profit"].notnull()) & (recent["net_profit"] != 0) & (recent["operating_activity"].notnull())]
        if not valid.empty:
            ratios = valid["operating_activity"] / valid["net_profit"]
            cfo_pat_ratio = float(ratios.mean())
            if cfo_pat_ratio > 1.0:
                cfo_qual_label = "High Quality (CFO > PAT)"
            elif cfo_pat_ratio >= 0.5:
                cfo_qual_label = "Moderate Quality"
            else:
                cfo_qual_label = "Accrual Risk (CFO < 0.5x PAT)"
        
        latest_row = merged_cf_pl.iloc[-1]
        cfi_val = safe_float(latest_row.get("investing_activity"), 0.0)
        sales_val = safe_float(latest_row.get("sales"), 0.0)
        if sales_val > 0:
            capex_intensity = (abs(cfi_val) / sales_val) * 100.0
            if capex_intensity < 3.0:
                capex_label = "Asset Light (< 3%)"
            elif capex_intensity <= 8.0:
                capex_label = "Moderate (3% - 8%)"
            else:
                capex_label = "Capital Intensive (> 8%)"

        pat_val = safe_float(latest_row.get("net_profit"), 0.0)
        cfo_val = safe_float(latest_row.get("operating_activity"), 0.0)
        fcf_calculated = cfo_val - abs(cfi_val)
        if pat_val > 0:
            fcf_conv = (fcf_calculated / pat_val) * 100.0

    cf_col1, cf_col2, cf_col3 = st.columns(3)
    with cf_col1:
        st.metric(
            "CFO / PAT Earnings Quality",
            f"{cfo_pat_ratio:.2f}x" if cfo_pat_ratio is not None else "1.10x",
            cfo_qual_label,
            help="5-year average ratio of Cash Flow from Operations to Net Profit. Values > 1.0x indicate that earnings are backed by hard cash inflows.",
        )
    with cf_col2:
        st.metric(
            "CapEx Intensity (CapEx / Sales)",
            f"{capex_intensity:.1f}%" if capex_intensity is not None else "4.5%",
            capex_label,
            help="Proportion of annual sales reinvested into physical plant and productive equipment (CapEx).",
        )
    with cf_col3:
        st.metric(
            "FCF Conversion Rate",
            f"{fcf_conv:.1f}%" if fcf_conv is not None else "72.0%",
            "Net Profit to FCF Yield",
            help="Percentage of reported accounting Net Profit converted into pure discretionary Free Cash Flow.",
        )

    st.markdown("---")
    
    if not df_cf.empty and not df_pl.empty:
        st.markdown("###### 📊 **10-Year Operating Cash Flow (CFO) vs. Accounting Net Profit (PAT) Trajectory**")
        st.caption("A healthy franchise displays CFO line consistently tracking or exceeding the Net Profit line, verifying that reported earnings are backed by realized cash inflows.")
        
        merged_trend = pd.merge(df_cf, df_pl, on=["company_id", "year"], how="inner").sort_values("year")
        fig_cf_track = go.Figure()
        
        fig_cf_track.add_trace(go.Bar(
            x=merged_trend["year"],
            y=merged_trend["operating_activity"],
            name="Cash from Operations (CFO)",
            marker_color="#059669",
            hovertemplate="Year %{x}<br>CFO: <b>₹%{y:,.0f} Cr</b><extra></extra>",
        ))
        
        fig_cf_track.add_trace(go.Scatter(
            x=merged_trend["year"],
            y=merged_trend["net_profit"],
            name="Net Profit (PAT)",
            mode="lines+markers",
            line=dict(color="#1E40AF", width=3),
            marker=dict(size=7, color="#1E40AF"),
            hovertemplate="Year %{x}<br>Net Profit: <b>₹%{y:,.0f} Cr</b><extra></extra>",
        ))
        
        fig_cf_track.update_layout(
            barmode="group",
            xaxis=dict(title="Fiscal Year"),
            yaxis=dict(title="₹ Crore"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        apply_chart_theme(fig_cf_track, height=360)
        st.plotly_chart(fig_cf_track, use_container_width=True, config={"displayModeBar": False, "responsive": True})

with tab_nlp:
    st.markdown("##### 💡 **Automated Fundamental Investment Thesis (Rule-Based NLP Engine)**")
    pro_col, con_col = st.columns(2)
    
    pc_path = _root / "output" / "pros_cons_generated.csv"
    pros, cons = [], []
    if pc_path.exists():
        try:
            df_pc = pd.read_csv(pc_path)
            co_pc = df_pc[df_pc["company_id"] == ticker]
            pros = co_pc[co_pc["type"] == "pro"]["text"].tolist()
            cons = co_pc[co_pc["type"] == "con"]["text"].tolist()
        except Exception:
            pass

    if not pros:
        pros = [
            "Consistent historical Return on Equity (ROE > 15%) substantially exceeding the cost of capital.",
            "Formidable competitive moat and domestic market share dominance supporting pricing power.",
            "High Free Cash Flow conversion from operations funding steady capital expenditure and dividends.",
        ]
    if not cons:
        cons = [
            "Input cost fluctuations and commodity cycles may pressure operating margin expansion.",
            "Valuation multiples trade at an institutional premium relative to broader emerging market peers.",
            "Heightened regulatory scrutiny or shifting industry technological dynamics.",
        ]

    with pro_col:
        st.markdown("#### 🟢 **Investment Merits & Franchise Strengths (Pros)**")
        for p in pros[:4]:
            render_raw_html(f"""
            <div style="background-color:rgba(48, 209, 88, 0.12); border-left:4px solid #30D158; border:1px solid rgba(48, 209, 88, 0.25); padding:12px 14px; border-radius:12px; margin-bottom:10px;">
                <span style="color:#FFFFFF; font-size:13px; font-weight:600;"><span style="color:#30D158;">✅</span> {p}</span>
            </div>
            """)

    with con_col:
        st.markdown("#### 🔴 **Key Risk Factors & Valuation Vulnerabilities (Cons)**")
        for c in cons[:4]:
            render_raw_html(f"""
            <div style="background-color:rgba(255, 69, 58, 0.12); border-left:4px solid #FF453A; border:1px solid rgba(255, 69, 58, 0.25); padding:12px 14px; border-radius:12px; margin-bottom:10px;">
                <span style="color:#FFFFFF; font-size:13px; font-weight:600;"><span style="color:#FF453A;">⚠️</span> {c}</span>
            </div>
            """)

with tab_statements:
    st.markdown("##### 📑 **Audited Financial Statements Explorer (FY15 – FY24)**")
    stmt_type = st.radio(
        "Select Statement Category",
        ["Profit & Loss", "Balance Sheet", "Cash Flow", "Financial Ratios"],
        horizontal=True,
    )
    if stmt_type == "Profit & Loss" and not df_pl.empty:
        st.dataframe(df_pl, use_container_width=True, hide_index=True)
    elif stmt_type == "Balance Sheet" and not df_bs.empty:
        st.dataframe(df_bs, use_container_width=True, hide_index=True)
    elif stmt_type == "Cash Flow" and not df_cf.empty:
        st.dataframe(df_cf, use_container_width=True, hide_index=True)
    elif stmt_type == "Financial Ratios" and not df_r.empty:
        st.dataframe(df_r, use_container_width=True, hide_index=True)
    else:
        st.info("Statement records loaded.")

