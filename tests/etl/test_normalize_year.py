"""20+ Unit tests for normalize_year function."""
from datetime import date, datetime
import pytest
from src.etl.normaliser import normalize_year


def test_year_mar23():
    """1. Standard month-year hyphen: Mar-23 -> 2023-03."""
    assert normalize_year("Mar-23") == "2023-03"


def test_year_mar_space_23():
    """2. Standard month-year space: Mar 23 -> 2023-03."""
    assert normalize_year("Mar 23") == "2023-03"


def test_year_march2023():
    """3. Full month name with 4-digit year: March-2023 -> 2023-03."""
    assert normalize_year("March-2023") == "2023-03"


def test_year_int_2023():
    """4. Integer year 2023 -> 2023-03."""
    assert normalize_year(2023) == "2023-03"


def test_year_str_int_2023():
    """5. String integer '2023' -> 2023-03."""
    assert normalize_year("2023") == "2023-03"


def test_year_float_2023():
    """6. String float '2023.0' -> 2023-03."""
    assert normalize_year("2023.0") == "2023-03"


def test_year_fy23():
    """7. Short FY prefix 'FY23' -> 2023-03."""
    assert normalize_year("FY23") == "2023-03"


def test_year_fy2024():
    """8. Spaced 4-digit FY 'FY 2024' -> 2024-03."""
    assert normalize_year("FY 2024") == "2024-03"


def test_year_dec22():
    """9. December calendar fiscal year 'Dec-22' -> 2022-12."""
    assert normalize_year("Dec-22") == "2022-12"


def test_year_december2022():
    """10. Full December month 'December-2022' -> 2022-12."""
    assert normalize_year("December-2022") == "2022-12"


def test_year_jun23():
    """11. June fiscal close 'Jun-23' -> 2023-06."""
    assert normalize_year("Jun-23") == "2023-06"


def test_year_already_normal():
    """12. Already normalized string '2023-03' passes through untouched."""
    assert normalize_year("2023-03") == "2023-03"


def test_year_already_normal_dec():
    """13. Already normalized December string '2022-12' passes through."""
    assert normalize_year("2022-12") == "2022-12"


def test_year_slash_separator():
    """14. Slash separator '2023/03' -> 2023-03."""
    assert normalize_year("2023/03") == "2023-03"


def test_year_dot_separator():
    """15. Dot separator '2023.03' -> 2023-03."""
    assert normalize_year("2023.03") == "2023-03"


def test_year_reverse_23_mar():
    """16. Reverse order '23-Mar' -> 2023-03."""
    assert normalize_year("23-Mar") == "2023-03"


def test_year_garbage():
    """17. Unparseable garbage string returns 'PARSE_ERROR'."""
    assert normalize_year("garbage_xyz") == "PARSE_ERROR"


def test_year_empty():
    """18. Empty string returns 'PARSE_ERROR'."""
    assert normalize_year("") == "PARSE_ERROR"


def test_year_none():
    """19. None value returns 'PARSE_ERROR'."""
    assert normalize_year(None) == "PARSE_ERROR"


def test_year_whitespace():
    """20. Whitespace only returns 'PARSE_ERROR'."""
    assert normalize_year("   ") == "PARSE_ERROR"


def test_year_datetime_obj():
    """21. Python datetime object converts to 'YYYY-MM'."""
    dt = datetime(2023, 3, 31)
    assert normalize_year(dt) == "2023-03"


def test_year_date_obj():
    """22. Python date object converts to 'YYYY-MM'."""
    d = date(2024, 12, 31)
    assert normalize_year(d) == "2024-12"
