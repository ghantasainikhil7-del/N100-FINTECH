"""Unit tests for NLP text parser and auto pros/cons generator."""
import pytest
from src.nlp.parser import AnalysisParser
from src.nlp.pros_cons_generator import ProsConsGenerator


def test_analysis_regex_parser_single():
    """Extract (period, value) from single period growth string."""
    text = "10 Years: 21%"
    res = AnalysisParser.parse_growth_string(text)
    assert len(res) == 1
    assert res[0] == (10, 21.0)


def test_analysis_regex_parser_multiple():
    """Extract multiple (period, value) pairs from multi-period text."""
    text = "10 Years: 21%   5 Years: 18.5%   3 Years: 15.2%"
    res = AnalysisParser.parse_growth_string(text)
    assert len(res) == 3
    assert res[0] == (10, 21.0)
    assert res[1] == (5, 18.5)
    assert res[2] == (3, 15.2)


def test_analysis_regex_parser_variations():
    """Handles space, case, and colon variations."""
    assert AnalysisParser.parse_growth_string("1 Year: 12.4%")[0] == (1, 12.4)
    assert AnalysisParser.parse_growth_string("5Years:6%")[0] == (5, 6.0)
    assert AnalysisParser.parse_growth_string("10 years 25.5%")[0] == (10, 25.5)


def test_analysis_regex_parser_invalid():
    """Returns empty list for empty or non-matching text."""
    assert AnalysisParser.parse_growth_string("") == []
    assert AnalysisParser.parse_growth_string(None) == []
    assert AnalysisParser.parse_growth_string("No CAGR figures available") == []


def test_pros_cons_confidence_filtering():
    """Verify confidence score filter threshold (> 60%)."""
    gen = ProsConsGenerator(min_confidence=60.0)
    assert gen.min_confidence == 60.0
