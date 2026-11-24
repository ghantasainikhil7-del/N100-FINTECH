"""Integration test for Nifty 100 ETL Pipeline."""
import sqlite3
from pathlib import Path
import pandas as pd
import pytest
from src.etl.loader import ETLPipeline


def test_full_pipeline_mock(tmp_path):
    """Test ETL pipeline end-to-end execution on a synthesized mini-universe."""
    db_file = tmp_path / "nifty_test.db"
    raw_dir = tmp_path / "raw"
    supp_dir = tmp_path / "supporting"
    out_dir = tmp_path / "output"
    schema_file = tmp_path / "schema.sql"

    # Write minimal test schema
    schema_file.write_text("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE companies (
            id VARCHAR(16) PRIMARY KEY,
            company_name TEXT NOT NULL,
            face_value NUMERIC DEFAULT 1
        );
        CREATE TABLE sectors (
            company_id VARCHAR(16) PRIMARY KEY,
            broad_sector TEXT,
            sub_sector TEXT,
            index_weight_pct NUMERIC,
            market_cap_category TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
        CREATE TABLE profitandloss (
            id INTEGER,
            company_id VARCHAR(16) NOT NULL,
            year VARCHAR(7) NOT NULL,
            sales NUMERIC,
            operating_profit NUMERIC,
            net_profit NUMERIC,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
    """)

    # Create dummy Excel data
    raw_dir.mkdir(parents=True, exist_ok=True)
    supp_dir.mkdir(parents=True, exist_ok=True)

    df_sec = pd.DataFrame([
        {"company_id": "TCS", "broad_sector": "IT", "sub_sector": "Services", "index_weight_pct": 4.5, "market_cap_category": "Large Cap"},
        {"company_id": "INFY", "broad_sector": "IT", "sub_sector": "Services", "index_weight_pct": 3.2, "market_cap_category": "Large Cap"},
    ])
    df_sec.to_excel(supp_dir / "sectors.xlsx", index=False)

    pipeline = ETLPipeline(
        db_path=str(db_file),
        raw_dir=str(raw_dir),
        supporting_dir=str(supp_dir),
        output_dir=str(out_dir),
        schema_path=str(schema_file),
    )

    # Initialize DB
    pipeline.init_database()
    assert db_file.exists()

    # Load sectors & companies
    df_sectors = pipeline.load_sectors()
    assert len(df_sectors) == 2

    df_companies = pipeline.load_companies(df_sectors)
    assert len(df_companies) == 2
    assert set(df_companies["id"]) == {"TCS", "INFY"}

    # Insert into DB
    conn = pipeline.db_manager.get_connection()
    pipeline.db_manager.load_dataframe("companies", df_companies, conn=conn)
    pipeline.db_manager.load_dataframe("sectors", df_sectors, conn=conn)

    fk_errors = pipeline.db_manager.check_foreign_keys()
    conn.close()

    assert len(fk_errors) == 0
