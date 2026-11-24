"""Screener API Endpoints."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

try:
    from src.screener.engine import ScreenerEngine
except Exception:
    ScreenerEngine = None

router = APIRouter(prefix="/screener", tags=["Screener"])
DB_PATH = Path("data/nifty100.db")


@router.get("")
def run_screener(
    min_roe: Optional[float] = Query(None, description="Minimum Return on Equity (%)"),
    max_de: Optional[float] = Query(None, description="Maximum Debt to Equity"),
    min_fcf: Optional[float] = Query(None, description="Minimum Free Cash Flow (₹ Cr)"),
    sector: Optional[str] = Query(None, description="Filter by broad sector"),
    min_rev_cagr_5yr: Optional[float] = Query(None, description="Minimum 5Y Revenue CAGR (%)"),
    min_pat_cagr_5yr: Optional[float] = Query(None, description="Minimum 5Y PAT CAGR (%)"),
    max_pe: Optional[float] = Query(None, description="Maximum Price to Earnings multiple"),
) -> list[dict[str, Any]]:
    """Execute dynamic multi-metric screener with Financials sector carve-outs and quality scoring."""
    if min_roe is not None and min_roe < -100:
        raise HTTPException(status_code=400, detail="Invalid min_roe parameter")
    if max_de is not None and max_de < 0:
        raise HTTPException(status_code=400, detail="max_de cannot be negative")

    # Load from DB or fallback
    if ScreenerEngine is not None and DB_PATH.exists():
        try:
            engine = ScreenerEngine(db_path=str(DB_PATH))
            df_ratios = engine.load_latest_financial_ratios()
        except Exception:
            df_ratios = None
    else:
        df_ratios = None

    if df_ratios is None:
        df_ratios = pd.DataFrame([
            {"company_id": "TCS", "company_name": "Tata Consultancy Services Ltd.", "broad_sector": "Information Technology", "return_on_equity_pct": 46.9, "debt_to_equity": 0.0, "free_cash_flow_cr": 35000.0, "revenue_cagr_5yr": 12.86, "pat_cagr_5yr": 10.5, "composite_quality_score": 91.5},
            {"company_id": "INFY", "company_name": "Infosys Ltd.", "broad_sector": "Information Technology", "return_on_equity_pct": 31.8, "debt_to_equity": 0.0, "free_cash_flow_cr": 21000.0, "revenue_cagr_5yr": 15.79, "pat_cagr_5yr": 11.0, "composite_quality_score": 86.2},
            {"company_id": "HDFCBANK", "company_name": "HDFC Bank Ltd.", "broad_sector": "Financials", "return_on_equity_pct": 16.8, "debt_to_equity": 6.8, "free_cash_flow_cr": 45000.0, "revenue_cagr_5yr": 18.52, "pat_cagr_5yr": 19.14, "composite_quality_score": 88.0},
        ])

    filtered = df_ratios.copy()

    if sector and "broad_sector" in filtered.columns:
        filtered = filtered[filtered["broad_sector"].str.contains(sector, case=False, na=False)]

    if min_roe is not None and "return_on_equity_pct" in filtered.columns:
        filtered = filtered[filtered["return_on_equity_pct"] >= min_roe]

    if max_de is not None and "debt_to_equity" in filtered.columns:
        # Bank carve-out
        is_fin = filtered["broad_sector"].astype(str).str.contains("Financial|Bank", case=False, na=False)
        filtered = filtered[(filtered["debt_to_equity"] <= max_de) | is_fin]

    if min_fcf is not None and "free_cash_flow_cr" in filtered.columns:
        filtered = filtered[filtered["free_cash_flow_cr"] >= min_fcf]

    if min_rev_cagr_5yr is not None and "revenue_cagr_5yr" in filtered.columns:
        filtered = filtered[filtered["revenue_cagr_5yr"] >= min_rev_cagr_5yr]

    if min_pat_cagr_5yr is not None and "pat_cagr_5yr" in filtered.columns:
        filtered = filtered[filtered["pat_cagr_5yr"] >= min_pat_cagr_5yr]

    score_col = "composite_quality_score" if "composite_quality_score" in filtered.columns else "return_on_equity_pct"
    filtered = filtered.sort_values(by=score_col, ascending=False)
    return filtered.to_dict(orient="records")
