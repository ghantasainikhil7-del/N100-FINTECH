"""Unit tests for deduplication and foreign key integrity checks."""
import pandas as pd
from src.etl.validator import DataQualityValidator


def test_dedup_annual_pk_keeps_last():
    """DQ-02: Verifies that duplicate (company_id, year) keeps the last occurrence."""
    validator = DataQualityValidator()
    df = pd.DataFrame([
        {"company_id": "TCS", "year": "2023-03", "sales": 200000},
        {"company_id": "TCS", "year": "2023-03", "sales": 225458},
        {"company_id": "INFY", "year": "2023-03", "sales": 146767},
    ])
    cleaned = validator.validate_dq02_annual_pk(df, "profitandloss")
    assert len(cleaned) == 2
    tcs_row = cleaned[cleaned["company_id"] == "TCS"].iloc[0]
    assert tcs_row["sales"] == 225458
    assert len(validator.violations) == 1
    assert validator.violations[0].rule_id == "DQ-02"


def test_dedup_no_duplicates():
    """DQ-02: Leaves unique rows untouched."""
    validator = DataQualityValidator()
    df = pd.DataFrame([
        {"company_id": "TCS", "year": "2022-03", "sales": 190000},
        {"company_id": "TCS", "year": "2023-03", "sales": 225458},
    ])
    cleaned = validator.validate_dq02_annual_pk(df, "profitandloss")
    assert len(cleaned) == 2
    assert len(validator.violations) == 0


def test_fk_integrity_rejects_orphans():
    """DQ-03: Rejects rows whose company_id is not in the master companies table."""
    validator = DataQualityValidator()
    valid_tickers = {"TCS", "INFY"}
    df_child = pd.DataFrame([
        {"company_id": "TCS", "year": "2023-03", "sales": 225458},
        {"company_id": "UNKNOWN_CORP", "year": "2023-03", "sales": 500},
    ])
    cleaned = validator.validate_dq03_fk_integrity(df_child, valid_tickers, "profitandloss")
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["company_id"] == "TCS"
    assert len(validator.violations) == 1
    assert validator.violations[0].rule_id == "DQ-03"
    assert validator.violations[0].severity == "CRITICAL"
