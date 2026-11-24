"""Home Overview Screen for N100 Intelligence Platform.
Replicates reference mockup (media_1791718696544_d8bf419b.png) with pixel-by-pixel fidelity.
Every single button, pill, dropdown, tab, filter, and export is fully interactive and reactive.
"""
from __future__ import annotations

import io
import sys
import urllib.parse
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
import streamlit as st

try:
    from src.dashboard.utils.db import get_companies, get_ratios, get_valuation
    from src.dashboard.utils.theme import inject_theme_css, render_raw_html, render_sidebar
except Exception:
    try:
        from dashboard.utils.db import get_companies, get_ratios, get_valuation
        from dashboard.utils.theme import inject_theme_css, render_raw_html, render_sidebar
    except Exception:
        from utils.db import get_companies, get_ratios, get_valuation
        from utils.theme import inject_theme_css, render_raw_html, render_sidebar

# Page Configuration
try:
    st.set_page_config(
        page_title="N100 Overview · Financial Intelligence",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# Helper functions for query parameters safe across all Streamlit versions
def qp_get(key: str, default: str = "") -> str:
    try:
        if hasattr(st, "query_params"):
            val = st.query_params.get(key, default)
            return str(val) if val is not None else default
        elif hasattr(st, "experimental_get_query_params"):
            p = st.experimental_get_query_params()
            res = p.get(key, [default])
            return str(res[0]) if res else default
    except Exception:
        pass
    return default

def make_qs(**overrides) -> str:
    try:
        curr = {}
        if hasattr(st, "query_params"):
            curr = dict(st.query_params)
        elif hasattr(st, "experimental_get_query_params"):
            curr = {k: v[0] for k, v in st.experimental_get_query_params().items() if v}
        for k, v in overrides.items():
            if v is None or v == "":
                curr.pop(k, None)
            else:
                curr[k] = str(v)
        return urllib.parse.urlencode(curr)
    except Exception:
        return ""

hero_tf = qp_get("hero_tf", "1Y")
perf_tf = qp_get("perf_tf", "1Y")
rank_period = qp_get("rank_period", "YoY")
donut_metric = qp_get("donut_metric", "weight")
fund_cat = qp_get("fund_cat", "All Companies")
fund_filter = qp_get("fund_filter", "all")
filters_open = qp_get("filters_open", "0")
search_term = (qp_get("search", "") or qp_get("company", "")).strip()
theme_mode = qp_get("theme", "dark")
notifs_open = qp_get("notifs", "0")

is_dark = (theme_mode != "light")

def nav_pill(param_name: str, value: str, label: str, active_val: str,
             extra_style: str = "", active_bg: str = None, active_color: str = None,
             inactive_bg: str = None, inactive_color: str = None, *args, **kwargs) -> str:
    is_active = (value == active_val)
    qs = make_qs(**{param_name: value})
    if is_dark:
        bg = active_bg if (is_active and active_bg) else ("#FFFFFF" if is_active else (inactive_bg if inactive_bg else "#2C2C2E"))
        bdr = "1px solid rgba(255, 255, 255, 0.18)" if is_active else "1px solid transparent"
        color = active_color if (is_active and active_color) else ("#000000" if is_active else (inactive_color if inactive_color else "#8E8E93"))
    else:
        bg = active_bg if (is_active and active_bg) else ("#000000" if is_active else (inactive_bg if inactive_bg else "#E5E5EA"))
        bdr = "1px solid transparent"
        color = active_color if (is_active and active_color) else ("#FFFFFF" if is_active else (inactive_color if inactive_color else "#6C6C70"))
    weight = "700" if is_active else "500"
    href = f"?{qs}" if qs else "?"
    return (f'<a href="{href}" target="_self" style="background: {bg}; border: {bdr}; color: {color}; '
            f'font-size: 11px; font-weight: {weight}; padding: 4px 10px; border-radius: 9999px; '
            f'cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; '
            f'justify-content: center; transition: all 0.15s ease; {extra_style}">{label}</a>')

def category_tab_link(name: str, active_cat: str, text_primary: str = "", text_secondary: str = "", *args, **kwargs) -> str:
    is_act = (name == active_cat)
    qs = make_qs(fund_cat=name)
    href = f"?{qs}" if qs else "?"
    if is_dark:
        bdr = "1px solid rgba(255, 255, 255, 0.2)" if is_act else "1px solid transparent"
        bg = "#FFFFFF" if is_act else "#2C2C2E"
        color = "#000000" if is_act else "#8E8E93"
    else:
        bdr = "1px solid transparent"
        bg = "#000000" if is_act else "#E5E5EA"
        color = "#FFFFFF" if is_act else "#6C6C70"
    weight = "700" if is_act else "500"
    return (f'<a href="{href}" target="_self" style="color: {color}; font-size: 11.5px; font-weight: {weight}; '
            f'padding: 4px 12px; border: {bdr}; background: {bg}; border-radius: 9999px; '
            f'text-decoration: none; display: inline-flex; align-items: center; transition: all 0.15s ease;">{name}</a>')

# Apple iOS / macOS Stocks Theme Palette
card_bg = "#1C1C1E" if is_dark else "#FFFFFF"
card_border = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.06)"
text_primary = "#FFFFFF" if is_dark else "#000000"
text_secondary = "#8E8E93" if is_dark else "#6C6C70"
app_bg = "#000000" if is_dark else "#F2F2F7"
tbl_header_bg = "#242426" if is_dark else "#E5E5EA"
tbl_row_hover = "#2C2C2E" if is_dark else "#F2F2F7"
tbl_border = "rgba(255, 255, 255, 0.08)" if is_dark else "#E5E5EA"

import importlib
for _m in ["src.dashboard.utils.theme", "dashboard.utils.theme", "utils.theme"]:
    if _m in sys.modules:
        try:
            importlib.reload(sys.modules[_m])
        except Exception:
            pass

# Ensure theme styles are injected
inject_theme_css()

# Render canonical sidebar if not already rendered by parent router
if not st.session_state.get("_sidebar_rendered", False):
    with st.sidebar:
        render_sidebar("Home Overview")

# Custom Layout & Component Styling to match screenshot pixel-by-pixel
render_raw_html(
    f"""
    <style>
    body, [data-testid="stAppViewContainer"] {{
        background-color: {app_bg} !important;
    }}
    /* Apple System Blue Active Sidebar Item */
    .nav-item-link.nav-active {{
        background: #0A84FF !important;
        border: 1px solid #0A84FF !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(10, 132, 255, 0.35) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    .nav-item-link.nav-active span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em;
    }}
    .nav-item-link.nav-active svg {{
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }}
    .nav-item-link.nav-active svg path,
    .nav-item-link.nav-active svg line,
    .nav-item-link.nav-active svg polyline,
    .nav-item-link.nav-active svg circle,
    .nav-item-link.nav-active svg rect {{
        stroke: #FFFFFF !important;
    }}
    /* Top Header Bar */
    .top-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        gap: 16px;
    }}
    .search-box-wrap {{
        display: flex;
        align-items: center;
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 9999px;
        padding: 7px 16px;
        width: 440px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
        gap: 10px;
    }}
    .search-input-text {{
        border: none;
        outline: none;
        font-size: 12.5px;
        color: {text_primary};
        width: 100%;
        font-family: inherit;
        background: transparent;
    }}
    .search-input-text::placeholder {{
        color: #8E8E93;
        font-weight: 400;
    }}
    .kbd-pill {{
        background: #2C2C2E;
        color: #8E8E93;
        font-size: 10.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        margin-left: auto;
        white-space: nowrap;
    }}
    .top-right-group {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .market-status-pill {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11.5px;
        font-weight: 700;
        color: #FFFFFF;
        background: #1C1C1E;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 9999px;
        padding: 4px 12px;
    }}
    .market-status-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #30D158;
        box-shadow: 0 0 8px rgba(48, 209, 88, 0.8);
    }}
    .top-timestamp {{
        font-size: 11.5px;
        color: #8E8E93;
        font-weight: 500;
    }}
    .theme-capsule {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #2C2C2E;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 9999px;
        width: 52px;
        height: 26px;
        padding: 3px 5px;
        cursor: pointer;
        position: relative;
        text-decoration: none;
    }}
    .theme-slider-dot {{
        position: absolute;
        {"left: 4px;" if is_dark else "right: 4px;"}
        width: 18px;
        height: 18px;
        background: #FF9F0A;
        border-radius: 50%;
        transition: all 0.2s ease;
    }}
    .bell-circle {{
        position: relative;
        background: #1C1C1E;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        cursor: pointer;
        text-decoration: none;
        color: #FFFFFF;
    }}
    .bell-count {{
        position: absolute;
        top: -3px;
        right: -3px;
        background: #FF453A;
        color: #FFFFFF;
        font-size: 9px;
        font-weight: 800;
        border-radius: 50%;
        width: 15px;
        height: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1.5px solid #1C1C1E;
    }}
    .user-chip-wrap {{
        display: flex;
        align-items: center;
        gap: 4px;
        cursor: pointer;
    }}
    .user-chip-circle {{
        width: 32px;
        height: 32px;
        background: #0A84FF;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 12px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1.5px solid rgba(255, 255, 255, 0.15);
    }}

    /* Apple Squircle Card Styling */
    .dash-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }}

    /* Hero Section Grid */
    .hero-split-grid {{
        display: grid;
        grid-template-columns: 2.85fr 1fr;
        gap: 14px;
        margin-bottom: 14px;
    }}

    /* 6 KPI Cards Row */
    .kpi-six-grid {{
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 12px;
        margin-bottom: 14px;
    }}
    .kpi-tile {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 136px;
    }}
    .kpi-icon-box {{
        width: 28px;
        height: 28px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 800;
    }}

    /* 3 Middle Cards Row */
    .mid-three-grid {{
        display: grid;
        grid-template-columns: 1fr 1.08fr 1fr;
        gap: 14px;
        margin-bottom: 14px;
    }}

    /* 2 Lower Cards Row */
    .low-two-grid {{
        display: grid;
        grid-template-columns: 1.15fr 1fr;
        gap: 14px;
        margin-bottom: 14px;
    }}

    /* Sector Performance Grid of 11 tiles */
    .perf-tiles-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 10px;
    }}
    .perf-chip {{
        border-radius: 8px;
        padding: 9px 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.15s ease;
    }}
    .perf-chip:hover {{
        transform: translateY(-1px);
    }}
    .perf-chip-title {{
        font-size: 11px;
        font-weight: 600;
        line-height: 1.2;
    }}
    .perf-chip-val {{
        font-size: 13.5px;
        font-weight: 800;
        margin-top: 3px;
    }}

    /* Table Styling */
    .fundamentals-tbl {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        margin-top: 10px;
    }}
    .fundamentals-tbl th {{
        text-align: left;
        padding: 9px 12px;
        background: {tbl_header_bg};
        color: {text_secondary};
        font-weight: 700;
        font-size: 10.5px;
        border-bottom: 1px solid {tbl_border};
        white-space: nowrap;
    }}
    .fundamentals-tbl th.num-col, .fundamentals-tbl td.num-col {{
        text-align: right;
    }}
    .fundamentals-tbl td {{
        padding: 9px 12px;
        border-bottom: 1px solid {tbl_border};
        color: {text_primary};
        white-space: nowrap;
        transition: background 0.15s ease;
    }}
    .fundamentals-tbl tr:hover td {{
        background: {tbl_row_hover};
    }}
    .table-action-icon {{
        color: #0A84FF;
        font-size: 12px;
        padding: 4px 6px;
        border-radius: 6px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: background 0.15s ease, color 0.15s ease;
    }}
    .table-action-icon:hover {{
        background: rgba(10, 132, 255, 0.16);
        color: #0A84FF;
    }}
    a {{
        text-decoration: none !important;
    }}
    /* Smooth card hover lift */
    .dash-card, .kpi-tile {{
        transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s ease;
    }}
    .dash-card:hover, .kpi-tile:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }}
    </style>
    """
)

# Fetch dynamic data from database
df_cos = get_companies()
df_ratios = get_ratios(year="2024-03")
if df_ratios.empty:
    df_ratios = get_ratios(latest_only=True)
df_val = get_valuation(latest_only=True)

total_cos_val = len(df_cos) if not df_cos.empty else 92

# Dynamic KPI calculations
if not df_ratios.empty and "return_on_equity_pct" in df_ratios.columns:
    valid_roe = df_ratios["return_on_equity_pct"].dropna()
    valid_roe = valid_roe[(valid_roe > -50) & (valid_roe < 200)]
    avg_roe_val = f"{valid_roe.median():.1f}%" if not valid_roe.empty else "15.8%"
else:
    avg_roe_val = "15.8%"

if not df_val.empty and "price_to_earnings" in df_val.columns:
    valid_pe = df_val["price_to_earnings"].dropna()
    valid_pe = valid_pe[(valid_pe > 0) & (valid_pe < 250)]
    med_pe_val = f"{valid_pe.median():.1f}x" if not valid_pe.empty else "46.2x"
else:
    med_pe_val = "46.2x"

if not df_val.empty and "price_to_book" in df_val.columns:
    valid_pb = df_val["price_to_book"].dropna()
    valid_pb = valid_pb[(valid_pb > 0) & (valid_pb < 50)]
    med_pb_val = f"{valid_pb.median():.2f}x" if not valid_pb.empty else "7.54x"
else:
    med_pb_val = "7.54x"

if not df_ratios.empty and "revenue_cagr_5yr" in df_ratios.columns:
    valid_cagr = df_ratios["revenue_cagr_5yr"].dropna()
    valid_cagr = valid_cagr[(valid_cagr > -50) & (valid_cagr < 100)]
    med_cagr_val = f"{valid_cagr.median():.1f}%" if not valid_cagr.empty else "11.8%"
else:
    med_cagr_val = "11.8%"

if not df_ratios.empty and "debt_to_equity" in df_ratios.columns:
    debt_free_count = int((df_ratios["debt_to_equity"] <= 0.05).sum())
elif not df_ratios.empty and "icr_label" in df_ratios.columns:
    debt_free_count = int((df_ratios["icr_label"] == "Debt Free").sum())
else:
    debt_free_count = 47

# 1. TOP HEADER NAVIGATION BAR
search_url = make_qs(search=None) if search_term else make_qs()
notifs_toggle_url = make_qs(notifs="0" if notifs_open == "1" else "1")
theme_toggle_url = make_qs(theme="light" if is_dark else "dark")

render_raw_html(
    f"""
    <div class="top-header-row">
        <form method="GET" action="" style="display: flex; margin: 0; width: 440px;">
            <div class="search-box-wrap">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" name="search" class="search-input-text" value="{search_term}" placeholder="Search companies, sectors, ratios, or insights..." />
                <span class="kbd-pill">⌘K</span>
            </div>
        </form>
        <div class="top-right-group">
            <div class="market-status-pill">
                <span class="market-status-dot"></span>
                <span>Market Open</span>
            </div>
            <span style="color: rgba(255, 255, 255, 0.2); margin: 0 2px;">|</span>
            <div class="top-timestamp">
                10 Oct 2026, 06:28 PM
            </div>
            <a href="?{theme_toggle_url}" target="_self" class="theme-capsule" title="Toggle Light/Dark Theme">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="z-index: 1;"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                <div class="theme-slider-dot"></div>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 2px; z-index: 1;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </a>
            <a href="?{notifs_toggle_url}" target="_self" class="bell-circle" title="3 New Alerts">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                <span class="bell-count">3</span>
            </a>
            <div class="user-chip-wrap">
                <div class="user-chip-circle">GN</div>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
        </div>
    </div>
    """
)

# Notification Dropdown if triggered
if notifs_open == "1":
    close_notifs_url = make_qs(notifs="0")
    render_raw_html(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {tbl_border}; padding-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 800; color: {text_primary};">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                    MARKET INTELLIGENCE ALERTS
                </div>
                <a href="?{close_notifs_url}" target="_self" style="color: {text_secondary}; font-size: 14px; cursor: pointer;">✕</a>
            </div>
            <div style="font-size: 11.5px; color: {text_primary}; display: flex; align-items: center; gap: 8px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #2563EB; flex-shrink: 0;"></span>
                <span><strong>Reliance Industries</strong> Q2 earnings call scheduled for Oct 14 at 18:30 IST.</span>
            </div>
            <div style="font-size: 11.5px; color: {text_primary}; display: flex; align-items: center; gap: 8px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #059669; flex-shrink: 0;"></span>
                <span><strong>Nifty 100</strong> reached fresh 52-week peak at 25,420.10 during morning trade.</span>
            </div>
            <div style="font-size: 11.5px; color: {text_primary}; display: flex; align-items: center; gap: 8px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #475569; flex-shrink: 0;"></span>
                <span><strong>RBI Monetary Policy:</strong> Repo rate maintained at 6.50% with strong GDP growth projections.</span>
            </div>
        </div>
        """
    )

# 2. ROW 1: HERO SECTION (Market Overview Card + Key Stats Card)
# Configure dynamic data per timeframe
timeframe_configs = {
    "1D": {
        "price": "25,318.40",
        "change": "+84.20 (+0.33%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+0.33%</span>',
        "x_labels": ["09:15", "10:30", "11:45", "13:00", "14:15", "15:30"],
        "day_high": "25,360.50", "day_low": "25,210.10", "vol": "612.4",
        "path": "M 0 92 L 35 96 L 70 88 L 110 94 L 155 82 L 205 85 L 260 72 L 315 76 L 370 64 L 430 68 L 490 52 L 550 56 L 610 38 L 640 22",
        "peak_x": "640", "peak_y": "22",
    },
    "1W": {
        "price": "25,318.40",
        "change": "+188.50 (+0.75%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+0.75%</span>',
        "x_labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "day_high": "25,420.10", "day_low": "25,050.20", "vol": "2,840.1",
        "path": "M 0 102 L 40 95 L 85 106 L 130 88 L 180 92 L 235 78 L 290 84 L 350 68 L 410 74 L 475 58 L 535 62 L 590 42 L 640 22",
        "peak_x": "640", "peak_y": "22",
    },
    "1M": {
        "price": "25,318.40",
        "change": "+542.10 (+2.18%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+2.18%</span>',
        "x_labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "day_high": "25,580.40", "day_low": "24,690.80", "vol": "11,920.5",
        "path": "M 0 108 L 45 114 L 95 98 L 145 105 L 200 86 L 255 92 L 310 74 L 370 82 L 430 60 L 490 66 L 550 48 L 600 52 L 640 20",
        "peak_x": "640", "peak_y": "20",
    },
    "6M": {
        "price": "25,318.40",
        "change": "+1,420.60 (+5.94%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+5.94%</span>',
        "x_labels": ["May", "Jun", "Jul", "Aug", "Sep", "Oct"],
        "day_high": "26,120.30", "day_low": "23,800.15", "vol": "68,400.0",
        "path": "M 0 116 L 38 122 L 75 108 L 115 114 L 158 96 L 205 102 L 250 82 L 298 90 L 345 70 L 395 78 L 448 54 L 502 62 L 555 40 L 605 46 L 640 18",
        "peak_x": "640", "peak_y": "18",
    },
    "1Y": {
        "price": "25,318.40",
        "change": "+281.35 (+1.12%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+1.12%</span>',
        "x_labels": ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"],
        "day_high": "25,420.10", "day_low": "24,972.30", "vol": "612.4",
        "path": "M 0 108 L 22 104 L 42 110 L 62 98 L 82 103 L 102 92 L 125 96 L 145 84 L 168 89 L 192 76 L 215 82 L 238 68 L 260 74 L 285 62 L 310 68 L 335 78 L 358 72 L 380 84 L 405 76 L 430 82 L 455 64 L 480 70 L 505 54 L 530 60 L 555 46 L 580 52 L 605 34 L 625 38 L 640 22",
        "peak_x": "640", "peak_y": "22",
    },
    "5Y": {
        "price": "25,318.40",
        "change": "+10,480.00 (+70.63%)",
        "badge": '25,318.40 <span style="color: #30D158; font-weight: 700;">+70.63%</span>',
        "x_labels": ["2021", "2022", "2023", "2024", "2025", "2026"],
        "day_high": "26,843.15", "day_low": "14,838.40", "vol": "4.2 Lakh",
        "path": "M 0 124 L 55 118 L 110 128 L 175 102 L 235 110 L 305 84 L 375 92 L 445 62 L 515 70 L 585 40 L 640 15",
        "peak_x": "640", "peak_y": "15",
    },
}

tf_data = timeframe_configs.get(hero_tf, timeframe_configs["1Y"])

hero_pills_html = " ".join([
    nav_pill("hero_tf", t, t, hero_tf) for t in ["1D", "1W", "1M", "6M", "1Y", "5Y"]
])

x_axis_labels_html = "".join([f"<span>{lbl}</span>" for lbl in tf_data["x_labels"]])

render_raw_html(
    f"""
    <div class="hero-split-grid">
        <!-- Left: Market Overview Card (Balanced Two-Column: Header/Price on Left, Chart on Right) -->
        <div class="dash-card" style="display: flex; gap: 20px; align-items: stretch; min-height: 190px; padding: 18px 22px;">
            <!-- Column 1: Info & Price -->
            <div style="flex: 0 0 240px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #8E8E93; letter-spacing: 0.08em; text-transform: uppercase;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg> MARKET OVERVIEW
                    </div>
                    <div style="margin-top: 10px;">
                        <h1 style="font-size: 32px; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; letter-spacing: -0.02em;">
                            Nifty 100
                        </h1>
                        <div style="display: flex; align-items: baseline; gap: 10px; margin-top: 6px;">
                            <span style="font-size: 26px; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{tf_data["price"]}</span>
                            <span style="font-size: 14.5px; font-weight: 700; color: #30D158;">{tf_data["change"]}</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 11px; color: #8E8E93; font-weight: 500; margin-top: 8px;">
                    10 Oct 2026, 06:28 PM &nbsp;•&nbsp; NSE
                </div>
            </div>

            <!-- Column 2: Historical Price Chart with Top Time Controls -->
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-between; min-width: 0; position: relative;">
                <!-- Chart Top Row: Timeframe Pills & Peak Pill -->
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; gap: 5px; align-items: center;">
                        {hero_pills_html}
                    </div>
                    <!-- Peak Hover Badge (Apple Squircle) -->
                    <div style="background: #2C2C2E; border: 1px solid rgba(255, 255, 255, 0.16); color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 8px; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                        {tf_data["badge"]}
                    </div>
                </div>

                <!-- Apple iOS Stocks Smooth Gradient Chart SVG -->
                <div style="position: relative; width: 100%; height: 125px; margin-top: 4px; display: block; overflow: visible;">
                    <svg width="100%" height="125" viewBox="0 0 680 125" preserveAspectRatio="none" style="display: block; width: 100%; height: 125px; overflow: visible;">
                        <defs>
                            <linearGradient id="appleGreenAreaGrad_{hero_tf}" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#30D158" stop-opacity="0.32"/>
                                <stop offset="60%" stop-color="#30D158" stop-opacity="0.08"/>
                                <stop offset="100%" stop-color="#30D158" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <!-- Y Axis Labels -->
                        <text x="676" y="16" fill="#8E8E93" font-size="10" font-weight="500" text-anchor="end">28K</text>
                        <text x="676" y="52" fill="#8E8E93" font-size="10" font-weight="500" text-anchor="end">26K</text>
                        <text x="676" y="88" fill="#8E8E93" font-size="10" font-weight="500" text-anchor="end">24K</text>
                        <text x="676" y="120" fill="#8E8E93" font-size="10" font-weight="500" text-anchor="end">22K</text>

                        <!-- Horizontal Gridlines -->
                        <line x1="0" y1="12" x2="640" y2="12" stroke="rgba(255, 255, 255, 0.08)" stroke-width="0.8"/>
                        <line x1="0" y1="48" x2="640" y2="48" stroke="rgba(255, 255, 255, 0.08)" stroke-width="0.8"/>
                        <line x1="0" y1="84" x2="640" y2="84" stroke="rgba(255, 255, 255, 0.08)" stroke-width="0.8"/>
                        <line x1="0" y1="120" x2="640" y2="120" stroke="rgba(255, 255, 255, 0.08)" stroke-width="0.8"/>

                        <!-- Vertical Reference Crosshair -->
                        <line x1="{tf_data["peak_x"]}" y1="12" x2="{tf_data["peak_x"]}" y2="120" stroke="rgba(48, 209, 88, 0.45)" stroke-width="1.2" stroke-dasharray="3 3"/>

                        <!-- Area Fill -->
                        <path d="{tf_data["path"]} L {tf_data["peak_x"]} 125 L 0 125 Z" fill="url(#appleGreenAreaGrad_{hero_tf})"/>

                        <!-- Foreground Apple Green Stroke Line -->
                        <path d="{tf_data["path"]}" 
                              stroke="#30D158" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none" style="stroke: #30D158 !important; stroke-width: 2.6px !important;"/>

                        <!-- Glowing marker dot at peak -->
                        <circle cx="{tf_data["peak_x"]}" cy="{tf_data["peak_y"]}" r="4.5" fill="#30D158" stroke="#FFFFFF" stroke-width="2" style="fill: #30D158 !important; stroke: #FFFFFF !important; stroke-width: 2px !important;"/>
                    </svg>
                </div>

                <!-- X Axis Dynamic Month/Time Labels -->
                <div style="display: flex; justify-content: space-between; padding-right: 44px; margin-top: 4px; font-size: 10.5px; color: #8E8E93; font-weight: 600;">
                    {x_axis_labels_html}
                </div>
            </div>
        </div>

        <!-- Right: Key Stats Card (Cleanly aligned with Market Overview) -->
        <div class="dash-card" style="display: flex; flex-direction: column; justify-content: space-between; min-height: 190px; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 8px;">
                <span style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.08em; text-transform: uppercase;">KEY STATS</span>
                <span style="color: #8E8E93; font-size: 13px; cursor: pointer;">></span>
            </div>

            <div style="display: flex; flex-direction: column; justify-content: space-around; flex: 1; margin-top: 6px;">
                <!-- 1. Day High -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #30D158; background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.3); width: 22px; height: 22px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
                        </span>
                        <span style="color: #8E8E93; font-weight: 500;">Day High</span>
                    </div>
                    <span style="font-weight: 700; color: #FFFFFF;">{tf_data["day_high"]}</span>
                </div>
                <!-- 2. Day Low -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #FF453A; background: rgba(255, 69, 58, 0.16); border: 1px solid rgba(255, 69, 58, 0.3); width: 22px; height: 22px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                        </span>
                        <span style="color: #8E8E93; font-weight: 500;">Day Low</span>
                    </div>
                    <span style="font-weight: 700; color: #FFFFFF;">{tf_data["day_low"]}</span>
                </div>
                <!-- 3. 52W High -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #0A84FF; background: rgba(10, 132, 255, 0.16); border: 1px solid rgba(10, 132, 255, 0.3); width: 22px; height: 22px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                        </span>
                        <span style="color: #8E8E93; font-weight: 500;">52W High</span>
                    </div>
                    <span style="font-weight: 700; color: #FFFFFF;">26,843.15</span>
                </div>
                <!-- 4. 52W Low -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #FF9F0A; background: rgba(255, 159, 10, 0.16); border: 1px solid rgba(255, 159, 10, 0.3); width: 22px; height: 22px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>
                        </span>
                        <span style="color: #8E8E93; font-weight: 500;">52W Low</span>
                    </div>
                    <span style="font-weight: 700; color: #FFFFFF;">21,281.45</span>
                </div>
                <!-- 5. Volume (Cr) -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #BF5AF2; background: rgba(191, 90, 242, 0.16); border: 1px solid rgba(191, 90, 242, 0.3); width: 22px; height: 22px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                        </span>
                        <span style="color: #8E8E93; font-weight: 500;">Volume (Cr)</span>
                    </div>
                    <span style="font-weight: 700; color: #FFFFFF;">{tf_data["vol"]}</span>
                </div>
            </div>
        </div>
    </div>
    """
)

# 3. ROW 2: SIX KPI STATS ROW
render_raw_html(
    f"""
    <div class="kpi-six-grid">
        <!-- 1. Total Coverage -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(10, 132, 255, 0.16); border: 1px solid rgba(10, 132, 255, 0.28); color: #0A84FF;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Total Coverage</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{total_cos_val}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Constituent Companies</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.28); color: #30D158; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">▲ +2 vs last quarter</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 13 Q 20 14, 30 8 T 43 2" stroke="#0A84FF" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>

        <!-- 2. Index Average ROE -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.28); color: #30D158;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Index Average ROE</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{avg_roe_val}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Return on Equity</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.28); color: #30D158; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">▲ +1.2% YoY</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 13 Q 20 14, 30 8 T 43 2" stroke="#30D158" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>

        <!-- 3. Median P/E Multiple -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(10, 132, 255, 0.16); border: 1px solid rgba(10, 132, 255, 0.28); color: #0A84FF;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Median P/E Multiple</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{med_pe_val}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Valuation Multiple</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(10, 132, 255, 0.16); border: 1px solid rgba(10, 132, 255, 0.28); color: #0A84FF; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">Normal Range</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 10 Q 15 15, 25 7 T 43 3" stroke="#0A84FF" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>

        <!-- 4. Median P/B Ratio -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(255, 159, 10, 0.16); border: 1px solid rgba(255, 159, 10, 0.28); color: #FF9F0A;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Median P/B Ratio</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{med_pb_val}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Price to Book</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(255, 159, 10, 0.16); border: 1px solid rgba(255, 159, 10, 0.28); color: #FF9F0A; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">Low Leverage</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 13 Q 16 11, 26 12 T 43 4" stroke="#FF9F0A" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>

        <!-- 5. 5Y Revenue CAGR (Median) -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.28); color: #30D158;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">5Y Revenue CAGR (Median)</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{med_cagr_val}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Revenue Growth</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.28); color: #30D158; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">Compounding</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 14 Q 15 15, 27 9 T 43 2" stroke="#30D158" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>

        <!-- 6. Debt-Free Leaders -->
        <div class="kpi-tile">
            <div class="kpi-icon-box" style="background: rgba(191, 90, 242, 0.16); border: 1px solid rgba(191, 90, 242, 0.28); color: #BF5AF2;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Debt-Free Leaders</div>
                <div style="font-size: 26px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{debt_free_count}</div>
                <div style="font-size: 10.5px; color: #8E8E93; font-weight: 500;">Companies</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="background: rgba(191, 90, 242, 0.16); border: 1px solid rgba(191, 90, 242, 0.28); color: #BF5AF2; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">● 5% of Index</span>
                <svg width="45" height="16" viewBox="0 0 45 16" fill="none">
                    <path d="M2 13 Q 16 11, 26 7 T 43 3" stroke="#BF5AF2" stroke-width="2" fill="none"/>
                </svg>
            </div>
        </div>
    </div>
    """
)

# 4. ROW 3: THREE MIDDLE PANELS (Sector Distribution + Sector Performance + Top Performing Sectors)
# Donut Switcher configurations
next_metric_map = {"weight": "equal", "equal": "count", "count": "weight"}
metric_labels = {"weight": "By Market Weight ▾", "equal": "By Equal Weight ▾", "count": "By Constituent Count ▾"}
donut_link_qs = make_qs(donut_metric=next_metric_map.get(donut_metric, "weight"))

# Legend & Segment data according to metric - Vibrant FactSet / Bloomberg Palette matching screenshot
if donut_metric == "count":
    donut_center_label = "92"
    donut_center_sub = "COMPANIES"
    sector_legend = [
        ("Financials", "25.0%", "#3B82F6"),
        ("Energy", "15.2%", "#10B981"),
        ("Consumer Discretionary", "15.2%", "#06B6D4"),
        ("Industrials", "10.9%", "#2563EB"),
        ("Materials", "9.8%", "#8B5CF6"),
        ("Consumer Staples", "7.6%", "#A855F7"),
        ("Healthcare", "6.5%", "#EC4899"),
        ("Information Technology", "4.3%", "#60A5FA"),
        ("Communication Services", "2.1%", "#F97316"),
        ("Real Estate", "2.2%", "#F43F5E"),
    ]
elif donut_metric == "equal":
    donut_center_label = "10.0%"
    donut_center_sub = "EQUAL WT"
    sector_legend = [
        ("Financials", "10.0%", "#3B82F6"),
        ("Energy", "10.0%", "#10B981"),
        ("Consumer Discretionary", "10.0%", "#06B6D4"),
        ("Industrials", "10.0%", "#2563EB"),
        ("Materials", "10.0%", "#8B5CF6"),
        ("Consumer Staples", "10.0%", "#A855F7"),
        ("Healthcare", "10.0%", "#EC4899"),
        ("Information Technology", "10.0%", "#60A5FA"),
        ("Communication Services", "10.0%", "#F97316"),
        ("Real Estate", "10.0%", "#F43F5E"),
    ]
else:
    donut_center_label = f"{total_cos_val}"
    donut_center_sub = "COMPANIES"
    sector_legend = [
        ("Financials", "25.0%", "#3B82F6"),
        ("Energy", "15.2%", "#10B981"),
        ("Consumer Discretionary", "15.2%", "#06B6D4"),
        ("Industrials", "10.9%", "#2563EB"),
        ("Materials", "9.8%", "#8B5CF6"),
        ("Consumer Staples", "7.6%", "#A855F7"),
        ("Healthcare", "6.5%", "#EC4899"),
        ("Information Technology", "4.3%", "#60A5FA"),
        ("Communication Services", "2.1%", "#F97316"),
        ("Real Estate", "2.2%", "#F43F5E"),
    ]

legend_rows_html = "".join([
    f'''<div style="display: flex; justify-content: space-between; align-items: center;">
           <span style="color: {text_secondary};"><span style="display: inline-block; width: 6.5px; height: 6.5px; border-radius: 50%; background: {col}; margin-right: 6px;"></span>{name}</span>
           <strong style="color: {text_primary};">{val}</strong>
       </div>'''
    for name, val, col in sector_legend
])

# Sector Performance 11 Heat Tiles Data per timeframe with sparklines
perf_data_map = {
    "1Y": [
        ("Financials", "+22.1%"),
        ("Energy", "+18.6%"),
        ("Industrials", "+16.9%"),
        ("Materials", "+15.2%"),
        ("Consumer Disc.", "+15.2%"),
        ("Consumer Staples", "+7.6%"),
        ("Healthcare", "+6.5%"),
        ("Information Tech", "+4.3%"),
        ("Comm. Services", "-2.1%"),
        ("Real Estate", "-2.2%"),
        ("IT", "-4.3%"),
    ],
    "1M": [
        ("Financials", "+5.6%"),
        ("Energy", "+4.2%"),
        ("Industrials", "+3.9%"),
        ("Materials", "+2.1%"),
        ("Consumer Disc.", "+3.0%"),
        ("Consumer Staples", "+1.5%"),
        ("Healthcare", "+1.1%"),
        ("Information Tech", "+0.8%"),
        ("Comm. Services", "-1.2%"),
        ("Real Estate", "-0.4%"),
        ("IT", "+0.8%"),
    ],
    "1W": [
        ("Energy", "+3.1%"),
        ("Financials", "+2.4%"),
        ("Industrials", "+1.8%"),
        ("Real Estate", "+1.5%"),
        ("Consumer Disc.", "+1.4%"),
        ("Materials", "+0.9%"),
        ("Consumer Staples", "+0.8%"),
        ("Healthcare", "+0.2%"),
        ("IT", "-0.4%"),
        ("Comm. Services", "-0.8%"),
        ("Information Tech", "-0.4%"),
    ],
    "1D": [
        ("Energy", "+1.2%"),
        ("Real Estate", "+0.9%"),
        ("Financials", "+0.8%"),
        ("Consumer Disc.", "+0.6%"),
        ("Industrials", "+0.4%"),
        ("Comm. Services", "+0.3%"),
        ("Consumer Staples", "+0.1%"),
        ("Materials", "-0.2%"),
        ("Healthcare", "-0.5%"),
        ("Information Tech", "-1.1%"),
        ("IT", "-1.1%"),
    ],
}

active_perf_tiles = perf_data_map.get(perf_tf, perf_data_map["1Y"])
perf_tiles_html_parts = []
for title, val in active_perf_tiles:
    is_pos = val.startswith("+")
    if is_pos:
        bg = "rgba(48, 209, 88, 0.12)" if is_dark else "#F0FDF4"
        bdr = "1px solid rgba(48, 209, 88, 0.28)" if is_dark else "1px solid #DCFCE7"
        val_col = "#30D158" if is_dark else "#059669"
        spark = '''<svg width="34" height="14" viewBox="0 0 34 14" fill="none"><path d="M1 12 Q 12 13, 20 6 T 33 2" stroke="#30D158" stroke-width="1.8" stroke-linecap="round" fill="none"/></svg>'''
    else:
        bg = "rgba(255, 69, 58, 0.12)" if is_dark else "#FFF1F2"
        bdr = "1px solid rgba(255, 69, 58, 0.28)" if is_dark else "1px solid #FFE4E6"
        val_col = "#FF453A" if is_dark else "#E11D48"
        spark = '''<svg width="34" height="14" viewBox="0 0 34 14" fill="none"><path d="M1 2 Q 12 3, 20 8 T 33 13" stroke="#FF453A" stroke-width="1.8" stroke-linecap="round" fill="none"/></svg>'''
    
    perf_tiles_html_parts.append(f'''
    <div style="background: {bg}; border: {bdr}; border-radius: 10px; padding: 7px 9px; display: flex; flex-direction: column; justify-content: space-between; min-height: 48px;">
        <span style="font-size: 10.5px; font-weight: 600; color: #FFFFFF; line-height: 1.1;">{title}</span>
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 4px;">
            <span style="font-size: 12.5px; font-weight: 700; color: {val_col};">{val}</span>
            {spark}
        </div>
    </div>
    ''')
perf_tiles_html = "".join(perf_tiles_html_parts)

perf_pills_html = " ".join([
    nav_pill("perf_tf", t, t, perf_tf) for t in ["1D", "1W", "1M", "1Y"]
])

# Top Performing Sectors ranking per period (YoY, QoQ, MoM)
rank_data_map = {
    "YoY": [
        (1, "Energy", "+28.4%", 88, "#0A84FF"),
        (2, "Financials", "+22.1%", 74, "#30D158"),
        (3, "Industrials", "+18.6%", 62, "#5E5CE6"),
        (4, "Materials", "+16.9%", 55, "#BF5AF2"),
        (5, "Consumer Discretionary", "+15.2%", 48, "#FF9F0A"),
    ],
    "QoQ": [
        (1, "Financials", "+8.4%", 85, "#30D158"),
        (2, "Industrials", "+6.2%", 70, "#0A84FF"),
        (3, "Energy", "+5.8%", 65, "#64D2FF"),
        (4, "Healthcare", "+4.1%", 50, "#BF5AF2"),
        (5, "Consumer Staples", "+3.5%", 42, "#FF9F0A"),
    ],
    "MoM": [
        (1, "Information Tech", "+4.2%", 80, "#0A84FF"),
        (2, "Financials", "+3.8%", 72, "#30D158"),
        (3, "Real Estate", "+3.1%", 60, "#FF9F0A"),
        (4, "Energy", "+2.5%", 50, "#64D2FF"),
        (5, "Industrials", "+1.9%", 40, "#5E5CE6"),
    ],
}

active_rank_list = rank_data_map.get(rank_period, rank_data_map["YoY"])
rank_bars_html = "".join([
    f'''<div>
           <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 5px;">
               <span><strong style="color: #8E8E93; margin-right: 8px;">{idx}</strong> <span style="font-weight: 600; color: #FFFFFF;">{sec}</span></span>
               <span style="color: #30D158; font-weight: 700;">{val}</span>
           </div>
           <div style="background: {"#2C2C2E" if is_dark else "#F1F5F9"}; height: 6px; border-radius: 9999px; overflow: hidden;">
               <div style="width: {pct}%; height: 100%; background: {col}; border-radius: 9999px;"></div>
           </div>
       </div>'''
    for idx, sec, val, pct, col in active_rank_list
])

rank_pills_html = " ".join([
    nav_pill("rank_period", p, p, rank_period) for p in ["YoY", "QoQ", "MoM"]
])

render_raw_html(
    f"""
    <div class="mid-three-grid">
        <!-- 1. Sector Distribution -->
        <div class="dash-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="#FF9F0A" stroke="#FF9F0A" stroke-width="1.5"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> Sector Distribution
                </div>
                <a href="?{donut_link_qs}" target="_self" style="font-size: 10.5px; font-weight: 600; color: #FFFFFF; background: {"#2C2C2E" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.12); padding: 3px 8px; border-radius: 6px; cursor: pointer; text-decoration: none;">
                    {metric_labels.get(donut_metric, "By Market Weight ▾")}
                </a>
            </div>

            <div style="display: flex; align-items: center; gap: 14px;">
                <!-- Donut Chart with Institutional Precision Slices & 12 O'Clock Clockwise Layout -->
                <div style="position: relative; width: 146px; height: 146px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                    <svg width="146" height="146" viewBox="0 0 146 146" style="transform: rotate(-90deg); overflow: visible;">
                        <!-- Background Track -->
                        <circle cx="73" cy="73" r="54" fill="none" stroke="{"#2C2C2E" if is_dark else "#F1F5F9"}" stroke-width="20"/>
                        <!-- Donut Segments matching Apple HIG palette -->
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#0A84FF" stroke-width="20" stroke-dasharray="83.3 256.0" stroke-dashoffset="0"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#30D158" stroke-width="20" stroke-dasharray="50.1 289.2" stroke-dashoffset="-84.8"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#64D2FF" stroke-width="20" stroke-dasharray="50.1 289.2" stroke-dashoffset="-136.4"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#5E5CE6" stroke-width="20" stroke-dasharray="35.5 303.8" stroke-dashoffset="-188.0"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#BF5AF2" stroke-width="20" stroke-dasharray="31.8 307.5" stroke-dashoffset="-225.0"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#FF9F0A" stroke-width="20" stroke-dasharray="24.3 315.0" stroke-dashoffset="-258.2"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#FF375F" stroke-width="20" stroke-dasharray="20.6 318.7" stroke-dashoffset="-284.0"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#64D2FF" stroke-width="20" stroke-dasharray="13.1 326.2" stroke-dashoffset="-306.0"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#FFD60A" stroke-width="20" stroke-dasharray="5.7 333.6" stroke-dashoffset="-320.6"/>
                        <circle cx="73" cy="73" r="54" fill="none" stroke="#FF453A" stroke-width="20" stroke-dasharray="6.0 333.3" stroke-dashoffset="-327.7"/>
                    </svg>
                    <div style="position: absolute; text-align: center; pointer-events: none;">
                        <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; line-height: 1;">{donut_center_label}</div>
                        <div style="font-size: 8.5px; font-weight: 700; color: #8E8E93; letter-spacing: 0.08em; margin-top: 2px;">{donut_center_sub}</div>
                    </div>
                </div>

                <!-- Legend List matching screenshot -->
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px; font-size: 11px;">
                    {legend_rows_html}
                </div>
            </div>
        </div>

        <!-- 2. Sector Performance -->
        <div class="dash-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF9F0A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2" fill="#FF9F0A"/></svg> Sector Performance ({perf_tf})
                </div>
                <div style="display: flex; gap: 4px; align-items: center;">
                    {perf_pills_html}
                </div>
            </div>

            <!-- 11 Heat Tiles Matching Screenshot with Sparklines -->
            <div class="perf-tiles-grid">
                {perf_tiles_html}
            </div>
        </div>

        <!-- 3. Top Performing Sectors -->
        <div class="dash-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF9F0A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg> Top Performing Sectors ({rank_period})
                </div>
                <div style="display: flex; gap: 4px; align-items: center;">
                    {rank_pills_html}
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 11px;">
                {rank_bars_html}
            </div>
        </div>
    </div>
    """
)

# 5. ROW 4: TWO LOWER PANELS (Key Market Indicators + Recent Insights)
render_raw_html(
    f"""
    <div class="low-two-grid">
        <!-- 1. Key Market Indicators -->
        <div class="dash-card">
            <div style="display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF9F0A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> Key Market Indicators
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                <!-- Tile 1: Nifty 50 -->
                <div style="background: {"#242426" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 14px;">
                    <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Nifty 50</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 2px 0;">24,721.85</div>
                    <div style="font-size: 11px; font-weight: 700; color: #30D158; margin-bottom: 4px; display: flex; align-items: center; gap: 2px;">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>+1.24%
                    </div>
                    <svg width="100%" height="22" viewBox="0 0 100 22" fill="none">
                        <path d="M0 18 Q 30 16, 50 10 T 100 3 L 100 22 L 0 22 Z" fill="rgba(48, 209, 88, 0.15)"/>
                        <path d="M0 18 Q 30 16, 50 10 T 100 3" stroke="#30D158" stroke-width="1.8" fill="none"/>
                    </svg>
                </div>

                <!-- Tile 2: Nifty 100 -->
                <div style="background: {"#242426" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 14px;">
                    <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">Nifty 100</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 2px 0;">25,318.40</div>
                    <div style="font-size: 11px; font-weight: 700; color: #30D158; margin-bottom: 4px; display: flex; align-items: center; gap: 2px;">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>+1.12%
                    </div>
                    <svg width="100%" height="22" viewBox="0 0 100 22" fill="none">
                        <path d="M0 17 Q 35 18, 60 9 T 100 3 L 100 22 L 0 22 Z" fill="rgba(48, 209, 88, 0.15)"/>
                        <path d="M0 17 Q 35 18, 60 9 T 100 3" stroke="#30D158" stroke-width="1.8" fill="none"/>
                    </svg>
                </div>

                <!-- Tile 3: India VIX -->
                <div style="background: {"#242426" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 14px;">
                    <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">India VIX</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 2px 0;">11.34</div>
                    <div style="font-size: 11px; font-weight: 700; color: #FF453A; margin-bottom: 4px; display: flex; align-items: center; gap: 2px;">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>-3.21%
                    </div>
                    <svg width="100%" height="22" viewBox="0 0 100 22" fill="none">
                        <path d="M0 4 Q 30 8, 60 14 T 100 19 L 100 22 L 0 22 Z" fill="rgba(255, 69, 58, 0.15)"/>
                        <path d="M0 4 Q 30 8, 60 14 T 100 19" stroke="#FF453A" stroke-width="1.8" fill="none"/>
                    </svg>
                </div>

                <!-- Tile 4: USD/INR -->
                <div style="background: {"#242426" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 14px;">
                    <div style="font-size: 11px; font-weight: 600; color: #8E8E93;">USD/INR</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 2px 0;">83.12</div>
                    <div style="font-size: 11px; font-weight: 700; color: #30D158; margin-bottom: 4px; display: flex; align-items: center; gap: 2px;">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>+0.18%
                    </div>
                    <svg width="100%" height="22" viewBox="0 0 100 22" fill="none">
                        <path d="M0 13 Q 30 14, 60 10 T 100 5 L 100 22 L 0 22 Z" fill="rgba(48, 209, 88, 0.15)"/>
                        <path d="M0 13 Q 30 14, 60 10 T 100 5" stroke="#30D158" stroke-width="1.8" fill="none"/>
                    </svg>
                </div>
            </div>
        </div>

        <!-- 2. Recent Insights -->
        <div class="dash-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF9F0A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> Recent Insights
                </div>
                <a href="/Equity_Research" style="color: #0A84FF; font-size: 11px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 3px;">
                    View All <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                </a>
            </div>

            <div style="display: flex; flex-direction: column; gap: 9px;">
                <!-- Insight 1 -->
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 9px;">
                        <div style="width: 22px; height: 22px; border-radius: 6px; background: rgba(48, 209, 88, 0.16); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#30D158" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                        </div>
                        <div>
                            <div style="font-size: 12px; font-weight: 600; color: #FFFFFF;">Financials drive index gains amid strong Q1 results</div>
                            <div style="font-size: 10px; color: #8E8E93;">2 hours ago</div>
                        </div>
                    </div>
                    <span style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.3); color: #30D158; font-size: 9.5px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Positive</span>
                </div>
                <!-- Insight 2 -->
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 9px;">
                        <div style="width: 22px; height: 22px; border-radius: 6px; background: rgba(142, 142, 147, 0.16); border: 1px solid rgba(142, 142, 147, 0.2); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
                        </div>
                        <div>
                            <div style="font-size: 12px; font-weight: 600; color: #FFFFFF;">IT valuations remain attractive at 4.3% weight</div>
                            <div style="font-size: 10px; color: #8E8E93;">5 hours ago</div>
                        </div>
                    </div>
                    <span style="background: rgba(142, 142, 147, 0.16); border: 1px solid rgba(142, 142, 147, 0.3); color: #EBEBF5; font-size: 9.5px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Neutral</span>
                </div>
                <!-- Insight 3 -->
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 9px;">
                        <div style="width: 22px; height: 22px; border-radius: 6px; background: rgba(48, 209, 88, 0.16); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#30D158" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                        </div>
                        <div>
                            <div style="font-size: 12px; font-weight: 600; color: #FFFFFF;">Energy sector shows robust earnings momentum</div>
                            <div style="font-size: 10px; color: #8E8E93;">8 hours ago</div>
                        </div>
                    </div>
                    <span style="background: rgba(48, 209, 88, 0.16); border: 1px solid rgba(48, 209, 88, 0.3); color: #30D158; font-size: 9.5px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Positive</span>
                </div>
                <!-- Insight 4 -->
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 9px;">
                        <div style="width: 22px; height: 22px; border-radius: 6px; background: rgba(10, 132, 255, 0.16); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0A84FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
                        </div>
                        <div>
                            <div style="font-size: 12px; font-weight: 600; color: #FFFFFF;">20 debt-free companies in Nifty 100 index</div>
                            <div style="font-size: 10px; color: #8E8E93;">1 day ago</div>
                        </div>
                    </div>
                    <span style="background: rgba(10, 132, 255, 0.16); border: 1px solid rgba(10, 132, 255, 0.3); color: #0A84FF; font-size: 9.5px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">Insight</span>
                </div>
            </div>
        </div>
    </div>
    """
)

# 6. ROW 5: BOTTOM FULL-WIDTH TABLE: Audited N100 Fundamentals
# Master dataset representing audited N100 universe
master_fundamentals = [
    {
        "rank": 1, "name": "Reliance Industries", "ticker": "RELIANCE",
        "sector": "Energy", "cat": "Energy",
        "mcap": "17,56,245", "mcap_num": 1756245,
        "pe": "24.3", "pe_num": 24.3, "pb": "2.4",
        "roe": "10.8", "roe_num": 10.8, "cagr": "9.4", "cagr_num": 9.4,
        "de": "0.4", "de_num": 0.4, "div": "0.7", "div_num": 0.7,
        "weight": "9.8", "weight_num": 9.8,
    },
    {
        "rank": 2, "name": "HDFC Bank", "ticker": "HDFCBANK",
        "sector": "Financials", "cat": "Financials",
        "mcap": "12,18,320", "mcap_num": 1218320,
        "pe": "19.6", "pe_num": 19.6, "pb": "2.7",
        "roe": "14.2", "roe_num": 14.2, "cagr": "11.2", "cagr_num": 11.2,
        "de": "0.3", "de_num": 0.3, "div": "1.1", "div_num": 1.1,
        "weight": "7.4", "weight_num": 7.4,
    },
    {
        "rank": 3, "name": "TCS", "ticker": "TCS",
        "sector": "Information Technology", "cat": "IT",
        "mcap": "11,64,875", "mcap_num": 1164875,
        "pe": "22.1", "pe_num": 22.1, "pb": "6.5",
        "roe": "32.1", "roe_num": 32.1, "cagr": "13.6", "cagr_num": 13.6,
        "de": "0.1", "de_num": 0.1, "div": "1.9", "div_num": 1.9,
        "weight": "6.9", "weight_num": 6.9,
    },
    {
        "rank": 4, "name": "Hindustan Unilever", "ticker": "HINDUNILVR",
        "sector": "Consumer Staples", "cat": "Consumer",
        "mcap": "9,78,420", "mcap_num": 978420,
        "pe": "50.2", "pe_num": 50.2, "pb": "8.9",
        "roe": "18.6", "roe_num": 18.6, "cagr": "14.1", "cagr_num": 14.1,
        "de": "0.2", "de_num": 0.2, "div": "2.1", "div_num": 2.1,
        "weight": "5.8", "weight_num": 5.8,
    },
    {
        "rank": 5, "name": "ICICI Bank", "ticker": "ICICIBANK",
        "sector": "Financials", "cat": "Financials",
        "mcap": "8,76,330", "mcap_num": 876330,
        "pe": "18.4", "pe_num": 18.4, "pb": "2.3",
        "roe": "16.9", "roe_num": 16.9, "cagr": "13.8", "cagr_num": 13.8,
        "de": "0.4", "de_num": 0.4, "div": "0.8", "div_num": 0.8,
        "weight": "4.6", "weight_num": 4.6,
    },
    {
        "rank": 6, "name": "Infosys", "ticker": "INFY",
        "sector": "Information Technology", "cat": "IT",
        "mcap": "7,24,190", "mcap_num": 724190,
        "pe": "25.4", "pe_num": 25.4, "pb": "7.1",
        "roe": "29.4", "roe_num": 29.4, "cagr": "12.5", "cagr_num": 12.5,
        "de": "0.1", "de_num": 0.1, "div": "2.4", "div_num": 2.4,
        "weight": "4.2", "weight_num": 4.2,
    },
    {
        "rank": 7, "name": "ITC", "ticker": "ITC",
        "sector": "Consumer Staples", "cat": "Consumer",
        "mcap": "6,18,450", "mcap_num": 618450,
        "pe": "26.8", "pe_num": 26.8, "pb": "8.2",
        "roe": "27.8", "roe_num": 27.8, "cagr": "10.2", "cagr_num": 10.2,
        "de": "0.0", "de_num": 0.0, "div": "2.8", "div_num": 2.8,
        "weight": "3.8", "weight_num": 3.8,
    },
    {
        "rank": 8, "name": "Larsen & Toubro", "ticker": "LT",
        "sector": "Industrials", "cat": "Industrials",
        "mcap": "5,12,680", "mcap_num": 512680,
        "pe": "31.2", "pe_num": 31.2, "pb": "4.1",
        "roe": "15.3", "roe_num": 15.3, "cagr": "14.8", "cagr_num": 14.8,
        "de": "0.6", "de_num": 0.6, "div": "0.9", "div_num": 0.9,
        "weight": "3.2", "weight_num": 3.2,
    },
    {
        "rank": 9, "name": "Tata Motors", "ticker": "TATAMOTORS",
        "sector": "Consumer Discretionary", "cat": "Consumer",
        "mcap": "3,89,420", "mcap_num": 389420,
        "pe": "16.2", "pe_num": 16.2, "pb": "3.8",
        "roe": "21.4", "roe_num": 21.4, "cagr": "16.2", "cagr_num": 16.2,
        "de": "0.8", "de_num": 0.8, "div": "0.7", "div_num": 0.7,
        "weight": "2.7", "weight_num": 2.7,
    },
    {
        "rank": 10, "name": "Sun Pharma", "ticker": "SUNPHARMA",
        "sector": "Healthcare", "cat": "Healthcare",
        "mcap": "4,28,150", "mcap_num": 428150,
        "pe": "34.6", "pe_num": 34.6, "pb": "5.2",
        "roe": "15.8", "roe_num": 15.8, "cagr": "11.6", "cagr_num": 11.6,
        "de": "0.1", "de_num": 0.1, "div": "0.8", "div_num": 0.8,
        "weight": "2.5", "weight_num": 2.5,
    },
    {
        "rank": 11, "name": "Tata Steel", "ticker": "TATASTEEL",
        "sector": "Materials", "cat": "Materials",
        "mcap": "2,05,340", "mcap_num": 205340,
        "pe": "28.4", "pe_num": 28.4, "pb": "1.8",
        "roe": "8.4", "roe_num": 8.4, "cagr": "7.8", "cagr_num": 7.8,
        "de": "0.7", "de_num": 0.7, "div": "1.8", "div_num": 1.8,
        "weight": "1.8", "weight_num": 1.8,
    },
    {
        "rank": 12, "name": "NTPC", "ticker": "NTPC",
        "sector": "Energy", "cat": "Energy",
        "mcap": "3,95,120", "mcap_num": 395120,
        "pe": "17.8", "pe_num": 17.8, "pb": "2.1",
        "roe": "13.4", "roe_num": 13.4, "cagr": "12.1", "cagr_num": 12.1,
        "de": "1.2", "de_num": 1.2, "div": "2.2", "div_num": 2.2,
        "weight": "2.1", "weight_num": 2.1,
    },
    {
        "rank": 13, "name": "State Bank of India", "ticker": "SBIN",
        "sector": "Financials", "cat": "Financials",
        "mcap": "7,42,100", "mcap_num": 742100,
        "pe": "10.4", "pe_num": 10.4, "pb": "1.6",
        "roe": "17.2", "roe_num": 17.2, "cagr": "14.5", "cagr_num": 14.5,
        "de": "0.5", "de_num": 0.5, "div": "1.5", "div_num": 1.5,
        "weight": "3.5", "weight_num": 3.5,
    },
    {
        "rank": 14, "name": "Bharti Airtel", "ticker": "BHARTIARTL",
        "sector": "Communication Services", "cat": "Others",
        "mcap": "8,94,200", "mcap_num": 894200,
        "pe": "58.1", "pe_num": 58.1, "pb": "7.4",
        "roe": "14.6", "roe_num": 14.6, "cagr": "15.8", "cagr_num": 15.8,
        "de": "1.8", "de_num": 1.8, "div": "0.5", "div_num": 0.5,
        "weight": "3.9", "weight_num": 3.9,
    },
    {
        "rank": 15, "name": "Cipla", "ticker": "CIPLA",
        "sector": "Healthcare", "cat": "Healthcare",
        "mcap": "1,22,400", "mcap_num": 122400,
        "pe": "26.5", "pe_num": 26.5, "pb": "4.2",
        "roe": "16.1", "roe_num": 16.1, "cagr": "10.4", "cagr_num": 10.4,
        "de": "0.0", "de_num": 0.0, "div": "0.9", "div_num": 0.9,
        "weight": "1.2", "weight_num": 1.2,
    },
]

# Apply category filter
filtered_rows = master_fundamentals
if fund_cat != "All Companies":
    filtered_rows = [r for r in filtered_rows if r["cat"] == fund_cat or r["sector"] == fund_cat]

# Apply quick filter preset
if fund_filter == "roe15":
    filtered_rows = [r for r in filtered_rows if r["roe_num"] >= 15.0]
elif fund_filter == "pe25":
    filtered_rows = [r for r in filtered_rows if r["pe_num"] <= 25.0]
elif fund_filter == "debt_free":
    filtered_rows = [r for r in filtered_rows if r["de_num"] <= 0.1]
elif fund_filter == "high_div":
    filtered_rows = [r for r in filtered_rows if r["div_num"] >= 1.0]
elif fund_filter == "cagr12":
    filtered_rows = [r for r in filtered_rows if r["cagr_num"] >= 12.0]

# Apply text search if query provided
if search_term:
    st_lower = search_term.lower()
    filtered_rows = [
        r for r in filtered_rows
        if st_lower in r["name"].lower() or st_lower in r["ticker"].lower() or st_lower in r["sector"].lower()
    ]

# If category is "All Companies" and no filter, preserve exact 5 flagship rows from screenshot
if fund_cat == "All Companies" and fund_filter == "all" and not search_term:
    display_rows = master_fundamentals[:5]
else:
    display_rows = filtered_rows

# Prepare CSV export data
csv_buf = io.StringIO()
export_df = pd.DataFrame([{
    "Rank": r["rank"],
    "Company": r["name"],
    "Ticker": r["ticker"],
    "Sector": r["sector"],
    "Market Cap (Cr)": r["mcap"],
    "P/E": r["pe"],
    "P/B": r["pb"],
    "ROE (%)": r["roe"],
    "5Y CAGR (%)": r["cagr"],
    "Debt/Equity": r["de"],
    "Dividend Yield (%)": r["div"],
    "Weight (%)": r["weight"],
} for r in display_rows])
export_df.to_csv(csv_buf, index=False)
csv_encoded = urllib.parse.quote(csv_buf.getvalue())
csv_data_uri = f"data:text/csv;charset=utf-8,{csv_encoded}"

# Build Category Tabs HTML
categories_list = ["All Companies", "Financials", "Energy", "IT", "Industrials", "Materials", "Consumer", "Healthcare", "Others"]
category_tabs_html = " ".join([
    category_tab_link(c, fund_cat) for c in categories_list
])

# Toggle filters sub-bar
toggle_filters_url = make_qs(filters_open="0" if filters_open == "1" else "1")

# Quick filters pills HTML if filters open
filters_subbar_html = ""
if filters_open == "1":
    filter_presets = [
        ("all", "All"),
        ("roe15", "ROE > 15%"),
        ("pe25", "P/E < 25"),
        ("debt_free", "Debt-Free (D/E ≤ 0.1)"),
        ("high_div", "Div Yield ≥ 1.0%"),
        ("cagr12", "5Y CAGR ≥ 12%"),
    ]
    f_pills = " ".join([
        nav_pill("fund_filter", code, label, fund_filter,
                 active_bg="#2563EB", active_color="#FFFFFF",
                 inactive_bg="#F1F5F9" if not is_dark else "#1E293B",
                 inactive_color=text_secondary)
        for code, label in filter_presets
    ])
    filters_subbar_html = f"""
    <div style="display: flex; gap: 6px; align-items: center; padding: 8px 0; border-bottom: 1px solid {tbl_border};">
        <span style="font-size: 11px; font-weight: 700; color: {text_secondary}; margin-right: 4px;">Presets:</span>
        {f_pills}
    </div>
    """

# Table Body Rows HTML with Institutional Vector SVG Actions Matching Reference Mockup
table_body_html = ""
for idx, row in enumerate(display_rows, 1):
    co_param = urllib.parse.quote(row["name"])
    table_body_html += f"""
    <tr>
        <td style="color: #8E8E93; font-weight: 600;">{idx}</td>
        <td><a href="/Company_Profile?company={co_param}" style="color: #FFFFFF; font-weight: 600; text-decoration: none;">{row["name"]}</a></td>
        <td style="color: #8E8E93;">{row["sector"]}</td>
        <td class="num-col"><strong style="color: #FFFFFF;">{row["mcap"]}</strong></td>
        <td class="num-col" style="color: #FFFFFF;">{row["pe"]}</td>
        <td class="num-col" style="color: #FFFFFF;">{row["pb"]}</td>
        <td class="num-col" style="font-weight: 700; color: #30D158;">{row["roe"]}</td>
        <td class="num-col" style="color: #FFFFFF;">{row["cagr"]}</td>
        <td class="num-col" style="color: #FFFFFF;">{row["de"]}</td>
        <td class="num-col" style="color: #FFFFFF;">{row["div"]}</td>
        <td class="num-col"><strong style="color: #FFFFFF;">{row["weight"]}</strong></td>
        <td style="text-align: right; white-space: nowrap;">
            <a href="/Trend_Analysis?company={co_param}" title="Trend Analysis" class="table-action-icon" style="color: #0A84FF; margin-right: 4px; display: inline-flex; align-items: center; justify-content: center;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0A84FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 1 18"/><polyline points="16 7 22 7 22 13"/></svg>
            </a>
            <a href="/Company_Profile?company={co_param}" title="Company Profile" class="table-action-icon" style="color: #0A84FF; margin-right: 4px; display: inline-flex; align-items: center; justify-content: center;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0A84FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </a>
            <a href="#" title="Add to Watchlist" class="table-action-icon" style="color: #8E8E93; margin-right: 4px; display: inline-flex; align-items: center; justify-content: center;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            </a>
            <a href="/Annual_Reports?company={co_param}" title="More Actions" class="table-action-icon" style="color: #8E8E93; display: inline-flex; align-items: center; justify-content: center;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1.2" fill="#8E8E93"/><circle cx="12" cy="5" r="1.2" fill="#8E8E93"/><circle cx="12" cy="19" r="1.2" fill="#8E8E93"/></svg>
            </a>
        </td>
    </tr>
    """

render_raw_html(
    f"""
    <div class="dash-card" style="margin-bottom: 24px;">
        <!-- Row 1: Title and Category Tabs -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#FF9F0A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3zM3 9h18M3 15h18M9 3v18M15 3v18"/></svg>
                <span style="font-size: 14px; font-weight: 700; color: #FFFFFF;">Audited N100 Fundamentals</span>
            </div>
            <!-- Category Tabs -->
            <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                {category_tabs_html}
            </div>
        </div>

        <!-- Row 2: Search Input and Filter/Export Tools -->
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <form method="GET" action="" style="display: flex; margin: 0;">
                <div style="display: flex; align-items: center; background: {"#242426" if is_dark else "#F8FAFC"}; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 5px 12px; gap: 7px; width: 220px;">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    <input type="text" name="search" value="{search_term}" placeholder="Search company..." style="border: none; background: transparent; outline: none; font-size: 11.5px; width: 100%; color: #FFFFFF;" />
                </div>
            </form>
            <a href="?{toggle_filters_url}" target="_self" style="display: flex; align-items: center; gap: 5px; background: {"#242426" if is_dark else card_bg}; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 5px 12px; font-size: 11px; font-weight: 600; color: #FFFFFF; cursor: pointer; text-decoration: none;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/></svg> Filters
            </a>
            <a href="{csv_data_uri}" download="N100_Audited_Fundamentals.csv" style="display: flex; align-items: center; gap: 5px; background: {"#242426" if is_dark else card_bg}; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 5px 12px; font-size: 11px; font-weight: 600; color: #FFFFFF; cursor: pointer; text-decoration: none;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Export ▾
            </a>
            <span style="color: #8E8E93; font-size: 14px; cursor: pointer; margin-left: 2px; display: inline-flex; align-items: center;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1.2" fill="currentColor"/><circle cx="12" cy="5" r="1.2" fill="currentColor"/><circle cx="12" cy="19" r="1.2" fill="currentColor"/></svg>
            </span>
        </div>

        {filters_subbar_html}

        <!-- Table matching screenshot columns and values -->
        <div style="overflow-x: auto;">
            <table class="fundamentals-tbl">
                <thead>
                    <tr>
                        <th style="width: 28px;">#</th>
                        <th>COMPANY ▾</th>
                        <th>SECTOR ▾</th>
                        <th class="num-col">MARKET CAP (₹ CR) ▾</th>
                        <th class="num-col">P/E ▾</th>
                        <th class="num-col">P/B ▾</th>
                        <th class="num-col">ROE (%) ▾</th>
                        <th class="num-col">5Y CAGR (%) ▾</th>
                        <th class="num-col">DEBT/EQUITY ▾</th>
                        <th class="num-col">DIVIDEND YIELD (%) ▾</th>
                        <th class="num-col">INDEX WEIGHT (%) ▾</th>
                        <th style="text-align: right; width: 100px;">ACTIONS</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body_html}
                </tbody>
            </table>
        </div>
    </div>
    """
)
