"""15+ Unit tests for normalize_ticker function."""
import pytest
from src.etl.normaliser import normalize_ticker


def test_ticker_upper():
    """1. Uppercase ticker returns unchanged."""
    assert normalize_ticker("TCS") == "TCS"


def test_ticker_lower():
    """2. Lowercase ticker converts to uppercase."""
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_mixed():
    """3. Mixed case converts to uppercase."""
    assert normalize_ticker("InFy") == "INFY"


def test_ticker_whitespace_both():
    """4. Leading and trailing spaces are stripped."""
    assert normalize_ticker("   TCS   ") == "TCS"


def test_ticker_whitespace_tabs():
    """5. Tabs and newlines are stripped."""
    assert normalize_ticker("\tINFY\n") == "INFY"


def test_ticker_hyphen():
    """6. Hyphen in ticker is preserved."""
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"


def test_ticker_hyphen_lower():
    """7. Lowercase hyphenated ticker converted."""
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"


def test_ticker_ampersand():
    """8. Ampersand in ticker is preserved."""
    assert normalize_ticker("M&M") == "M&M"


def test_ticker_ampersand_lower():
    """9. Lowercase ampersand ticker converted."""
    assert normalize_ticker("m&m") == "M&M"


def test_ticker_single_char():
    """10. Single character ticker rejected (< 2 chars)."""
    assert normalize_ticker("A") == ""


def test_ticker_too_long():
    """11. Ticker > 12 characters rejected."""
    assert normalize_ticker("VERYLONGCOMPANYTICKER") == ""


def test_ticker_special_chars():
    """12. Invalid symbols (@, $, !) rejected."""
    assert normalize_ticker("TCS@123") == ""


def test_ticker_none():
    """13. None returns empty string."""
    assert normalize_ticker(None) == ""


def test_ticker_empty():
    """14. Empty string returns empty string."""
    assert normalize_ticker("") == ""


def test_ticker_alphanumeric_suffix():
    """15. Alphanumeric tickers preserved."""
    assert normalize_ticker("JSWENERGY") == "JSWENERGY"


def test_ticker_punctuation():
    """16. Punctuation symbols rejected."""
    assert normalize_ticker("RELIANCE.NS") == ""
