"""Utility functions for Nifty 100 ETL pipeline.

Provides file discovery, download helpers, and DataFrame cleaning utilities.
"""
from __future__ import annotations

import logging
import os
import shutil
import urllib.request
from pathlib import Path
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def discover_source_file(filename: str, target_dir: Path, search_dirs: Optional[list[Path]] = None) -> Path:
    """Discover a source dataset file in target_dir or candidate directories."""
    dest = target_dir / filename
    if dest.exists() and dest.stat().st_size > 100:
        return dest

    candidates = search_dirs or [
        target_dir.parent / "raw",
        target_dir.parent / "supporting",
        target_dir.parent,
        Path.home() / "Downloads",
    ]

    for d in candidates:
        if d.exists():
            direct_match = d / filename
            if direct_match.exists() and direct_match.stat().st_size > 100:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(direct_match, dest)
                logger.info("Discovered and copied %s from %s to %s", filename, direct_match, dest)
                return dest

            for f in d.glob(f"*{filename}*"):
                if f.is_file() and f.stat().st_size > 100:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    logger.info("Found fuzzy match %s, copied to %s", f, dest)
                    return dest

    return dest


def download_file(url: str, dest_path: Path, timeout: int = 30) -> bool:
    """Safely download file from remote URL with headers."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) N100-Data-Platform/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        logger.info("Successfully downloaded %s (%d bytes)", dest_path.name, dest_path.stat().st_size)
        return True
    except Exception as e:
        logger.warning("Failed to download %s from %s: %e", dest_path.name, url, e)
        return False


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to lower_snake_case and strip whitespace."""
    clean_cols = []
    for c in df.columns:
        s = str(c).strip().replace(" ", "_").replace("-", "_").lower()
        clean_cols.append(s)
    df.columns = clean_cols
    return df
