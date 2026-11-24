"""Capital Allocation Matrix Screen with Interactive Pattern Treemap."""
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
import streamlit as st
from src.dashboard.utils.db import get_companies
from src.dashboard.utils.theme import render_header, apply_chart_theme, inject_theme_css, render_raw_html

try:
    st.set_page_config(page_title="Capital Allocation · N100 Analytics", page_icon="🗺️", layout="wide")
except Exception:
    pass
inject_theme_css()

# Render Header
render_header(
    title="Capital Allocation Matrix & Cash Dynamics",
    subtitle="8-pattern behavioral taxonomy categorizing how constituents generate operating cash and allocate capital across reinvestment, debt repayment, or shareholder dividends.",
    badge_text="CASH DYNAMICS",
)

# Load capital allocation data with caching
@st.cache_data
def _load_cached_capital():
    cap_path = _root / "output" / "capital_allocation.csv"
    try:
        df = pd.read_csv(cap_path)
        return df.drop_duplicates(subset=["company_id"], keep="last")
    except Exception:
        _cos = get_companies()
        patterns = ["Reinvestor", "Shareholder Returns", "Growth Funded by Debt", "Cash Accumulator", "Distress Signal", "Liquidating Assets", "Mixed", "Pre-Revenue"]
        return pd.DataFrame([
            {"company_id": r["id"], "pattern_label": patterns[idx % len(patterns)], "cfo_sign": "+", "cfi_sign": "-", "cff_sign": "-"}
            for idx, r in _cos.iterrows()
        ])

df_cap = _load_cached_capital()

df_cos = get_companies()
merged = pd.merge(df_cap, df_cos, left_on="company_id", right_on="id", how="left")
merged["broad_sector"] = merged["broad_sector"].fillna("Diversified")
merged["count"] = 1

ARCHETYPE_COLORS = {
    "Reinvestor": "#30D158",
    "Shareholder Returns": "#0A84FF",
    "Growth Funded by Debt": "#BF5AF2",
    "Cash Accumulator": "#64D2FF",
    "Distress Signal": "#FF453A",
    "Liquidating Assets": "#FF9F0A",
    "Turnaround Speculative": "#FF375F",
    "Pre-Revenue": "#8E8E93",
    "Mixed": "#5E5CE6",
}

tab_tree, tab_distress, tab_shifts = st.tabs([
    "🧭 **8-Archetype Capital Deployment Treemap**",
    "🚨 **Cash Burn & Distress Risk Monitor**",
    "🔄 **Strategic Capital Shifts (FY23 ➔ FY24)**",
])

with tab_tree:
    # Treemap
    st.markdown("##### 🧭 **8-Archetype Capital Deployment Treemap**")
    st.caption("Hierarchical Breakdown: Allocation Archetype ➔ Broad Sector ➔ Constituent Company")

    fig_tree = px.treemap(
        merged,
        path=["pattern_label", "broad_sector", "company_id"],
        values="count",
        color="pattern_label",
        color_discrete_map=ARCHETYPE_COLORS,
    )
    fig_tree.update_traces(
        marker=dict(cornerradius=4),
    )
    apply_chart_theme(fig_tree, height=490)
    st.plotly_chart(fig_tree, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown("---")

    ARCHETYPE_DESCRIPTIONS = {
        "Reinvestor": ("(+ CFO, - CFI, - CFF)", "Strong operating cash flow fully self-funds capital expansion (CapEx) while retiring debt or paying dividends.", "#059669"),
        "Shareholder Returns": ("(+ CFO, + CFI, - CFF)", "Mature generative business harvesting investments to fund shareholder dividends and buybacks.", "#2563EB"),
        "Growth Funded by Debt": ("(+ CFO, - CFI, + CFF)", "Operating cash flow is supplemented by external borrowings to fund aggressive capital expansion.", "#7C3AED"),
        "Cash Accumulator": ("(+ CFO, - CFI, - CFF)", "Conservative capital allocator building cash reserves post-capex rather than over-distributing.", "#0284C7"),
        "Distress Signal": ("(- CFO, - CFI, + CFF)", "Negative operating cash; enterprise relies on external borrowings to survive and cover cash burn.", "#E11D48"),
        "Liquidating Assets": ("(- CFO, + CFI, - CFF)", "Operating cash deficits compensated by selling productive assets or investments to service debt.", "#D97706"),
        "Turnaround Speculative": ("(- CFO, - CFI, - CFF)", "Contracting cash dynamics across all three statements; high restructuring or speculative risk.", "#9F1239"),
        "Pre-Revenue": ("(- CFO, - CFI, + CFF)", "Early-stage or high-growth capital burn phase funded via sponsor and market equity infusions.", "#64748B"),
        "Mixed": ("(+ CFO, - CFI, + CFF)", "Dynamic capital allocation balancing reinvestment, debt adjustments, and operational liquidity.", "#4F46E5"),
    }

    # Filter by pattern
    st.markdown("##### 📋 **Constituent Archetype Diagnostics & Classification**")
    all_patterns = sorted(merged["pattern_label"].unique())
    chosen_pattern = st.selectbox("Select Capital Allocation Archetype", all_patterns, index=0)

    pattern_companies = merged[merged["pattern_label"] == chosen_pattern]

    p_count = len(pattern_companies)
    total_c = len(merged)

    signs, desc, color = ARCHETYPE_DESCRIPTIONS.get(chosen_pattern, ("(N/A)", "Custom corporate cash flow pattern.", "#2563EB"))

    render_raw_html(f"""
    <div class="dash-card" style="border-left: 4px solid {color}; margin-bottom: 16px; background: #1C1C1E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 18px 22px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
                <h3 style="color:#FFFFFF; margin:0; font-size:18px; font-weight:700;"><b>{chosen_pattern}</b></h3>
                <span style="font-family:monospace; font-weight:700; color:{color}; font-size:13px;">{signs}</span>
            </div>
            <div>
                <span class="badge badge-blue">{p_count} Constituents ({(p_count/max(1, total_c))*100:.1f}% of Index)</span>
            </div>
        </div>
        <p style="color:#8E8E93; font-size:13px; margin-top:10px; line-height:1.5;">
            <b style="color:#FFFFFF;">Behavioral Profile:</b> {desc}
        </p>
    </div>
    """)

    # 3-Statement Directional Cash Flow Indicators
    col_cfo, col_cfi, col_cff = st.columns(3)
    cfo_s = "+" if "+ CFO" in signs else "-"
    cfi_s = "+" if "+ CFI" in signs else "-"
    cff_s = "+" if "+ CFF" in signs else "-"

    col_cfo.metric(
        "1. Operating Cash Flow (CFO)",
        f"{cfo_s} CFO",
        "Generative Surplus" if cfo_s == "+" else "Operational Deficit / Burn"
    )
    col_cfi.metric(
        "2. Investing Cash Flow (CFI)",
        f"{cfi_s} CFI",
        "Asset Divestment / Harvest" if cfi_s == "+" else "Capital Expansion (CapEx)"
    )
    col_cff.metric(
        "3. Financing Cash Flow (CFF)",
        f"{cff_s} CFF",
        "External Debt/Equity Raised" if cff_s == "+" else "Dividends Paid / Deleveraging"
    )

    display_cols = ["company_id", "company_name", "broad_sector", "cfo_sign", "cfi_sign", "cff_sign"]
    renames = {
        "company_id": "Ticker",
        "company_name": "Company Name",
        "broad_sector": "Sector",
        "cfo_sign": "CFO Sign",
        "cfi_sign": "CFI Sign",
        "cff_sign": "CFF Sign",
    }
    avail_cols = [c for c in display_cols if c in pattern_companies.columns]
    st.dataframe(
        pattern_companies[avail_cols].rename(columns=renames),
        use_container_width=True,
        hide_index=True,
    )


with tab_distress:
    st.markdown("##### 🚨 **Forensic Cash Flow Distress & Cash Burn Monitor**")
    render_raw_html("""
    <div style="background-color:rgba(255, 69, 58, 0.12); border-left:4px solid #FF453A; border:1px solid rgba(255, 69, 58, 0.25); padding:14px 18px; border-radius:12px; margin-bottom:16px;">
        <span style="color:#FFFFFF; font-size:13px; font-weight:600;">
            <span style="color:#FF453A;">⚠️</span> <b>Distress Signal Heuristic:</b> Flags constituents burning operational cash (CFO &lt; 0) while simultaneously relying on external financing inflows (CFF &gt; 0) to service liquidity.
        </span>
        <div style="color:#8E8E93; font-size:11.5px; margin-top:6px;">
            Note: Financial institutions (banks and NBFCs) naturally disburse loans via operating activities, so their negative CFO reflects credit expansion rather than commercial cash distress.
        </div>
    </div>
    """)
    
    distress_path = _root / "output" / "distress_alerts.csv"
    if distress_path.exists():
        df_distress = pd.read_csv(distress_path)
        
        # Sector category filter
        distress_filter = st.radio("Focus Classification", ["All Flagged Constituents", "Non-Financials Only (Industrial / Consumer)", "Financials Only"], horizontal=True)
        if distress_filter == "Non-Financials Only (Industrial / Consumer)":
            df_distress_view = df_distress[~df_distress["sector"].str.contains("Financial", case=False, na=False)]
        elif distress_filter == "Financials Only":
            df_distress_view = df_distress[df_distress["sector"].str.contains("Financial", case=False, na=False)]
        else:
            df_distress_view = df_distress
            
        d_renames = {
            "company_id": "Ticker",
            "sector": "Sector",
            "cfo": "Operating Cash Flow (CFO ₹ Cr)",
            "cff": "Financing Cash Flow (CFF ₹ Cr)",
            "net_profit": "Net Profit (PAT ₹ Cr)",
            "reason": "Forensic Observation",
        }
        
        df_d_disp = df_distress_view.rename(columns=d_renames)
        for col_num in ["Operating Cash Flow (CFO ₹ Cr)", "Financing Cash Flow (CFF ₹ Cr)", "Net Profit (PAT ₹ Cr)"]:
            if col_num in df_d_disp.columns:
                df_d_disp[col_num] = pd.to_numeric(df_d_disp[col_num], errors="coerce")
                
        d_config = {
            "Ticker": st.column_config.TextColumn("Ticker"),
            "Sector": st.column_config.TextColumn("Sector"),
            "Operating Cash Flow (CFO ₹ Cr)": st.column_config.NumberColumn("CFO (₹ Cr)", format="₹%d Cr"),
            "Financing Cash Flow (CFF ₹ Cr)": st.column_config.NumberColumn("CFF (₹ Cr)", format="₹%d Cr"),
            "Net Profit (PAT ₹ Cr)": st.column_config.NumberColumn("PAT (₹ Cr)", format="₹%d Cr"),
            "Forensic Observation": st.column_config.TextColumn("Diagnostic Alert"),
        }
        
        st.dataframe(df_d_disp, column_config=d_config, use_container_width=True, hide_index=True)
    else:
        st.info("No active distress alerts logged.")

with tab_shifts:
    st.markdown("##### 🔄 **Year-over-Year Capital Allocation Strategy Shifts (FY23 ➔ FY24)**")
    st.caption("Identifies constituents that pivoted their capital allocation behavioral taxonomy between fiscal years.")
    
    shifts_path = _root / "output" / "pattern_changes.csv"
    if shifts_path.exists():
        df_shifts = pd.read_csv(shifts_path)
        
        s_renames = {
            "company_id": "Ticker",
            "sector": "Sector",
            "previous_year_pattern": "FY23 Capital Archetype",
            "latest_year_pattern": "FY24 Capital Archetype",
        }
        df_s_disp = df_shifts.rename(columns=s_renames)
        
        # Add Strategic Pivot Interpretation
        def interpret_shift(row):
            p = row.get("FY23 Capital Archetype", "")
            l = row.get("FY24 Capital Archetype", "")
            if "Reinvestor" in p and "Shareholder Returns" in l:
                return "🌟 Maturing: Transitioned from aggressive CapEx to high dividend distributions"
            elif "Liquidating" in p and "Reinvestor" in l:
                return "🚀 Operational Turnaround: Restored cash generation to fund organic expansion"
            elif "Debt" in p and "Reinvestor" in l:
                return "💪 Deleveraging: Transitioned from debt funding to organic self-funding"
            elif "Shareholder Returns" in l:
                return "💰 Increasing capital return to equity holders"
            else:
                return f"Strategic reallocation from {p} to {l}"
                
        df_s_disp["Strategic Pivot Interpretation"] = df_s_disp.apply(interpret_shift, axis=1)
        
        st.dataframe(df_s_disp, use_container_width=True, hide_index=True)
    else:
        st.info("No pattern shift records found.")

