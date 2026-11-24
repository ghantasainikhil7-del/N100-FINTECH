"""Unit tests for DataQualityValidator covering all 16 Data Quality rules."""
import pandas as pd
import pytest
from src.etl.validator import DataQualityValidator


def test_dq01_company_pk_unique():
    validator = DataQualityValidator()
    df_valid = pd.DataFrame([{"id": "TCS"}, {"id": "INFY"}])
    assert validator.validate_dq01_company_pk(df_valid) is True
    assert len(validator.critical_violations()) == 0

    df_dup = pd.DataFrame([{"id": "TCS"}, {"id": "TCS"}])
    assert validator.validate_dq01_company_pk(df_dup) is False
    assert len(validator.critical_violations()) >= 1


def test_dq02_annual_pk_dedup():
    validator = DataQualityValidator()
    df = pd.DataFrame([
        {"company_id": "TCS", "year": "2023-03", "sales": 100},
        {"company_id": "TCS", "year": "2023-03", "sales": 120},
    ])
    df_clean = validator.validate_dq02_annual_pk(df, "profitandloss")
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["sales"] == 120


def test_dq03_fk_integrity():
    validator = DataQualityValidator()
    valid_ids = {"TCS", "INFY"}
    df = pd.DataFrame([
        {"company_id": "TCS", "year": "2023-03"},
        {"company_id": "UNKNOWN_CORP", "year": "2023-03"},
    ])
    df_clean = validator.validate_dq03_fk_integrity(df, valid_ids, "profitandloss")
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["company_id"] == "TCS"
    assert len(validator.critical_violations()) == 1


def test_dq04_bs_balance():
    validator = DataQualityValidator()
    # Balanced
    df_ok = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "total_assets": 1000, "total_liabilities": 1000}])
    validator.validate_dq04_bs_balance(df_ok)
    assert len(validator.warning_violations()) == 0

    # Imbalanced (>1%)
    df_bad = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "total_assets": 1000, "total_liabilities": 900}])
    validator.validate_dq04_bs_balance(df_bad)
    assert len(validator.warning_violations()) == 1


def test_dq05_opm_crosscheck():
    validator = DataQualityValidator()
    # Correct OPM: 25 / 100 * 100 = 25%
    df_ok = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "sales": 100, "operating_profit": 25, "opm_percentage": 25.0}])
    validator.validate_dq05_opm_crosscheck(df_ok)
    assert len(validator.warning_violations()) == 0

    # Mismatch OPM: 25 / 100 * 100 != 50%
    df_bad = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "sales": 100, "operating_profit": 25, "opm_percentage": 50.0}])
    validator.validate_dq05_opm_crosscheck(df_bad)
    assert len(validator.warning_violations()) == 1


def test_dq06_positive_sales():
    validator = DataQualityValidator()
    df_bad = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "sales": -50}])
    validator.validate_dq06_positive_sales(df_bad, bank_tickers=set())
    assert len(validator.warning_violations()) == 1

    # Bank carve-out passes
    validator.violations.clear()
    validator.validate_dq06_positive_sales(df_bad, bank_tickers={"TCS"})
    assert len(validator.warning_violations()) == 0


def test_dq07_year_format():
    validator = DataQualityValidator()
    df = pd.DataFrame([
        {"company_id": "TCS", "year": "2023-03"},
        {"company_id": "TCS", "year": "INVALID_YR"},
    ])
    df_clean = validator.validate_dq07_year_format(df, "profitandloss")
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["year"] == "2023-03"
    assert len(validator.critical_violations()) == 1


def test_dq08_ticker_format():
    validator = DataQualityValidator()
    df = pd.DataFrame([
        {"company_id": "TCS"},
        {"company_id": "X"},  # < 2 chars
        {"company_id": "TOOLONGCOMPANYTICKER"},
    ])
    df_clean = validator.validate_dq08_ticker_format(df, "profitandloss")
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["company_id"] == "TCS"
    assert len(validator.critical_violations()) == 2


def test_dq09_net_cash_check():
    validator = DataQualityValidator()
    df_ok = pd.DataFrame([{
        "company_id": "TCS", "year": "2023-03",
        "operating_activity": 100, "investing_activity": -40, "financing_activity": -50,
        "net_cash_flow": 10
    }])
    validator.validate_dq09_net_cash_check(df_ok)
    assert len(validator.warning_violations()) == 0

    df_bad = pd.DataFrame([{
        "company_id": "TCS", "year": "2023-03",
        "operating_activity": 100, "investing_activity": -40, "financing_activity": -50,
        "net_cash_flow": 50  # diff 40 > 10 Cr tolerance
    }])
    validator.validate_dq09_net_cash_check(df_bad)
    assert len(validator.warning_violations()) == 1


def test_dq10_fixed_assets():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "fixed_assets": -500}])
    df_fixed = validator.validate_dq10_fixed_assets(df)
    assert df_fixed.iloc[0]["fixed_assets"] == 0.0
    assert len(validator.warning_violations()) == 1


def test_dq11_tax_rate():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "tax_percentage": 75.0}])
    validator.validate_dq11_tax_rate(df)
    assert len(validator.warning_violations()) == 1


def test_dq12_dividend_payout():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "dividend_payout": 250.0}])
    validator.validate_dq12_dividend_payout(df)
    assert len(validator.warning_violations()) == 1


def test_dq14_eps_sign():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "net_profit": 1000, "eps": -5.0}])
    validator.validate_dq14_eps_sign(df)
    assert len(validator.warning_violations()) == 1


def test_dq15_strict_bs_balance():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "total_assets": 1000, "total_liabilities": 1000.5}])
    diffs = validator.validate_dq15_strict_bs_balance(df)
    assert diffs == 1
    assert len(validator.info_violations()) == 1


def test_dq16_coverage():
    validator = DataQualityValidator()
    df_pl = pd.DataFrame([{"company_id": "NEWCO", "year": f"202{i}-03"} for i in range(3)])  # 3 years
    df_bs = df_pl.copy()
    df_cf = df_pl.copy()
    validator.validate_dq16_coverage(df_pl, df_bs, df_cf, min_years=5)
    assert len(validator.warning_violations()) == 1
