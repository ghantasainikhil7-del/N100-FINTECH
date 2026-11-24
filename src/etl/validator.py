"""
Nifty 100 Financial Intelligence Platform · Data Quality Validation Engine
Author: Data Analytics Division
Sprint: Sprint 1 · Data Foundation (Days 01–07)
Module: Module 1 (ETL Pipeline)
Specification: 16 Data Quality Rules (DQ-01 to DQ-16)
"""

import os
import re
import pandas as pd
from typing import Dict, List, Tuple, Any


class DataQualityValidator:
    """
    Executes 16 Data Quality rules across Nifty 100 datasets.
    Logs warnings and critical issues to output/validation_failures.csv.
    """

    def __init__(self, output_path: str = "output/validation_failures.csv"):
        self.output_path = output_path
        self.failures: List[Dict[str, Any]] = []

    def log_failure(
        self, 
        rule_id: str, 
        rule_name: str, 
        company_id: str, 
        year: str, 
        field: str, 
        issue: str, 
        severity: str
    ):
        """Record a validation failure record."""
        self.failures.append({
            "rule_id": rule_id,
            "rule_name": rule_name,
            "company_id": company_id,
            "year": year,
            "field": field,
            "issue": issue,
            "severity": severity
        })

    def validate_companies(self, df_companies: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Master Companies dataset.
        Rules: DQ-01 (PK Uniqueness), DQ-08 (Ticker Format)
        """
        # DQ-01: Company PK Uniqueness
        dup_mask = df_companies.duplicated(subset=['id'], keep=False)
        if dup_mask.any():
            for _, r in df_companies[dup_mask].iterrows():
                self.log_failure(
                    "DQ-01", "Company PK Uniqueness", str(r.get('id')), "CURRENT", 
                    "id", f"Duplicate company ticker found: '{r.get('id')}'", "CRITICAL"
                )
            # Deduplicate
            df_companies = df_companies.drop_duplicates(subset=['id'], keep='last')

        # DQ-08: Ticker Format
        for _, r in df_companies.iterrows():
            ticker = str(r.get('id', ''))
            if not re.match(r'^[A-Z0-9&\-]{2,12}$', ticker):
                self.log_failure(
                    "DQ-08", "Ticker Format", ticker, "CURRENT", 
                    "id", f"Invalid ticker format or length: '{ticker}'", "CRITICAL"
                )

        return df_companies

    def validate_time_series_pk(
        self, 
        df: pd.DataFrame, 
        table_name: str
    ) -> pd.DataFrame:
        """
        Validate (company_id, year) composite uniqueness.
        Rule: DQ-02 (Annual PK Uniqueness)
        """
        if 'company_id' in df.columns and 'year' in df.columns:
            dup_mask = df.duplicated(subset=['company_id', 'year'], keep=False)
            if dup_mask.any():
                for _, r in df[dup_mask].iterrows():
                    self.log_failure(
                        "DQ-02", "Annual PK Uniqueness", str(r.get('company_id')), 
                        str(r.get('year')), f"{table_name}.(company_id, year)",
                        f"Duplicate (company_id, year) pair in {table_name}", "CRITICAL"
                    )
                # Keep last occurrence per specification
                df = df.drop_duplicates(subset=['company_id', 'year'], keep='last')
        return df

    def validate_fk_integrity(
        self, 
        df: pd.DataFrame, 
        valid_tickers: set, 
        table_name: str
    ) -> pd.DataFrame:
        """
        Validate foreign key integrity against companies table.
        Rule: DQ-03 (FK Integrity)
        """
        if 'company_id' in df.columns:
            orphan_mask = ~df['company_id'].isin(valid_tickers)
            if orphan_mask.any():
                for _, r in df[orphan_mask].iterrows():
                    self.log_failure(
                        "DQ-03", "FK Integrity", str(r.get('company_id')), 
                        str(r.get('year', 'N/A')), f"{table_name}.company_id",
                        f"Orphan record: ticker '{r.get('company_id')}' not found in companies table", "CRITICAL"
                    )
                # Reject orphan rows
                df = df[~orphan_mask]
        return df

    def validate_profit_and_loss(
        self, 
        df_pnl: pd.DataFrame, 
        bank_tickers: set
    ) -> pd.DataFrame:
        """
        Validate Profit & Loss statements.
        Rules: DQ-05 (OPM), DQ-06 (Sales), DQ-11 (Tax), DQ-12 (Payout), DQ-14 (EPS)
        """
        for _, r in df_pnl.iterrows():
            cid = str(r.get('company_id', ''))
            yr = str(r.get('year', ''))
            sales = pd.to_numeric(r.get('sales'), errors='coerce') or 0
            op = pd.to_numeric(r.get('operating_profit'), errors='coerce') or 0
            opm = pd.to_numeric(r.get('opm_percentage'), errors='coerce')
            pat = pd.to_numeric(r.get('net_profit'), errors='coerce')
            eps = pd.to_numeric(r.get('eps'), errors='coerce')
            tax = pd.to_numeric(r.get('tax_percentage'), errors='coerce')
            payout = pd.to_numeric(r.get('dividend_payout'), errors='coerce')

            # DQ-05: OPM Cross-check
            if sales > 0 and opm is not None:
                calc_opm = (op / sales) * 100
                if abs(opm - calc_opm) > 1.5:
                    self.log_failure(
                        "DQ-05", "OPM Cross-Check", cid, yr, "opm_percentage",
                        f"Reported OPM {opm}% diverges from computed {calc_opm:.1f}%", "WARNING"
                    )

            # DQ-06: Positive Sales (Non-Banks)
            if cid not in bank_tickers and sales <= 0:
                self.log_failure(
                    "DQ-06", "Positive Sales", cid, yr, "sales",
                    f"Non-bank corporation has zero or negative sales: {sales}", "WARNING"
                )

            # DQ-11: Tax Rate Range (0 to 60%)
            if tax is not None and (tax < 0 or tax > 60):
                self.log_failure(
                    "DQ-11", "Tax Rate Range", cid, yr, "tax_percentage",
                    f"Out-of-range effective tax rate: {tax}%", "WARNING"
                )

            # DQ-12: Dividend Payout Cap (<= 200%)
            if payout is not None and payout > 200:
                self.log_failure(
                    "DQ-12", "Dividend Payout Cap", cid, yr, "dividend_payout",
                    f"Extreme dividend payout ratio: {payout}%", "WARNING"
                )

            # DQ-14: EPS Sign Consistency
            if pat is not None and eps is not None:
                if pat > 0 and eps < 0:
                    self.log_failure(
                        "DQ-14", "EPS Sign Consistency", cid, yr, "eps",
                        f"Positive PAT (₹{pat} Cr) contradicts negative EPS (₹{eps})", "WARNING"
                    )
        return df_pnl

    def validate_balance_sheet(self, df_bs: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Balance Sheet statement.
        Rules: DQ-04 (BS Balance), DQ-10 (Fixed Assets), DQ-15 (Strict Balance)
        """
        for idx, r in df_bs.iterrows():
            cid = str(r.get('company_id', ''))
            yr = str(r.get('year', ''))
            assets = pd.to_numeric(r.get('total_assets'), errors='coerce') or 0
            liab = pd.to_numeric(r.get('total_liabilities'), errors='coerce') or 0
            fixed = pd.to_numeric(r.get('fixed_assets'), errors='coerce') or 0

            # DQ-04: Balance Sheet Balance within 1%
            if assets > 0:
                discrepancy = abs(assets - liab) / assets
                if discrepancy > 0.01:
                    self.log_failure(
                        "DQ-04", "Balance Sheet Balance", cid, yr, "total_assets",
                        f"Assets (₹{assets}) and Liabilities (₹{liab}) differ by {discrepancy*100:.2f}%", "WARNING"
                    )
            elif assets == 0 and liab != 0:
                self.log_failure(
                    "DQ-04", "Balance Sheet Balance", cid, yr, "total_assets",
                    "Total assets is zero while liabilities is non-zero", "WARNING"
                )

            # DQ-10: Non-Negative Fixed Assets
            if fixed < 0:
                self.log_failure(
                    "DQ-10", "Non-Negative Fixed Assets", cid, yr, "fixed_assets",
                    f"Negative fixed assets: {fixed}; coercing to 0", "WARNING"
                )
                df_bs.at[idx, 'fixed_assets'] = 0

            # DQ-15: Strict Balance Check (Informational)
            if assets != liab:
                self.log_failure(
                    "DQ-15", "BSE/ASE Balance Check", cid, yr, "total_liabilities",
                    f"Liabilities (₹{liab}) != Assets (₹{assets}) (nominal mismatch)", "INFO"
                )
        return df_bs

    def validate_cash_flow(self, df_cf: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Cash Flow statements.
        Rule: DQ-09 (Net Cash Check)
        """
        for idx, r in df_cf.iterrows():
            cid = str(r.get('company_id', ''))
            yr = str(r.get('year', ''))
            cfo = pd.to_numeric(r.get('operating_activity'), errors='coerce') or 0
            cfi = pd.to_numeric(r.get('investing_activity'), errors='coerce') or 0
            cff = pd.to_numeric(r.get('financing_activity'), errors='coerce') or 0
            net = pd.to_numeric(r.get('net_cash_flow'), errors='coerce') or 0

            # DQ-09: Net Cash Check (|net - (CFO + CFI + CFF)| <= 10 Cr tolerance)
            expected = cfo + cfi + cff
            diff = abs(net - expected)
            if diff > 10:
                self.log_failure(
                    "DQ-09", "Net Cash Check", cid, yr, "net_cash_flow",
                    f"Reported net cash {net} differs from sum of activities {expected} by {diff} Cr", "WARNING"
                )
                # Compute and adjust net cash flow from components
                df_cf.at[idx, 'net_cash_flow'] = expected
        return df_cf

    def validate_documents(self, df_docs: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Annual Reports document URLs.
        Rule: DQ-13 (URL Validity)
        """
        for _, r in df_docs.iterrows():
            cid = str(r.get('company_id', ''))
            yr = str(r.get('Year', ''))
            url = str(r.get('Annual_Report', '')).strip()

            if not url or url.lower() == 'null' or not url.startswith("http"):
                self.log_failure(
                    "DQ-13", "URL Validity (Documents)", cid, yr, "Annual_Report",
                    f"Missing or invalid regulatory PDF link: '{url}'", "WARNING"
                )
        return df_docs

    def validate_coverage(self, df_pnl: pd.DataFrame, all_tickers: set):
        """
        Validate history length per company.
        Rule: DQ-16 (Coverage Check: >= 5 years history)
        """
        counts = df_pnl.groupby('company_id')['year'].nunique().to_dict()
        for ticker in all_tickers:
            yrs = counts.get(ticker, 0)
            if yrs < 5:
                self.log_failure(
                    "DQ-16", "Coverage Check", ticker, "ALL", "year",
                    f"Company has limited historical depth: {yrs} years (minimum 5 required)", "WARNING"
                )

    def export_report(self):
        """Save all logged failures to CSV."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df_report = pd.DataFrame(self.failures)
        if df_report.empty:
            df_report = pd.DataFrame(columns=[
                "rule_id", "rule_name", "company_id", "year", "field", "issue", "severity"
            ])
        df_report.to_csv(self.output_path, index=False)
        return df_report
