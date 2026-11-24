"""Peer Comparison Screen with Interactive Radar Charts and Benchmarks."""
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
import plotly.graph_objects as go
import streamlit as st
from src.dashboard.utils.db import get_companies, get_peers, get_ratios
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, safe_float, render_raw_html

try:
    st.set_page_config(page_title="Peer Comparison · N100 Analytics", page_icon="📊", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Peer Comparison & Competitive Benchmarking",
    subtitle="Evaluate relative fundamental strength across 11 designated industry peer groups using 8-axis polar radar charts.",
    badge_text="PEER BENCHMARK",
)

tab_cohort, tab_duel = st.tabs([
    "🎯 **Designated Industry Cohort Radar & Matrix**",
    "⚔️ **Head-to-Head Company Duel (Any 2 Constituents)**",
])

with tab_cohort:
    peer_groups = [
        "IT Services", "Private Banks", "FMCG", "Pharmaceuticals", "Automobiles",
        "Oil & Gas", "Power & Utilities", "Steel & Metals", "Life Insurance",
        "Public Banks", "Consumer Finance"
    ]

    c_grp, c_co = st.columns(2)
    with c_grp:
        selected_group = st.selectbox("Select Target Peer Group", peer_groups, index=0)

    df_p = get_peers(group_name=selected_group)
    df_cos = get_companies()
    df_r = get_ratios(latest_only=True)
    if df_r.empty:
        df_r = get_ratios()
    if not df_r.empty and "year" in df_r.columns:
        df_r = df_r.sort_values("year").groupby("company_id", as_index=False).last()

    merged = pd.merge(df_p, df_cos, left_on="company_id", right_on="id", how="inner")
    merged = pd.merge(merged, df_r, on="company_id", how="left")
    merged = merged.drop_duplicates(subset=["company_id"], keep="last")

    if merged.empty:
        st.info(f"No active constituents found for peer group {selected_group}.")
        st.stop()

    co_options = merged["company_id"].tolist()
    ticker_names = {r["id"]: r["company_name"] for _, r in df_cos.iterrows()}
    with c_co:
        selected_co = st.selectbox(
            "Select Target Constituent to Benchmark",
            co_options,
            format_func=lambda t: f"{ticker_names.get(t, t)} ({t})",
            index=0,
        )

    st.markdown("---")

    # Radar Chart computation
    categories = ["ROE", "ROCE", "Net Margin", "Solvency (1/DE)", "FCF Quality", "PAT 5Y CAGR", "Rev 5Y CAGR", "Quality Score"]

    def normalize_val(val, min_v, max_v):
        if pd.isna(val):
            return 50.0
        return max(10.0, min(100.0, ((val - min_v) / (max_v - min_v + 1e-6)) * 100.0))

    co_row = merged[merged["company_id"] == selected_co].iloc[0]

    co_metrics = [
        normalize_val(co_row.get("return_on_equity_pct", 20), 0, 50),
        normalize_val(co_row.get("return_on_capital_employed_pct", 25), 0, 60),
        normalize_val(co_row.get("net_profit_margin_pct", 15), 0, 40),
        normalize_val(1.0 / (co_row.get("debt_to_equity", 0.5) + 0.1), 0.2, 10),
        normalize_val(co_row.get("free_cash_flow_cr", 5000), 0, 50000),
        normalize_val(co_row.get("pat_cagr_5yr", 12), -10, 40),
        normalize_val(co_row.get("revenue_cagr_5yr", 12), -10, 40),
        normalize_val(co_row.get("composite_quality_score", 70), 30, 100),
    ]

    group_avg_metrics = [
        normalize_val(merged["return_on_equity_pct"].mean(), 0, 50),
        normalize_val(merged["return_on_capital_employed_pct"].mean(), 0, 60),
        normalize_val(merged["net_profit_margin_pct"].mean(), 0, 40),
        normalize_val((1.0 / (merged["debt_to_equity"] + 0.1)).mean(), 0.2, 10),
        normalize_val(merged["free_cash_flow_cr"].mean(), 0, 50000),
        normalize_val(merged["pat_cagr_5yr"].mean(), -10, 40),
        normalize_val(merged["revenue_cagr_5yr"].mean(), -10, 40),
        normalize_val(merged["composite_quality_score"].mean(), 30, 100),
    ]

    col_radar, col_meta = st.columns([1.4, 1])

    with col_radar:
        # Identify Benchmark constituent if available
        if "status" in merged.columns:
            bm_row = merged[merged["status"] == "Benchmark"]
        elif "is_benchmark" in merged.columns:
            bm_row = merged[merged["is_benchmark"] == 1]
        else:
            bm_row = pd.DataFrame()

        bm_metrics = []
        bm_name = "Industry Benchmark"
        if not bm_row.empty:
            bm_single = bm_row.iloc[0]
            bm_name = bm_single.get("company_id", "Benchmark")
            bm_metrics = [
                normalize_val(bm_single.get("return_on_equity_pct", 20), 0, 50),
                normalize_val(bm_single.get("return_on_capital_employed_pct", 25), 0, 60),
                normalize_val(bm_single.get("net_profit_margin_pct", 15), 0, 40),
                normalize_val(1.0 / (bm_single.get("debt_to_equity", 0.5) + 0.1), 0.2, 10),
                normalize_val(bm_single.get("free_cash_flow_cr", 5000), 0, 50000),
                normalize_val(bm_single.get("pat_cagr_5yr", 12), -10, 40),
                normalize_val(bm_single.get("revenue_cagr_5yr", 12), -10, 40),
                normalize_val(bm_single.get("composite_quality_score", 70), 30, 100),
            ]

        st.markdown(f"##### 🎯 **8-Axis Polar Radar: {selected_co} Benchmarking**")
        fig_radar = go.Figure()
        # Target Constituent
        fig_radar.add_trace(go.Scatterpolar(
            r=co_metrics + [co_metrics[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=f"🎯 {selected_co} (Target)",
            fillcolor="rgba(37, 99, 235, 0.35)",
            line=dict(color="#2563EB", width=3),
            hovertemplate="<b>%{theta}</b>: %{r:.1f} / 100<extra></extra>",
        ))
        # Peer Average
        fig_radar.add_trace(go.Scatterpolar(
            r=group_avg_metrics + [group_avg_metrics[0]],
            theta=categories + [categories[0]],
            fill="none",
            name=f"🌐 {selected_group} Avg",
            line=dict(color="#7C3AED", width=2, dash="dash"),
            hovertemplate="<b>Peer Avg %{theta}</b>: %{r:.1f} / 100<extra></extra>",
        ))
        # Benchmark Leader
        if bm_metrics:
            fig_radar.add_trace(go.Scatterpolar(
                r=bm_metrics + [bm_metrics[0]],
                theta=categories + [categories[0]],
                fill="none",
                name=f"⭐ Benchmark ({bm_name})",
                line=dict(color="#D97706", width=2.5, dash="dot"),
                hovertemplate="<b>Benchmark %{theta}</b>: %{r:.1f} / 100<extra></extra>",
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color="#8E8E93"), gridcolor="#2C2C2E"),
                angularaxis=dict(tickfont=dict(size=11, color="#FFFFFF", family="-apple-system, BlinkMacSystemFont, sans-serif"), gridcolor="#2C2C2E"),
            ),
            showlegend=True,
            height=470,
            margin=dict(t=30, b=30, l=40, r=40),
        )
        apply_chart_theme(fig_radar, height=470)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with col_meta:
        st.markdown("##### 📌 **Relative Fundamental Diagnostics**")
        target_score = safe_float(co_row.get("composite_quality_score"), default=0.0)
        avg_score = safe_float(merged["composite_quality_score"].dropna().mean(), default=0.0)
        diff = target_score - avg_score
        
        render_raw_html(f"""
        <div class="dash-card" style="margin-bottom:12px; background: #1C1C1E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 14px 18px;">
            <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Composite Score Spread</div>
            <div style="font-size:26px; font-weight:700; color:#FFFFFF;">{target_score:.1f} / 100</div>
            <div style="font-size:12px; color:{'#30D158' if diff >= 0 else '#FF453A'}; font-weight:700; margin-top:4px;">
                {diff:+.1f} points vs. {selected_group} Peer Average ({avg_score:.1f})
            </div>
        </div>
        """)
        
        # Innovative KPI Spread Divergence Chart
        st.markdown("###### 📊 **Spread vs. Peer Average (+ Outperform / - Lag)**")
        spreads = [co_m - avg_m for co_m, avg_m in zip(co_metrics, group_avg_metrics)]
        fig_spread = go.Figure(go.Bar(
            y=categories,
            x=spreads,
            orientation="h",
            marker_color=["#30D158" if s >= 0 else "#FF453A" for s in spreads],
            text=[f"{s:+.1f}" for s in spreads],
            textposition="inside",
            hovertemplate="<b>%{y}</b><br>Spread vs Peer Avg: <b>%{x:+.1f} pts</b><extra></extra>",
        ))
        fig_spread.update_layout(
            height=260,
            margin=dict(t=10, b=20, l=10, r=10),
            xaxis=dict(title="Delta Points vs Peer Mean", zeroline=True, zerolinecolor="rgba(255, 255, 255, 0.15)", zerolinewidth=1.5),
        )
        apply_chart_theme(fig_spread, height=260)
        st.plotly_chart(fig_spread, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        if not bm_row.empty:
            bm = bm_row.iloc[0]
            st.info(f"⭐ **{bm.get('company_name', bm.get('company_id', 'Leader'))} ({bm.get('company_id', '')})** serves as the anchor benchmark for {selected_group}.")
        else:
            top_bm = merged.sort_values(by="composite_quality_score", ascending=False).iloc[0]
            st.info(f"⭐ **{top_bm.get('company_name', top_bm.get('company_id'))} ({top_bm.get('company_id')})** serves as the highest-scoring peer constituent for {selected_group}.")

    st.markdown("---")

    # Ensure status column is populated for the table
    if "status" not in merged.columns:
        if "is_benchmark" in merged.columns:
            merged["status"] = merged["is_benchmark"].apply(lambda x: "Benchmark" if x == 1 else "Member")
        else:
            merged["status"] = "Member"

    st.markdown(f"##### 📋 **{selected_group} Constituent KPI Matrix**")
    table_cols = [
        "company_id", "company_name", "status", "return_on_equity_pct",
        "return_on_capital_employed_pct", "debt_to_equity", "free_cash_flow_cr",

        "revenue_cagr_5yr", "composite_quality_score"
    ]
    renames = {
        "company_id": "Ticker",
        "company_name": "Company Name",
        "status": "Role",
        "return_on_equity_pct": "ROE (%)",
        "return_on_capital_employed_pct": "ROCE (%)",
        "debt_to_equity": "D/E Ratio",
        "free_cash_flow_cr": "FCF (₹ Cr)",
        "revenue_cagr_5yr": "5Y Rev CAGR (%)",
        "composite_quality_score": "Score",
    }
    avail = [c for c in table_cols if c in merged.columns]
    matrix_df = merged[avail].rename(columns=renames)

    for c in ["ROE (%)", "ROCE (%)", "D/E Ratio", "FCF (₹ Cr)", "5Y Rev CAGR (%)", "Score"]:
        if c in matrix_df.columns:
            matrix_df[c] = pd.to_numeric(matrix_df[c], errors="coerce")

    col_config = {
        "Ticker": st.column_config.TextColumn("Ticker"),
        "Company Name": st.column_config.TextColumn("Company Name"),
        "Role": st.column_config.TextColumn("Role", help="Benchmark anchor vs Cohort peer"),
        "ROE (%)": st.column_config.NumberColumn("ROE", format="%.1f%%"),
        "ROCE (%)": st.column_config.NumberColumn("ROCE", format="%.1f%%"),
        "D/E Ratio": st.column_config.NumberColumn("D/E", format="%.2f"),
        "FCF (₹ Cr)": st.column_config.NumberColumn("FCF (₹ Cr)", format="₹%d Cr"),
        "5Y Rev CAGR (%)": st.column_config.NumberColumn("5Y Rev CAGR", format="%.1f%%"),
        "Score": st.column_config.ProgressColumn(
            "Quality Score",
            help="Bluestock Multi-Factor Composite Quality Score (0-100)",
            format="%.1f",
            min_value=0,
            max_value=100,
        ),
    }

    def highlight_benchmark_row(row):
        is_bm = str(row.get("Role", "")).strip().lower() == "benchmark" or str(row.get("status", "")).strip().lower() == "benchmark"
        return ['background-color: #FFEBAA; color: #0F172A; font-weight: bold;' if is_bm else '' for _ in row]

    st.dataframe(
        matrix_df.style.apply(highlight_benchmark_row, axis=1),
        column_config=col_config,
        use_container_width=True,
        hide_index=True,
    )


with tab_duel:
    st.markdown("##### ⚔️ **Head-to-Head Fundamental Duel (Select Any 2 Constituents)**")
    st.caption("Direct side-by-side comparison across profitability, capital efficiency, leverage, cash flow, and composite quality.")
    
    df_all_cos = get_companies()
    df_all_ratios = get_ratios(latest_only=True)
    if df_all_ratios.empty:
        df_all_ratios = get_ratios()
    if not df_all_ratios.empty and "year" in df_all_ratios.columns:
        df_all_ratios = df_all_ratios.sort_values("year").groupby("company_id", as_index=False).last()
        
    all_merged = pd.merge(df_all_cos, df_all_ratios, left_on="id", right_on="company_id", how="left")
    all_tickers = sorted(df_all_cos["id"].unique().tolist())
    ticker_display = {r["id"]: f"{r['company_name']} ({r['id']})" for _, r in df_all_cos.iterrows()}
    
    default_idx_a = all_tickers.index("TCS") if "TCS" in all_tickers else 0
    default_idx_b = all_tickers.index("INFY") if "INFY" in all_tickers else (1 if len(all_tickers) > 1 else 0)
    
    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        duel_co_a = st.selectbox("Select Company A (Primary)", all_tickers, index=default_idx_a, format_func=lambda t: ticker_display.get(t, t), key="duel_co_a")
    with col_sel_b:
        duel_co_b = st.selectbox("Select Company B (Challenger)", all_tickers, index=default_idx_b, format_func=lambda t: ticker_display.get(t, t), key="duel_co_b")
        
    row_a = all_merged[all_merged["id"] == duel_co_a]
    row_b = all_merged[all_merged["id"] == duel_co_b]
    
    if not row_a.empty and not row_b.empty:
        r_a = row_a.iloc[0]
        r_b = row_b.iloc[0]
        
        duel_kpis = [
            ("Composite Quality Score", "composite_quality_score", "{:.1f} pts", True),
            ("Return on Equity (ROE)", "return_on_equity_pct", "{:.1f}%", True),
            ("ROCE (Operating Return)", "return_on_capital_employed_pct", "{:.1f}%", True),
            ("Operating Profit Margin", "operating_profit_margin_pct", "{:.1f}%", True),
            ("5Y Revenue CAGR", "revenue_cagr_5yr", "{:.1f}%", True),
            ("5Y PAT Growth CAGR", "pat_cagr_5yr", "{:.1f}%", True),
            ("Debt-to-Equity Ratio", "debt_to_equity", "{:.2f}x", False),
            ("Free Cash Flow (FCF)", "free_cash_flow_cr", "₹{:,.0f} Cr", True),
        ]
        
        wins_a = 0
        wins_b = 0
        table_rows = []
        for label, k, fmt, higher_better in duel_kpis:
            val_a = safe_float(r_a.get(k), 0.0)
            val_b = safe_float(r_b.get(k), 0.0)
            str_a = fmt.format(val_a)
            str_b = fmt.format(val_b)
            
            if higher_better:
                if val_a > val_b:
                    win_tag = f"👑 {r_a['company_name']} (+{val_a - val_b:.1f})"
                    wins_a += 1
                elif val_b > val_a:
                    win_tag = f"👑 {r_b['company_name']} (+{val_b - val_a:.1f})"
                    wins_b += 1
                else:
                    win_tag = "🤝 Equal"
            else:
                if val_a < val_b:
                    win_tag = f"👑 {r_a['company_name']} (Lower Leverage)"
                    wins_a += 1
                elif val_b < val_a:
                    win_tag = f"👑 {r_b['company_name']} (Lower Leverage)"
                    wins_b += 1
                else:
                    win_tag = "🤝 Equal"
                    
            table_rows.append({
                "Operational Dimension": label,
                f"{r_a['company_name']} ({duel_co_a})": str_a,
                f"{r_b['company_name']} ({duel_co_b})": str_b,
                "Leader Advantage": win_tag,
            })
            
        render_raw_html(f"""
        <div class="dash-card" style="margin-bottom:16px; padding:16px 20px; border-left: 4px solid {'#0A84FF' if wins_a > wins_b else ('#30D158' if wins_b > wins_a else '#8E8E93')}; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; background: #1C1C1E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;">
            <div>
                <span class="header-org-badge" style="color: #0A84FF;">DUEL SCORECARD & BENCHMARK TALLY</span>
                <div style="font-size:19px; font-weight:700; color:#FFFFFF; margin-top:2px;">
                    {r_a['company_name']}: <span style="color:#0A84FF;">{wins_a} Wins</span> &nbsp;|&nbsp; 
                    {r_b['company_name']}: <span style="color:#30D158;">{wins_b} Wins</span>
                </div>
            </div>
            <div>
                <span class="badge {'badge-blue' if wins_a > wins_b else ('badge-green' if wins_b > wins_a else 'badge-gold')}" style="font-size:12px; padding:6px 14px;">
                    {'🏆 ' + r_a['company_name'] + ' Leads Duel' if wins_a > wins_b else ('🏆 ' + r_b['company_name'] + ' Leads Duel' if wins_b > wins_a else '🤝 Equal Standing')}
                </span>
            </div>
        </div>
        """)
        
        d_col_radar, d_col_table = st.columns([1.2, 1.4])
        with d_col_radar:
            st.markdown("###### 📊 **Direct 8-Axis Polar Radar Overlay**")
            radar_cats = ["ROE", "ROCE", "Net Margin", "Solvency (1/DE)", "FCF Quality", "PAT 5Y CAGR", "Rev 5Y CAGR", "Quality Score"]
            
            radar_vals_a = [
                normalize_val(r_a.get("return_on_equity_pct", 20), 0, 50),
                normalize_val(r_a.get("return_on_capital_employed_pct", 25), 0, 60),
                normalize_val(r_a.get("net_profit_margin_pct", 15), 0, 40),
                normalize_val(1.0 / (safe_float(r_a.get("debt_to_equity", 0.5)) + 0.1), 0.2, 10),
                normalize_val(safe_float(r_a.get("free_cash_flow_cr", 5000)), 0, 50000),
                normalize_val(safe_float(r_a.get("pat_cagr_5yr", 12)), -10, 40),
                normalize_val(safe_float(r_a.get("revenue_cagr_5yr", 12)), -10, 40),
                normalize_val(safe_float(r_a.get("composite_quality_score", 70)), 30, 100),
            ]
            radar_vals_b = [
                normalize_val(r_b.get("return_on_equity_pct", 20), 0, 50),
                normalize_val(r_b.get("return_on_capital_employed_pct", 25), 0, 60),
                normalize_val(r_b.get("net_profit_margin_pct", 15), 0, 40),
                normalize_val(1.0 / (safe_float(r_b.get("debt_to_equity", 0.5)) + 0.1), 0.2, 10),
                normalize_val(safe_float(r_b.get("free_cash_flow_cr", 5000)), 0, 50000),
                normalize_val(safe_float(r_b.get("pat_cagr_5yr", 12)), -10, 40),
                normalize_val(safe_float(r_b.get("revenue_cagr_5yr", 12)), -10, 40),
                normalize_val(safe_float(r_b.get("composite_quality_score", 70)), 30, 100),
            ]
            
            fig_duel_radar = go.Figure()
            fig_duel_radar.add_trace(go.Scatterpolar(
                r=radar_vals_a + [radar_vals_a[0]],
                theta=radar_cats + [radar_cats[0]],
                name=f"{r_a['company_name']} ({duel_co_a})",
                line=dict(color="#0A84FF", width=2.5),
                fill="toself",
                fillcolor="rgba(10, 132, 255, 0.15)",
            ))
            fig_duel_radar.add_trace(go.Scatterpolar(
                r=radar_vals_b + [radar_vals_b[0]],
                theta=radar_cats + [radar_cats[0]],
                name=f"{r_b['company_name']} ({duel_co_b})",
                line=dict(color="#30D158", width=2.5),
                fill="toself",
                fillcolor="rgba(48, 209, 88, 0.15)",
            ))
            fig_duel_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color="#8E8E93"), gridcolor="#2C2C2E"),
                    angularaxis=dict(tickfont=dict(size=10, color="#FFFFFF"), gridcolor="#2C2C2E"),
                ),
                showlegend=True,
                height=400,
                margin=dict(t=20, b=20, l=30, r=30),
            )
            apply_chart_theme(fig_duel_radar, height=400)
            st.plotly_chart(fig_duel_radar, use_container_width=True, config={"displayModeBar": False, "responsive": True})
            
        with d_col_table:
            st.markdown("###### 📋 **Side-by-Side Dimension Diagnostics**")
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
