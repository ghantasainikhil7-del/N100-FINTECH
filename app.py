"""N100 Financial Intelligence Platform - Master SPA Application Entrypoint."""
from __future__ import annotations

import os
import sys
import runpy
import warnings
from pathlib import Path

# Ensure project root and src are in sys.path
_cur = Path(__file__).resolve()
_root = None
for _p in [_cur.parent, _cur.parent.parent, _cur.parent.parent.parent]:
    if (_p / "src").is_dir():
        _root = _p
        break
if _root is None:
    _root = Path.cwd().resolve()

for _p in [str(_cur.parent), str(_root / "src"), str(_root)]:
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*use_container_width.*")

import streamlit as st
from src.dashboard.utils.theme import inject_theme_css, render_sidebar

# Configure Streamlit page layout
try:
    st.set_page_config(
        page_title="N100 Financial Intelligence",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# Always inject dark Apple iOS institutional theme CSS
inject_theme_css()

# Read active page from query_params
def _get_active_page() -> str:
    try:
        if hasattr(st, "query_params"):
            p = st.query_params.get("page", "home")
            return str(p).strip().lower() if p else "home"
        elif hasattr(st, "experimental_get_query_params"):
            p = st.experimental_get_query_params().get("page", ["home"])
            return str(p[0]).strip().lower() if p else "home"
    except Exception:
        pass
    return "home"

active_page_key = _get_active_page()

# Canonical Page Routing Registry
PAGE_REGISTRY = {
    "home": ("01_home.py", "Home Overview"),
    "overview": ("01_home.py", "Home Overview"),
    "profile": ("02_profile.py", "Company Profile"),
    "company_profile": ("02_profile.py", "Company Profile"),
    "screener": ("03_screener.py", "Stock Screener"),
    "peers": ("04_peers.py", "Peer Comparison"),
    "trends": ("05_trends.py", "Trend Analysis"),
    "trend_analysis": ("05_trends.py", "Trend Analysis"),
    "sectors": ("06_sectors.py", "Sector Analysis"),
    "capital": ("07_capital.py", "Capital Allocation"),
    "reports": ("08_reports.py", "Annual Reports"),
    "annual_reports": ("08_reports.py", "Annual Reports"),
    "equity": ("02_profile.py", "Equity Research"),
    "equity_research": ("02_profile.py", "Equity Research"),
    "analytics": ("05_trends.py", "Advanced Analytics"),
    "advanced_analytics": ("05_trends.py", "Advanced Analytics"),
    "executive": ("01_home.py", "Executive Dashboard"),
    "executive_dashboards": ("01_home.py", "Executive Dashboard"),
    "react": ("09_react.py", "React Native Web App"),
    "react_app": ("09_react.py", "React Native Web App"),
}

target_file, target_title = PAGE_REGISTRY.get(active_page_key, ("01_home.py", "Home Overview"))

# Locate target page script
pages_dir = Path(__file__).resolve().parent / "src" / "dashboard" / "pages"
if not (pages_dir / target_file).exists():
    pages_dir = Path(__file__).resolve().parent / "pages"
target_path = pages_dir / target_file

# Render unified institutional sidebar once with the active screen indicator
with st.sidebar:
    render_sidebar(target_title)
st.session_state["_sidebar_rendered"] = True

# Execute the target screen inside the active Streamlit app
if target_path.exists():
    runpy.run_path(str(target_path), run_name="__main__")
else:
    st.error(f"Cannot find screen '{target_file}' at {target_path}")
