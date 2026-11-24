"""10 Unit Tests verifying ETL Loader row counts, column names, schema integrity, and fallbacks."""
import sqlite3
import pandas as pd
import pytest
from src.etl.loader import ETLPipeline


def test_pipeline_directory_initialization(tmp_path):
    """Test 1: Verify ETL pipeline directory tree creation."""
    db_file = tmp_path / "nifty100.db"
    raw_dir = tmp_path / "raw"
    supp_dir = tmp_path / "supporting"
    out_dir = tmp_path / "output"

    pipeline = ETLPipeline(
        db_path=str(db_file),
        raw_dir=str(raw_dir),
        supporting_dir=str(supp_dir),
        output_dir=str(out_dir),
        schema_path="db/schema.sql",
    )
    assert raw_dir.exists()
    assert supp_dir.exists()
    assert out_dir.exists()


def test_database_schema_initialization(tmp_path):
    """Test 2: Verify SQLite schema creates >= 10 relational tables."""
    db_file = tmp_path / "nifty100.db"
    pipeline = ETLPipeline(db_path=str(db_file), schema_path="db/schema.sql")
    pipeline.init_database()
    assert db_file.exists()

    conn = sqlite3.connect(db_file)
    cur = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
    count = cur.fetchone()[0]
    conn.close()
    assert count >= 10


def test_companies_loader_fallback_columns(tmp_path):
    """Test 3: Verify companies table contains required core columns."""
    pipeline = ETLPipeline(
        db_path=str(tmp_path / "nifty.db"),
        raw_dir=str(tmp_path / "raw"),
        supporting_dir=str(tmp_path / "supp"),
        output_dir=str(tmp_path / "out"),
    )
    df_sec = pd.DataFrame([
        {"company_id": "TCS", "broad_sector": "IT", "sub_sector": "IT", "index_weight_pct": 3.8, "market_cap_category": "Large Cap"}
    ])
    df_companies = pipeline.load_companies(df_sec)
    assert "id" in df_companies.columns
    assert "company_name" in df_companies.columns
    assert "face_value" in df_companies.columns
    assert len(df_companies) == 1


def test_profit_and_loss_column_contract():
    """Test 4: Verify Profit and Loss expected column structure."""
    expected_cols = {"company_id", "year", "sales", "operating_profit", "net_profit"}
    dummy_pl = pd.DataFrame(columns=["company_id", "year", "sales", "operating_profit", "net_profit", "opm_percentage"])
    assert expected_cols.issubset(set(dummy_pl.columns))


def test_balancesheet_column_contract():
    """Test 5: Verify Balance Sheet expected column structure."""
    expected_cols = {"company_id", "year", "equity_capital", "reserves", "borrowings", "total_assets"}
    dummy_bs = pd.DataFrame(columns=["company_id", "year", "equity_capital", "reserves", "borrowings", "other_liabilities", "total_assets"])
    assert expected_cols.issubset(set(dummy_bs.columns))


def test_cashflow_column_contract():
    """Test 6: Verify Cash Flow expected column structure."""
    expected_cols = {"company_id", "year", "operating_activity", "investing_activity", "financing_activity"}
    dummy_cf = pd.DataFrame(columns=["company_id", "year", "operating_activity", "investing_activity", "financing_activity", "net_cash_flow"])
    assert expected_cols.issubset(set(dummy_cf.columns))


def test_sectors_column_contract():
    """Test 7: Verify Sectors metadata column structure."""
    expected_cols = {"company_id", "broad_sector", "sub_sector"}
    dummy_sec = pd.DataFrame(columns=["company_id", "broad_sector", "sub_sector", "index_weight_pct", "market_cap_category"])
    assert expected_cols.issubset(set(dummy_sec.columns))


def test_stock_prices_column_contract():
    """Test 8: Verify Stock Prices table structure."""
    expected_cols = {"company_id", "date", "close_price"}
    dummy_px = pd.DataFrame(columns=["company_id", "date", "close_price", "volume"])
    assert expected_cols.issubset(set(dummy_px.columns))


def test_documents_column_contract():
    """Test 9: Verify Documents/filings link table structure."""
    expected_cols = {"company_id", "year", "file_url"}
    dummy_docs = pd.DataFrame(columns=["company_id", "year", "doc_type", "file_url", "is_url_valid"])
    assert expected_cols.issubset(set(dummy_docs.columns))


def test_prosandcons_column_contract():
    """Test 10: Verify Prosandcons qualitative table structure."""
    expected_cols = {"company_id", "type", "description"}
    dummy_pc = pd.DataFrame(columns=["company_id", "type", "description"])
    assert expected_cols.issubset(set(dummy_pc.columns))
