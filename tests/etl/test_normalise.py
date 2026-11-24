"""
Nifty 100 Financial Intelligence Platform · Unit Tests for Normaliser
Covers 35+ Mandatory Unit Tests (20 normalize_year + 15 normalize_ticker)
Sprint 1 · Definition of Done / Acceptance Gate
"""

import pytest
from src.etl.normaliser import normalize_ticker, normalize_year


# ============================================================================
# PART 1: normalize_year() Unit Tests (20 test cases)
# ============================================================================

def test_year_mar23():
    """Test 1: Standard format Mar-23 -> 2023-03"""
    assert normalize_year("Mar-23") == "2023-03"

def test_year_mar_space_23():
    """Test 2: Space separator Mar 23 -> 2023-03"""
    assert normalize_year("Mar 23") == "2023-03"

def test_year_march_2023():
    """Test 3: Full month name March-2023 -> 2023-03"""
    assert normalize_year("March-2023") == "2023-03"

def test_year_march_space_2023():
    """Test 4: Full month name with space March 2023 -> 2023-03"""
    assert normalize_year("March 2023") == "2023-03"

def test_year_integer():
    """Test 5: Integer year 2023 -> 2023-03"""
    assert normalize_year(2023) == "2023-03"

def test_year_string_4digits():
    """Test 6: 4-digit string '2024' -> 2024-03"""
    assert normalize_year("2024") == "2024-03"

def test_year_fy24():
    """Test 7: Fiscal year prefix FY24 -> 2024-03"""
    assert normalize_year("FY24") == "2024-03"

def test_year_fy_space_23():
    """Test 8: Fiscal year with space FY 23 -> 2023-03"""
    assert normalize_year("FY 23") == "2023-03"

def test_year_fy2022():
    """Test 9: 4-digit FY prefix FY2022 -> 2022-03"""
    assert normalize_year("FY2022") == "2022-03"

def test_year_dec22():
    """Test 10: December year-end (Nestle) Dec-22 -> 2022-12"""
    assert normalize_year("Dec-22") == "2022-12"

def test_year_dec_2020():
    """Test 11: December with 4-digit year Dec 2020 -> 2020-12"""
    assert normalize_year("Dec 2020") == "2020-12"

def test_year_december_2019():
    """Test 12: Full month December 2019 -> 2019-12"""
    assert normalize_year("December 2019") == "2019-12"

def test_year_jun23():
    """Test 13: June fiscal year-end Jun-23 -> 2023-06"""
    assert normalize_year("Jun-23") == "2023-06"

def test_year_sep21():
    """Test 14: September fiscal year-end (Siemens) Sep-21 -> 2021-09"""
    assert normalize_year("Sep-21") == "2021-09"

def test_year_already_normalised():
    """Test 15: Already normalised 2023-03 -> 2023-03"""
    assert normalize_year("2023-03") == "2023-03"

def test_year_whitespace():
    """Test 16: Leading/trailing whitespace '  Mar-24  ' -> 2024-03"""
    assert normalize_year("  Mar-24  ") == "2024-03"

def test_year_reverse_ym():
    """Test 17: Reverse year-month format '2023-Mar' -> 2023-03"""
    assert normalize_year("2023-Mar") == "2023-03"

def test_year_garbage():
    """Test 18: Unparseable garbage string raises ValueError"""
    with pytest.raises(ValueError, match="PARSE_ERROR"):
        normalize_year("xyz_invalid")

def test_year_none():
    """Test 19: None value raises ValueError"""
    with pytest.raises(ValueError):
        normalize_year(None)

def test_year_empty():
    """Test 20: Empty string raises ValueError"""
    with pytest.raises(ValueError):
        normalize_year("   ")


# ============================================================================
# PART 2: normalize_ticker() Unit Tests (15 test cases)
# ============================================================================

def test_ticker_clean():
    """Test 21: Clean ticker unchanged"""
    assert normalize_ticker("TCS") == "TCS"

def test_ticker_lowercase():
    """Test 22: Lowercase converted to uppercase"""
    assert normalize_ticker("tcs") == "TCS"

def test_ticker_mixed_case():
    """Test 23: Mixed case converted to uppercase"""
    assert normalize_ticker("InFy") == "INFY"

def test_ticker_whitespace():
    """Test 24: Leading and trailing whitespace stripped"""
    assert normalize_ticker("  HDFCBANK  ") == "HDFCBANK"

def test_ticker_hyphen_preserved():
    """Test 25: Hyphen preserved for valid tickers like BAJAJ-AUTO"""
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"

def test_ticker_ampersand_preserved():
    """Test 26: Ampersand preserved for valid tickers like M&M"""
    assert normalize_ticker("m&m") == "M&M"

def test_ticker_numeric_suffix():
    """Test 27: Alphanumeric ticker valid"""
    assert normalize_ticker("nifty50") == "NIFTY50"

def test_ticker_min_length_2():
    """Test 28: 2-character ticker valid (boundary check)"""
    assert normalize_ticker("LT") == "LT"

def test_ticker_max_length_12():
    """Test 29: 12-character ticker valid (boundary check)"""
    assert normalize_ticker("TATACONSUMER") == "TATACONSUMER"

def test_ticker_too_short():
    """Test 30: 1-character string rejected"""
    with pytest.raises(ValueError, match="length"):
        normalize_ticker("A")

def test_ticker_too_long():
    """Test 31: >12 character string rejected"""
    with pytest.raises(ValueError, match="length"):
        normalize_ticker("LONGERTHANTWELVECHARS")

def test_ticker_none():
    """Test 32: None ticker rejected"""
    with pytest.raises(ValueError):
        normalize_ticker(None)

def test_ticker_empty():
    """Test 33: Empty ticker rejected"""
    with pytest.raises(ValueError):
        normalize_ticker("   ")

def test_ticker_invalid_special_chars():
    """Test 34: Invalid symbols like @, #, $ rejected"""
    with pytest.raises(ValueError, match="invalid characters"):
        normalize_ticker("TCS#1")

def test_ticker_internal_spaces():
    """Test 35: Internal space rejected"""
    with pytest.raises(ValueError, match="invalid characters"):
        normalize_ticker("TCS LTD")
