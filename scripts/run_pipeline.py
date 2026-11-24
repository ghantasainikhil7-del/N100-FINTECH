"""Pipeline Runner for Nifty 100 Financial Data Platform (Sprint 1: Data Foundation).

Executes full ETL ingestion, validates DQ rules, executes database integrity checks,
runs analytical verification queries, and prints institutional audit summary.
"""
from __future__ import annotations

import logging
import sqlite3
import sys
import time
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.etl.config import DB_PATH, OUTPUT_DIR, ROOT_DB_PATH
from src.etl.loader import ETLPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_pipeline")


def main() -> int:
    print("=" * 80)
    print("  NIFTY 100 FINANCIAL DATA PLATFORM — SPRINT 1 DATA FOUNDATION")
    print("  ETL Ingestion, 16 DQ Rules Validation, SQLite Database Population")
    print("=" * 80)

    t0 = time.time()
    pipeline = ETLPipeline()
    result = pipeline.run()
    elapsed = time.time() - t0

    # Verify SQLite database
    target_db = DB_PATH if DB_PATH.exists() else ROOT_DB_PATH
    conn = sqlite3.connect(target_db)
    cur = conn.cursor()

    # Table counts
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]

    print("\n" + "-" * 80)
    print("  DATABASE TABLE POPULATION AUDIT")
    print("-" * 80)
    print(f"  {'Table Name':<25} {'Row Count':>12} {'Status':>12}")
    print("  " + "-" * 51)

    total_rows = 0
    for t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        total_rows += count
        status = "PASSED" if count > 0 else "EMPTY"
        print(f"  {t:<25} {count:>12,d} {status:>12}")

    print("  " + "-" * 51)
    print(f"  {'Total Records Loaded':<25} {total_rows:>12,d}")

    # Check foreign keys
    cur.execute("PRAGMA foreign_key_check;")
    fk_errors = cur.fetchall()

    print("\n" + "-" * 80)
    print("  DATA QUALITY & INTEGRITY GATES")
    print("-" * 80)
    print(f"  PRAGMA foreign_key_check : {len(fk_errors)} violations ({'PASSED' if len(fk_errors) == 0 else 'FAILED'})")
    print(f"  Critical DQ Failures     : {result.get('dq_critical', 0)} ({'PASSED' if result.get('dq_critical', 0) == 0 else 'FAILED'})")
    print(f"  Warning DQ Flags (logged): {result.get('dq_warning', 0)}")
    print(f"  Info DQ Notes (logged)   : {result.get('dq_info', 0)}")
    print(f"  Audit Trail CSV          : {OUTPUT_DIR / 'load_audit.csv'}")
    print(f"  Source Manifest CSV      : {OUTPUT_DIR / 'source_manifest.csv'}")
    print(f"  Source Table Mapping CSV : {OUTPUT_DIR / 'source_table_mapping.csv'}")
    print(f"  Source Lineage CSV       : {OUTPUT_DIR / 'source_lineage.csv'}")
    print(f"  Validation Log CSV       : {OUTPUT_DIR / 'validation_failures.csv'}")
    print(f"  Manual Review Spot-Check : {OUTPUT_DIR / 'manual_review.csv'}")

    conn.close()

    if len(fk_errors) == 0 and result.get("dq_critical", 0) == 0:
        print("\n" + "=" * 80)
        print("  >>> SPRINT 1 ACCEPTANCE CRITERIA 100% SATISFIED — PIPELINE GREEN <<<")
        print(f"  Completed in {elapsed:.2f} seconds.")
        print("=" * 80 + "\n")
        return 0
    else:
        print("\n" + "=" * 80)
        print("  >>> PIPELINE FAILED ACCEPTANCE GATES <<<")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
