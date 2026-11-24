"""Unit tests for Peer Comparison Engine (11 peer groups, inverted D/E, 10 metrics, percentiles)."""
import numpy as np
import pandas as pd
import pytest
from src.analytics.peer import DEFAULT_PEER_GROUPS, RANKING_METRICS, PeerComparisonEngine, calculate_percentile


def test_peer_groups_definition_count():
    """Verify all 11 peer groups are defined with valid benchmarks."""
    engine = PeerComparisonEngine()
    assert len(engine.peer_groups) == 11
    expected_groups = [
        "Private Banks", "Public Banks", "IT Services", "Pharmaceuticals",
        "Automobiles", "Life Insurance", "Oil & Gas", "Power & Utilities",
        "Steel & Metals", "FMCG", "Consumer Finance"
    ]
    for g in expected_groups:
        assert g in engine.peer_groups
        assert "benchmark" in engine.peer_groups[g]
        assert "members" in engine.peer_groups[g]


def test_ranking_metrics_count():
    """Verify exactly 10 ranking metrics are specified with D/E inverted."""
    assert len(RANKING_METRICS) == 10
    metric_ids = [m["id"] for m in RANKING_METRICS]
    assert "return_on_equity_pct" in metric_ids
    assert "return_on_capital_employed_pct" in metric_ids
    assert "net_profit_margin_pct" in metric_ids
    assert "debt_to_equity" in metric_ids
    assert "free_cash_flow_cr" in metric_ids
    assert "pat_cagr_5yr" in metric_ids
    assert "revenue_cagr_5yr" in metric_ids
    assert "eps_cagr_5yr" in metric_ids
    assert "interest_coverage" in metric_ids
    assert "asset_turnover" in metric_ids

    # D/E must be inverted
    de_info = next(m for m in RANKING_METRICS if m["id"] == "debt_to_equity")
    assert de_info["invert"] is True


def test_peer_group_lookup():
    """Lookup peer group name by ticker."""
    engine = PeerComparisonEngine()
    assert engine.get_peer_group_for_ticker("TCS") == "IT Services"
    assert engine.get_peer_group_for_ticker("INFY") == "IT Services"
    assert engine.get_peer_group_for_ticker("HDFCBANK") == "Private Banks"
    assert engine.get_peer_group_for_ticker("RELIANCE") == "Oil & Gas"
    assert engine.get_peer_group_for_ticker("UNASSIGNED_XYZ") is None


def test_unassigned_ticker_handling():
    """Unassigned companies return clean status without raising exceptions."""
    engine = PeerComparisonEngine()
    res = engine.get_company_peer_analysis("UNASSIGNED_TICKER")
    assert res["status"] == "NO_PEER_GROUP"
    assert "No peer group assigned" in res["message"]


def test_inverted_de_logic():
    """Inverted percentile ranking ensures lower D/E produces higher percentile."""
    s = pd.Series([0.0, 1.0, 3.0])  # 0.0 is best, 3.0 is worst
    ranks = calculate_percentile(s, invert=True)
    assert ranks.iloc[0] > ranks.iloc[1] > ranks.iloc[2]
    # D/E = 0.0 gets highest percentile
    assert ranks.iloc[0] >= 0.66


def test_positive_metric_percentile_logic():
    """Standard higher-is-better metrics produce higher percentiles for higher values."""
    s = pd.Series([10.0, 20.0, 30.0])  # 30.0 is best
    ranks = calculate_percentile(s, invert=False)
    assert ranks.iloc[2] > ranks.iloc[1] > ranks.iloc[0]


def test_it_services_highest_roe_percentile_rank():
    """Within IT Services peer group, company with highest ROE has highest ROE percentile rank."""
    # IT Services sample members: TCS (highest ROE ~46%), INFY (~32%), HCLTECH (~25%), TECHM (~16%), LTIM (~22%)
    it_members_roe = pd.Series({
        "TCS": 46.85,
        "INFY": 31.80,
        "HCLTECH": 25.10,
        "LTIM": 22.40,
        "TECHM": 16.50,
    })
    ranks = calculate_percentile(it_members_roe, invert=False)
    # Highest ROE company (TCS) must have the highest percentile rank
    assert ranks.idxmax() == "TCS"
    assert ranks["TCS"] == ranks.max()
    assert ranks["TCS"] >= ranks["INFY"] >= ranks["HCLTECH"]
