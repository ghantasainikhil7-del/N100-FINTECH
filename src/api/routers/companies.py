"""Company Intelligence Endpoints."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
import pandas as pd

router = APIRouter(prefix="/companies", tags=["Companies"])
DB_PATH = Path("data/nifty100.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def list_companies(
    sector: Optional[str] = Query(None, description="Filter by broad sector"),
    market_cap_category: Optional[str] = Query(None, description="Filter by Large Cap / Mid Cap"),
    search: Optional[str] = Query(None, description="Search ticker or company name"),
) -> list[dict[str, Any]]:
    """Return list of all 92 companies with basic sector and return metrics."""
    if not DB_PATH.exists():
        # Fallback sample dataset
        sample = [
            {"id": "TCS", "company_name": "Tata Consultancy Services Ltd.", "broad_sector": "Information Technology", "sub_sector": "IT Consulting", "roe_pct": 46.9, "roce_pct": 58.0},
            {"id": "INFY", "company_name": "Infosys Ltd.", "broad_sector": "Information Technology", "sub_sector": "IT Consulting", "roe_pct": 31.8, "roce_pct": 39.2},
            {"id": "HDFCBANK", "company_name": "HDFC Bank Ltd.", "broad_sector": "Financials", "sub_sector": "Private Banks", "roe_pct": 16.8, "roce_pct": 18.2},
            {"id": "RELIANCE", "company_name": "Reliance Industries Ltd.", "broad_sector": "Energy", "sub_sector": "Oil & Gas", "roe_pct": 9.4, "roce_pct": 10.5},
            {"id": "HINDUNILVR", "company_name": "Hindustan Unilever Ltd.", "broad_sector": "Fast Moving Consumer Goods", "sub_sector": "FMCG", "roe_pct": 20.2, "roce_pct": 27.5},
        ]
        return sample

    conn = get_db()
    try:
        query = """
            SELECT c.id, c.company_name, s.broad_sector, s.sub_sector,
                   r.return_on_equity_pct as roe_pct,
                   r.return_on_capital_employed_pct as roce_pct
            FROM companies c
            LEFT JOIN sectors s ON c.id = s.company_id
            LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = (
                SELECT MAX(year) FROM financial_ratios WHERE company_id = c.id
            )
            WHERE 1=1
        """
        params = []
        if sector:
            query += " AND s.broad_sector = ?"
            params.append(sector)
        if market_cap_category:
            query += " AND s.market_cap_category = ?"
            params.append(market_cap_category)
        if search:
            query += " AND (c.id LIKE ? OR c.company_name LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])

        query += " ORDER BY c.id ASC"
        cursor = conn.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        return rows
    finally:
        conn.close()


@router.get("/{ticker}")
def get_company_profile(ticker: str) -> dict[str, Any]:
    """Return detailed company profile, sector classification, and latest financial KPIs."""
    ticker_clean = ticker.upper()
    if not DB_PATH.exists():
        if ticker_clean == "TCS":
            return {
                "id": "TCS", "company_name": "Tata Consultancy Services Ltd.",
                "broad_sector": "Information Technology", "sub_sector": "IT Consulting",
                "about_company": "Premier global IT services and consulting organization.",
                "latest_kpis": {"roe": 46.9, "roce": 58.0, "de": 0.0, "fcf": 35000.0, "cagr_5yr": 12.86}
            }
        raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker_clean}' not found")

    conn = get_db()
    try:
        cur = conn.execute("SELECT * FROM companies WHERE id = ?", (ticker_clean,))
        co = cur.fetchone()
        if not co:
            raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker_clean}' not found")

        cur_sec = conn.execute("SELECT * FROM sectors WHERE company_id = ?", (ticker_clean,))
        sec = cur_sec.fetchone()

        cur_r = conn.execute("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC LIMIT 1", (ticker_clean,))
        latest_r = cur_r.fetchone()

        return {
            "company": dict(co),
            "sector": dict(sec) if sec else {},
            "latest_ratios": dict(latest_r) if latest_r else {},
        }
    finally:
        conn.close()


@router.get("/{ticker}/pl")
def get_pl_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None) -> list[dict[str, Any]]:
    """Return historical Profit & Loss entries for the company."""
    ticker_clean = ticker.upper()
    if not DB_PATH.exists():
        return [{"company_id": ticker_clean, "year": "2024-03", "sales": 240893.0, "operating_profit": 63482.0, "net_profit": 46099.0}]

    conn = get_db()
    try:
        query = "SELECT * FROM profitandloss WHERE company_id = ?"
        params = [ticker_clean]
        if from_year:
            query += " AND year >= ?"
            params.append(from_year)
        if to_year:
            query += " AND year <= ?"
            params.append(to_year)
        query += " ORDER BY year ASC"
        cursor = conn.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/{ticker}/bs")
def get_bs_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None) -> list[dict[str, Any]]:
    """Return historical Balance Sheet entries for the company."""
    ticker_clean = ticker.upper()
    if not DB_PATH.exists():
        return [{"company_id": ticker_clean, "year": "2024-03", "equity_capital": 362.0, "reserves": 90127.0, "borrowings": 0.0}]

    conn = get_db()
    try:
        query = "SELECT * FROM balancesheet WHERE company_id = ?"
        params = [ticker_clean]
        if from_year:
            query += " AND year >= ?"
            params.append(from_year)
        if to_year:
            query += " AND year <= ?"
            params.append(to_year)
        query += " ORDER BY year ASC"
        cursor = conn.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/{ticker}/cashflow")
def get_cf_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None) -> list[dict[str, Any]]:
    """Return historical Cash Flow entries for the company."""
    ticker_clean = ticker.upper()
    if not DB_PATH.exists():
        return [{"company_id": ticker_clean, "year": "2024-03", "operating_activity": 44342.0, "investing_activity": -3671.0, "financing_activity": -37746.0}]

    conn = get_db()
    try:
        query = "SELECT * FROM cashflow WHERE company_id = ?"
        params = [ticker_clean]
        if from_year:
            query += " AND year >= ?"
            params.append(from_year)
        if to_year:
            query += " AND year <= ?"
            params.append(to_year)
        query += " ORDER BY year ASC"
        cursor = conn.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/{ticker}/ratios")
def get_ratios_history(ticker: str, year: Optional[str] = None) -> list[dict[str, Any]]:
    """Return computed financial KPIs and quality scores."""
    ticker_clean = ticker.upper()
    if not DB_PATH.exists():
        return [{"company_id": ticker_clean, "year": "2024-03", "return_on_equity_pct": 46.9, "debt_to_equity": 0.0, "composite_quality_score": 91.2}]

    conn = get_db()
    try:
        query = "SELECT * FROM financial_ratios WHERE company_id = ?"
        params = [ticker_clean]
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year ASC"
        cursor = conn.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/{ticker}/tearsheet")
def download_tearsheet(ticker: str):
    """Download the 2-page publication-grade tearsheet PDF for the company."""
    ticker_clean = ticker.upper()
    pdf_path = Path(f"reports/tearsheets/{ticker_clean}_tearsheet.pdf")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Tearsheet PDF for {ticker_clean} has not been generated yet")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{ticker_clean}_tearsheet.pdf",
    )
