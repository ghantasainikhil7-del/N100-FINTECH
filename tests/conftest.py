import sys
from pathlib import Path

# Ensure project root is in sys.path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import sqlite3
import pytest
import pandas as pd


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database populated with schema.sql."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    with open("db/schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    yield conn
    conn.close()


@pytest.fixture
def sample_companies_df():
    """Sample DataFrame of companies."""
    return pd.DataFrame([
        {
            "id": "TCS",
            "company_logo": "https://assets.validstep.com/logos/TCS.png",
            "company_name": "Tata Consultancy Services Limited",
            "chart_link": "https://in.tradingview.com/chart/?symbol=NSE:TCS",
            "about_company": "TCS is a global leader in IT services.",
            "website": "https://www.tcs.com",
            "nse_profile": "https://www.nseindia.com/get-quotes/equity?symbol=TCS",
            "bse_profile": "https://www.bseindia.com/stock-share-price/tcs",
            "face_value": 1.0,
            "book_value": 250.0,
            "roce_percentage": 58.0,
            "roe_percentage": 46.0,
        },
        {
            "id": "INFY",
            "company_logo": "https://assets.validstep.com/logos/INFY.png",
            "company_name": "Infosys Limited",
            "chart_link": "https://in.tradingview.com/chart/?symbol=NSE:INFY",
            "about_company": "Infosys is a global leader in next-generation digital services.",
            "website": "https://www.infosys.com",
            "nse_profile": "https://www.nseindia.com/get-quotes/equity?symbol=INFY",
            "bse_profile": "https://www.bseindia.com/stock-share-price/infy",
            "face_value": 5.0,
            "book_value": 210.0,
            "roce_percentage": 42.0,
            "roe_percentage": 32.0,
        }
    ])
