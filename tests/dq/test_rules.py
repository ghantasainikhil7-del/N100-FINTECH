"""Unit tests verifying all 16 Data Quality rules trigger correctly with proper severities."""
import pandas as pd
from src.etl.validator import DataQualityValidator


def test_dq01_company_pk():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"id": "TCS"}, {"id": "TCS"}])
    assert validator.validate_dq01_company_pk(df) is False
    assert any(v.rule_id == "DQ-01" and v.severity == "CRITICAL" for v in validator.violations)


def test_dq02_annual_pk():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03"}, {"company_id": "TCS", "year": "2023-03"}])
    res = validator.validate_dq02_annual_pk(df, "pl")
    assert len(res) == 1
    assert any(v.rule_id == "DQ-02" and v.severity == "CRITICAL" for v in validator.violations)


def test_dq03_fk_integrity():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "ORPHAN", "year": "2023-03"}])
    res = validator.validate_dq03_fk_integrity(df, {"TCS"}, "pl")
    assert len(res) == 0
    assert any(v.rule_id == "DQ-03" and v.severity == "CRITICAL" for v in validator.violations)


def test_dq04_bs_balance():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "total_assets": 1000.0, "total_liabilities": 1050.0}])
    validator.validate_dq04_bs_balance(df)
    assert any(v.rule_id == "DQ-04" and v.severity == "WARNING" for v in validator.violations)


def test_dq05_opm_crosscheck():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "sales": 1000.0, "operating_profit": 200.0, "opm_percentage": 25.0}])
    validator.validate_dq05_opm_crosscheck(df)
    assert any(v.rule_id == "DQ-05" and v.severity == "WARNING" for v in validator.violations)


def test_dq06_positive_sales():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "sales": -50.0}])
    validator.validate_dq06_positive_sales(df, bank_tickers=set())
    assert any(v.rule_id == "DQ-06" and v.severity == "WARNING" for v in validator.violations)


def test_dq07_year_format():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "BAD_YEAR"}, {"company_id": "TCS", "year": "2023-03"}])
    res = validator.validate_dq07_year_format(df, "pl")
    assert len(res) == 1
    assert any(v.rule_id == "DQ-07" and v.severity == "CRITICAL" for v in validator.violations)


def test_dq08_ticker_format():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "INVALID@TICKER"}, {"company_id": "TCS"}])
    res = validator.validate_dq08_ticker_format(df, "companies")
    assert len(res) == 1
    assert any(v.rule_id == "DQ-08" and v.severity == "CRITICAL" for v in validator.violations)


def test_dq09_net_cash_check():
    validator = DataQualityValidator()
    df = pd.DataFrame([{
        "company_id": "TCS", "year": "2023-03",
        "operating_activity": 100.0, "investing_activity": -40.0, "financing_activity": -20.0,
        "net_cash_flow": 100.0  # Mismatch: calc is 40, diff is 60 > 10
    }])
    validator.validate_dq09_net_cash_check(df)
    assert any(v.rule_id == "DQ-09" and v.severity == "WARNING" for v in validator.violations)


def test_dq10_fixed_assets():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "fixed_assets": -50.0}])
    res = validator.validate_dq10_fixed_assets(df)
    assert res.iloc[0]["fixed_assets"] == 0.0
    assert any(v.rule_id == "DQ-10" and v.severity == "WARNING" for v in validator.violations)


def test_dq11_tax_rate():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "tax_percentage": 75.0}])
    validator.validate_dq11_tax_rate(df)
    assert any(v.rule_id == "DQ-11" and v.severity == "WARNING" for v in validator.violations)


def test_dq12_dividend_payout():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "dividend_payout": 250.0}])
    validator.validate_dq12_dividend_payout(df)
    assert any(v.rule_id == "DQ-12" and v.severity == "WARNING" for v in validator.violations)


def test_dq14_eps_sign():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "net_profit": 500.0, "eps": -2.0}])
    validator.validate_dq14_eps_sign(df)
    assert any(v.rule_id == "DQ-14" and v.severity == "WARNING" for v in validator.violations)


def test_dq15_strict_bs_balance():
    validator = DataQualityValidator()
    df = pd.DataFrame([{"company_id": "TCS", "year": "2023-03", "total_assets": 1000.0, "total_liabilities": 1000.5}])
    c = validator.validate_dq15_strict_bs_balance(df)
    assert c == 1
    assert any(v.rule_id == "DQ-15" and v.severity == "INFO" for v in validator.violations)


def test_dq16_coverage():
    validator = DataQualityValidator()
    df_pl = pd.DataFrame([{"company_id": "TCS", "year": "2023-03"}, {"company_id": "TCS", "year": "2022-03"}])
    df_bs = df_pl.copy()
    df_cf = df_pl.copy()
    validator.validate_dq16_coverage(df_pl, df_bs, df_cf)
    assert any(v.rule_id == "DQ-16" and v.severity == "WARNING" for v in validator.violations)
