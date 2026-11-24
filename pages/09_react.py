"""Direct Embedded React 18 Apple Native Stocks Web Interface inside Streamlit."""
from __future__ import annotations

import os
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Hide Streamlit default padding to make React full-screen
st.markdown(
    """
    <style>
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    iframe {
        width: 100% !important;
        height: 100vh !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Resolve path to standalone.html
_cur = Path(__file__).resolve()
_root = None
for _p in [_cur.parent, _cur.parent.parent, _cur.parent.parent.parent]:
    if (_p / "frontend" / "standalone.html").exists():
        _root = _p
        break
if _root is None:
    _root = Path.cwd().resolve()

html_path = _root / "frontend" / "standalone.html"
if html_path.exists():
    html_code = html_path.read_text(encoding="utf-8")
    components.html(html_code, height=950, scrolling=True)
else:
    st.error(f"Cannot locate React build at {html_path}")
