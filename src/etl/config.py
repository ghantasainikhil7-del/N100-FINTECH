"""ETL Configuration for Nifty 100 Financial Intelligence Platform.

Defines filesystem paths, table definitions, dataset mappings, and DQ rule thresholds.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Base Directory Resolution
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

# Data Directories
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
SUPPORTING_DATA_DIR: Path = DATA_DIR / "supporting"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"
DB_DIR: Path = PROJECT_ROOT / "db"
SCHEMA_PATH: Path = DB_DIR / "schema.sql"

# Database Paths (both primary data/nifty100.db and root nifty100.db fallback)
DB_PATH: Path = DATA_DIR / "nifty100.db"
ROOT_DB_PATH: Path = PROJECT_ROOT / "nifty100.db"

# Core Excel Files (header=1: row 0 is metadata, row 1 is headers)
CORE_DATASETS: dict[str, str] = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
}

# Supplementary Datasets (header=0)
SUPPLEMENTARY_DATASETS: dict[str, str] = {
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "company_master": "company_master.csv",
}

# Remote Download URLs
DEFAULT_DATASET_URLS: dict[str, str] = {
    "companies.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501606103-7177b6c2-companies.xlsx",
    "profitandloss.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501607124-aad40f4f-profitandloss.xlsx",
    "balancesheet.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501604829-ac8c0874-balancesheet.xlsx",
    "cashflow.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501605758-8e951681-cashflow.xlsx",
    "analysis.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501604303-57986a9b-analysis.xlsx",
    "documents.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501606362-ba899c04-documents.xlsx",
    "prosandcons.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501607452-d6bbe55b-prosandcons.xlsx",
    "sectors.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501621129-8684701e-sectors.xlsx",
    "stock_prices.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501621395-a51977cd-stock_prices.xlsx",
    "market_cap.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620397-69ae3e7f-market_cap.xlsx",
    "peer_groups.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620796-5060f580-peer_groups.xlsx",
    "financial_ratios.xlsx": "https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620089-fb3ae469-financial_ratios.xlsx",
}

# The 11 Core Domain Tables
TABLE_NAMES: list[str] = [
    "companies",
    "sectors",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "stock_prices",
    "financial_ratios",
    "peer_groups",
]

# Table Ingestion Order (Respecting Foreign Key Hierarchies)
LOAD_ORDER: list[str] = [
    "companies",
    "sectors",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "stock_prices",
    "market_cap",
    "peer_groups",
    "financial_ratios",
]

# DQ Validation Thresholds
DQ_THRESHOLDS: dict[str, Any] = {
    "BS_BALANCE_TOLERANCE": 0.01,         # DQ-04: 1% max variance
    "OPM_TOLERANCE_PCT": 1.0,             # DQ-05: 1% tolerance
    "NET_CASH_TOLERANCE_CR": 10.0,        # DQ-09: 10 Crore tolerance
    "TAX_RATE_MIN_PCT": 0.0,              # DQ-11: 0% min tax rate
    "TAX_RATE_MAX_PCT": 60.0,             # DQ-11: 60% max tax rate
    "DIVIDEND_PAYOUT_MAX_PCT": 200.0,     # DQ-12: 200% max payout ratio
    "MIN_YEAR_COVERAGE": 5,               # DQ-16: 5 years minimum history
}

# Sample 5 companies for manual audit review
MANUAL_REVIEW_COMPANIES: list[dict[str, str]] = [
    {"ticker": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "Information Technology"},
    {"ticker": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Financials"},
    {"ticker": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy"},
    {"ticker": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Consumer Discretionary"},
    {"ticker": "ABB", "name": "ABB India Ltd", "sector": "Industrials"},
]
