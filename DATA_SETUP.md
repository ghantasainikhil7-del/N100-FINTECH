# NIFTY 100 Financial Intelligence Platform — Data Setup & Architecture Guide

> **Data Foundation — ETL Pipeline, Data Quality Validation & SQLite Database**  
> *Target Database:* `data/nifty100.db` (with root mirror `nifty100.db`)  
> *Scope:* 12 Source Datasets, 11 Relational Domain Tables, 16 Data Quality (DQ) Rules, 0 Critical DQ Failures, 0 FK Violations.

---

## 1. Executive Summary

This architecture guide establishes the production data foundation for the **Nifty 100 Financial Intelligence Platform**. The automated ETL pipeline ingests, normalizes, validates, and loads 10–14 years of financial statement and market data across 92 Nifty 100 constituents into a relational SQLite database.

```text
┌────────────────────────────────────────────────────────┐
│             12 Source Datasets (Excel)                 │
│  7 Core Datasets (header=1) + 5 Supplementary (header=0) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             File Discovery & Download Engine           │
│  Auto-resolves local files / downloads from CDN        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Normalization & Sanitization               │
│  • normalize_year (YYYY-MM, handles '23-Mar', FY, etc.)│
│  • normalize_ticker (uppercase, 2-12 chars, &, -)      │
│  • clean_numeric (coerces ₹ Cr, handles negatives)    │
│  • Clean non-annual TTM interim rows                   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             16 Data Quality (DQ) Rules Engine          │
│  • Critical (DQ-01, DQ-02, DQ-03, DQ-07, DQ-08)        │
│  • Warning  (DQ-04, DQ-05, DQ-06, DQ-09, DQ-10, etc.) │
│  • Info     (DQ-15)                                    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             SQLite Relational Database                 │
│  • 11 Core Domain Tables                               │
│  • PRAGMA foreign_keys = ON;                           │
│  • 0 Foreign Key Violations                            │
└────────────────────────────────────────────────────────┘
```
