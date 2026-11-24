"""Unit tests for DatabaseManager module."""
import sqlite3
import pandas as pd
import pytest
from src.etl.database import DatabaseManager


def test_db_manager_init(tmp_path):
    db_file = tmp_path / "test.db"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE companies (
            id VARCHAR(16) PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL
        );
        CREATE TABLE profitandloss (
            id INTEGER,
            company_id VARCHAR(16) NOT NULL,
            year VARCHAR(7) NOT NULL,
            sales NUMERIC,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
    """)

    manager = DatabaseManager(db_file, schema_file)
    manager.init_database()

    counts = manager.get_table_counts()
    assert "companies" in counts
    assert "profitandloss" in counts
    assert counts["companies"] == 0


def test_fk_enforcement(tmp_path):
    db_file = tmp_path / "test_fk.db"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE companies (id VARCHAR(16) PRIMARY KEY);
        CREATE TABLE child (
            id INTEGER PRIMARY KEY,
            company_id VARCHAR(16) NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        );
    """)
    manager = DatabaseManager(db_file, schema_file)
    manager.init_database()

    conn = manager.get_connection()
    # Inserting orphan child without parent should fail foreign key constraint
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO child (id, company_id) VALUES (1, 'NONEXISTENT');")
        conn.commit()
    conn.close()


def test_load_dataframe_and_check(tmp_path):
    db_file = tmp_path / "test_load.db"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE companies (id VARCHAR(16) PRIMARY KEY, company_name TEXT);
    """)
    manager = DatabaseManager(db_file, schema_file)
    manager.init_database()

    df = pd.DataFrame([{"id": "TCS", "company_name": "TCS Ltd"}, {"id": "INFY", "company_name": "Infosys Ltd"}])
    rows = manager.load_dataframe("companies", df)
    assert rows == 2

    violations = manager.check_foreign_keys()
    assert len(violations) == 0
