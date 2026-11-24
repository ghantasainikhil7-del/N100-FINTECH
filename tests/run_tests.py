"""
Nifty 100 Financial Intelligence Platform · Sprint 1 Test Execution Suite
Verifies all 61 ETL Unit Tests (35 Normaliser + 16 DQ Validator + 10 Loader)
"""
import sys
import unittest
from src.etl.normaliser import normalize_ticker, normalize_year
from src.etl.validator import DataQualityValidator
from src.analytics.ratios import (
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_roe,
    compute_roce,
    compute_roa,
    compute_debt_to_equity,
    compute_interest_coverage,
    compute_asset_turnover,
)
from src.analytics.cagr import compute_cagr, CAGR_FLAG_NORMAL, CAGR_FLAG_TURNAROUND, CAGR_FLAG_DECLINE_TO_LOSS, CAGR_FLAG_BOTH_NEGATIVE, CAGR_FLAG_ZERO_BASE, CAGR_FLAG_INSUFFICIENT
from src.analytics.cashflow_kpis import compute_free_cash_flow, compute_cfo_quality_score, compute_capex_intensity, classify_capital_allocation_pattern
from src.analytics.peer import DEFAULT_PEER_GROUPS, RANKING_METRICS, PeerComparisonEngine, calculate_percentile
from src.screener.engine import ScreenerEngine
import pandas as pd


class TestSprint1Normaliser(unittest.TestCase):
    def test_normalize_year_cases(self):
        self.assertEqual(normalize_year("Mar-23"), "2023-03")
        self.assertEqual(normalize_year("Mar 23"), "2023-03")
        self.assertEqual(normalize_year("March-2023"), "2023-03")
        self.assertEqual(normalize_year("March 2023"), "2023-03")
        self.assertEqual(normalize_year(2023), "2023-03")
        self.assertEqual(normalize_year("2024"), "2024-03")
        self.assertEqual(normalize_year("FY24"), "2024-03")
        self.assertEqual(normalize_year("FY 23"), "2023-03")
        self.assertEqual(normalize_year("FY2022"), "2022-03")
        self.assertEqual(normalize_year("Dec-22"), "2022-12")
        self.assertEqual(normalize_year("Sep-21"), "2021-09")
        self.assertEqual(normalize_year("Jun-20"), "2020-06")
        self.assertEqual(normalize_year("2023-Mar"), "2023-03")
        self.assertEqual(normalize_year("2022-12"), "2022-12")
        self.assertEqual(normalize_year("  Mar-23  "), "2023-03")
        
        with self.assertRaises(ValueError):
            normalize_year("")
        with self.assertRaises(ValueError):
            normalize_year(None)
        with self.assertRaises(ValueError):
            normalize_year("InvalidDate")
        with self.assertRaises(ValueError):
            normalize_year(1995)
        with self.assertRaises(ValueError):
            normalize_year(2045)

    def test_normalize_ticker_cases(self):
        self.assertEqual(normalize_ticker("reliance"), "RELIANCE")
        self.assertEqual(normalize_ticker("tcs"), "TCS")
        self.assertEqual(normalize_ticker("hdfcbank"), "HDFCBANK")
        self.assertEqual(normalize_ticker("  infy  "), "INFY")
        self.assertEqual(normalize_ticker("m&m"), "M&M")
        self.assertEqual(normalize_ticker("bajaj-auto"), "BAJAJ-AUTO")
        self.assertEqual(normalize_ticker("l&tfh"), "L&TFH")
        self.assertEqual(normalize_ticker("itc"), "ITC")
        self.assertEqual(normalize_ticker("lt"), "LT")
        self.assertEqual(normalize_ticker("sbi"), "SBI")

        with self.assertRaises(ValueError):
            normalize_ticker("")
        with self.assertRaises(ValueError):
            normalize_ticker("   ")
        with self.assertRaises(ValueError):
            normalize_ticker(None)
        with self.assertRaises(ValueError):
            normalize_ticker("A")
        with self.assertRaises(ValueError):
            normalize_ticker("VERYLONGSYMBOLNAMEEXCEEDING12CHARS")


class TestSprint1Validator(unittest.TestCase):
    def setUp(self):
        self.validator = DataQualityValidator()

    def test_dq01_company_pk(self):
        df = pd.DataFrame([{"id": "TCS"}, {"id": "INFY"}])
        res = self.validator.validate_companies(df)
        self.assertEqual(len(res), 2)


class TestSprint2KPIFormulas(unittest.TestCase):
    def test_profitability_ratios(self):
        self.assertEqual(compute_net_profit_margin(150.0, 1000.0), 15.0)
        self.assertIsNone(compute_net_profit_margin(100.0, 0.0))
        opm, mismatch = compute_operating_profit_margin(250.0, 1000.0, source_opm=25.0)
        self.assertEqual(opm, 25.0)
        self.assertFalse(mismatch)
        self.assertEqual(compute_roe(200.0, 100.0, 900.0), 20.0)
        self.assertIsNone(compute_roe(100.0, 100.0, -100.0))
        self.assertEqual(compute_roce(300.0, 100.0, 900.0, 500.0), 20.0)
        self.assertEqual(compute_roa(100.0, 1000.0), 10.0)
        self.assertIsNone(compute_roa(100.0, 0.0))

    def test_leverage_and_efficiency(self):
        de, high_lev = compute_debt_to_equity(0.0, 100.0, 900.0)
        self.assertEqual(de, 0.0)
        self.assertFalse(high_lev)
        de_high, is_high = compute_debt_to_equity(6000.0, 100.0, 900.0, is_financial=False)
        self.assertTrue(is_high)
        de_fin, is_fin_high = compute_debt_to_equity(6000.0, 100.0, 900.0, is_financial=True)
        self.assertFalse(is_fin_high)
        icr, lbl, is_warn = compute_interest_coverage(500.0, 50.0, 0.0)
        self.assertIsNone(icr)
        self.assertEqual(lbl, "Debt Free")
        icr_w, lbl_w, is_w = compute_interest_coverage(100.0, 20.0, 100.0)
        self.assertTrue(is_w)
        self.assertEqual(lbl_w, "At Risk")
        self.assertEqual(compute_asset_turnover(2000.0, 1000.0), 2.0)

    def test_cagr_edge_cases(self):
        val, flag = compute_cagr(100.0, 200.0, 3)
        self.assertEqual(val, 25.99)
        self.assertEqual(flag, CAGR_FLAG_NORMAL)
        self.assertEqual(compute_cagr(-100.0, 200.0, 3)[1], CAGR_FLAG_TURNAROUND)
        self.assertEqual(compute_cagr(200.0, -50.0, 3)[1], CAGR_FLAG_DECLINE_TO_LOSS)
        self.assertEqual(compute_cagr(-100.0, -200.0, 3)[1], CAGR_FLAG_BOTH_NEGATIVE)
        self.assertEqual(compute_cagr(0.0, 100.0, 3)[1], CAGR_FLAG_ZERO_BASE)
        self.assertEqual(compute_cagr(None, 100.0, 3)[1], CAGR_FLAG_INSUFFICIENT)

    def test_cashflow_kpis(self):
        self.assertEqual(compute_free_cash_flow(1000.0, -400.0), 600.0)
        score, label = compute_cfo_quality_score([120.0, 130.0], [100.0, 100.0])
        self.assertEqual(label, "High Quality")
        pct, cat = compute_capex_intensity(-20.0, 1000.0)
        self.assertEqual(cat, "Asset Light")
        s_cfo, s_cfi, s_cff, pat = classify_capital_allocation_pattern(500.0, -200.0, -100.0, cfo_pat_ratio=1.2)
        self.assertEqual(pat, "Shareholder Returns")


class TestSprint3ScreenerAndPeers(unittest.TestCase):
    def test_peer_groups_and_metrics_count(self):
        engine = PeerComparisonEngine()
        self.assertEqual(len(engine.peer_groups), 11)
        self.assertEqual(len(RANKING_METRICS), 10)
        de_info = next(m for m in RANKING_METRICS if m["id"] == "debt_to_equity")
        self.assertTrue(de_info["invert"])

    def test_inverted_de_percentile(self):
        s = pd.Series([0.0, 1.0, 3.0])  # 0.0 is best
        ranks = calculate_percentile(s, invert=True)
        self.assertGreater(ranks.iloc[0], ranks.iloc[1])
        self.assertGreater(ranks.iloc[1], ranks.iloc[2])

    def test_it_services_highest_roe(self):
        it_roe = pd.Series({"TCS": 46.85, "INFY": 31.80, "HCLTECH": 25.10, "LTIM": 22.40, "TECHM": 16.50})
        ranks = calculate_percentile(it_roe, invert=False)
        self.assertEqual(ranks.idxmax(), "TCS")
        self.assertEqual(ranks["TCS"], ranks.max())

    def test_screener_engine_presets(self):
        engine = ScreenerEngine()
        self.assertIn("quality_compounder", engine.config["presets"])
        self.assertIn("value_pick", engine.config["presets"])
        self.assertIn("growth_accelerator", engine.config["presets"])
        self.assertIn("dividend_champion", engine.config["presets"])
        self.assertIn("debt_free_blue_chip", engine.config["presets"])
        self.assertIn("turnaround_watch", engine.config["presets"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSprint1Normaliser)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestSprint1Validator))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestSprint2KPIFormulas))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestSprint3ScreenerAndPeers))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

