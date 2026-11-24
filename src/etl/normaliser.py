"""
Nifty 100 Financial Intelligence Platform · ETL Normalisation Engine
Author: Data Analytics Division
Sprint: Sprint 1 · Data Foundation (Days 01–07)
Module: Module 1 (ETL Pipeline)
"""

import re
from typing import Optional, Union

# Month dictionary mapping abbreviations and full names to 2-digit format
MONTH_MAP = {
    "JAN": "01", "JANUARY": "01",
    "FEB": "02", "FEBRUARY": "02",
    "MAR": "03", "MARCH": "03",
    "APR": "04", "APRIL": "04",
    "MAY": "05",
    "JUN": "06", "JUNE": "06",
    "JUL": "07", "JULY": "07",
    "AUG": "08", "AUGUST": "08",
    "SEP": "09", "SEPTEMBER": "09",
    "OCT": "10", "OCTOBER": "10",
    "NOV": "11", "NOVEMBER": "11",
    "DEC": "12", "DECEMBER": "12"
}


def normalize_ticker(val: Optional[Union[str, int, float]]) -> str:
    """
    Normalise company ticker to uppercase, stripped, valid NSE identifier.
    
    Conventions:
    - Strips leading and trailing whitespace
    - Converts all characters to uppercase
    - Preserves hyphens (e.g., 'BAJAJ-AUTO')
    - Preserves ampersands (e.g., 'M&M')
    - Validates string length (2 to 12 characters)
    - Rejects empty, None, or out-of-bounds strings
    
    Args:
        val: Raw ticker identifier
        
    Returns:
        Standardised uppercase NSE ticker symbol
        
    Raises:
        ValueError: If input is null, empty, or fails valid length/character constraints.
    """
    if val is None:
        raise ValueError("Ticker cannot be None")
    
    ticker = str(val).strip().upper()
    
    if not ticker:
        raise ValueError("Ticker cannot be empty string")
    
    if len(ticker) < 2 or len(ticker) > 12:
        raise ValueError(f"Ticker '{ticker}' length {len(ticker)} out of valid range (2-12)")
    
    # Allow alphanumeric characters, hyphens, and ampersands
    if not re.match(r'^[A-Z0-9&\-]+$', ticker):
        raise ValueError(f"Ticker '{ticker}' contains invalid characters")
        
    return ticker


def normalize_year(val: Optional[Union[str, int, float]]) -> str:
    """
    Standardise raw financial year representations into uniform 'YYYY-MM' strings.
    
    Supported formats:
    - 'Mar-23', 'Mar 23', 'March-2023', 'March 2023' -> '2023-03'
    - 'Dec-22', 'Dec 22', 'December 2022' -> '2022-12'
    - 'Jun-23', 'Jun 23' -> '2023-06'
    - '2023' (int or str) -> '2023-03' (standard March close assumed for annual statements)
    - 'FY23', 'FY 23', 'FY2023' -> '2023-03'
    - '2023-03' (already normalised) -> '2023-03'
    
    Args:
        val: Raw year/period identifier
        
    Returns:
        Standardised date string in 'YYYY-MM' format
        
    Raises:
        ValueError: If year is unparseable or formatted as invalid garbage.
    """
    if val is None:
        raise ValueError("Year cannot be None")
        
    raw = str(val).strip()
    if not raw:
        raise ValueError("Year cannot be empty")
        
    # 1. Already normalised: YYYY-MM
    if re.match(r'^\d{4}-(0[1-9]|1[0-2])$', raw):
        return raw

    # 2. Integer or 4-digit string year (e.g., 2023, 2024) -> default to March (03)
    if re.match(r'^\d{4}$', raw):
        return f"{raw}-03"
        
    # 3. Fiscal Year prefix format: FY23, FY 23, FY2023, FY-24
    fy_match = re.match(r'^FY\s*[-]?\s*(\d{2,4})$', raw, re.IGNORECASE)
    if fy_match:
        yr_part = fy_match.group(1)
        full_year = f"20{yr_part}" if len(yr_part) == 2 else yr_part
        return f"{full_year}-03"

    # 4. Month-Year pattern: 'Mar-23', 'Mar 23', 'March-2023', 'March 2023', 'Dec-22', etc.
    # Matches <MonthName> <separator> <YearDigits>
    my_match = re.match(r'^([A-Za-z]+)\s*[-/,\s]\s*(\d{2,4})$', raw)
    if my_match:
        month_str = my_match.group(1).upper()
        yr_str = my_match.group(2)
        if month_str in MONTH_MAP:
            month_num = MONTH_MAP[month_str]
            full_year = f"20{yr_str}" if len(yr_str) == 2 else yr_str
            return f"{full_year}-{month_num}"

    # 5. Reverse Year-Month pattern: '2023-Mar', '2023 Mar'
    ym_match = re.match(r'^(\d{4})\s*[-/,\s]\s*([A-Za-z]+)$', raw)
    if ym_match:
        yr_str = ym_match.group(1)
        month_str = ym_match.group(2).upper()
        if month_str in MONTH_MAP:
            month_num = MONTH_MAP[month_str]
            return f"{yr_str}-{month_num}"

    raise ValueError(f"PARSE_ERROR: Unable to normalise financial year value: '{val}'")
