"""Sprint 3 Execution Script: Screener, Peer Rankings, Radar Charts, and Excel Exports."""
import logging
import sqlite3
from pathlib import Path
from src.analytics.peer import PeerComparisonEngine
from src.reports.radar import RadarChartGenerator
from src.screener.engine import ScreenerEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sprint3_runner")


def run_sprint3() -> None:
    logger.info("Starting Sprint 3 Generation: Screener & Peer Comparison...")

    # 1. Screener Generation & Excel Export
    logger.info("Initializing Screener Engine...")
    screener = ScreenerEngine()
    screener.load_universe()
    screener_file = screener.export_screener_excel()
    logger.info("Generated %s successfully.", screener_file)

    # 2. Peer Comparison Percentiles & Excel Export
    logger.info("Computing Peer Percentiles & Generating Comparison Workbook...")
    peer_engine = PeerComparisonEngine()
    peer_engine.compute_peer_percentiles()
    peer_file = peer_engine.export_peer_comparison_excel()
    logger.info("Generated %s successfully.", peer_file)

    # 3. Radar Chart Visualizations
    logger.info("Generating Radar Charts for all companies...")
    radar_gen = RadarChartGenerator()
    chart_count = radar_gen.generate_all_radar_charts()
    logger.info("Generated %d radar charts in reports/radar_charts/", chart_count)

    logger.info("Sprint 3 Generation Finished Successfully!")


if __name__ == "__main__":
    run_sprint3()
