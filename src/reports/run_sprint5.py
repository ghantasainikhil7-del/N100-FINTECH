"""Sprint 5 Unified Orchestrator: NLP, Cash Flow Intelligence, and PDF Reporting."""
import logging
from src.analytics.cashflow_intelligence import CashFlowIntelligence
from src.nlp.parser import AnalysisParser
from src.nlp.pros_cons_generator import ProsConsGenerator
from src.reports.portfolio_report import PortfolioReportGenerator
from src.reports.sector_report import SectorReportGenerator
from src.reports.tearsheet import TearsheetGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sprint5_runner")


def run_sprint5() -> None:
    logger.info("==================================================================")
    logger.info("Starting Sprint 5: Intelligence, NLP, and Automated PDF Reports...")
    logger.info("==================================================================")

    # 1. NLP Analysis Parser
    logger.info("Step 1: Running NLP Analysis Text Parser...")
    parser = AnalysisParser()
    p_df, f_df = parser.parse_all_analysis_records()
    parser.cross_validate_cagr()
    logger.info("NLP Parsing completed: %d records parsed.", len(p_df))

    # 2. NLP Pros & Cons Generator
    logger.info("Step 2: Generating Auto Pros & Cons (12 Pro & 12 Con Rules)...")
    pc_gen = ProsConsGenerator()
    pc_df = pc_gen.generate_all_pros_cons()
    logger.info("Pros & Cons generation completed: %d entries generated.", len(pc_df))

    # 3. Cash Flow Intelligence
    logger.info("Step 3: Executing Cash Flow Intelligence Module...")
    cf_intel = CashFlowIntelligence()
    cf_res = cf_intel.run_analysis()
    logger.info("Cash Flow Intelligence completed: %s", cf_res)

    # 4. Company Tearsheet PDFs
    logger.info("Step 4: Generating 2-Page Company Tearsheets (ReportLab)...")
    tearsheet_gen = TearsheetGenerator()
    t_count, skipped = tearsheet_gen.generate_all_tearsheets()
    logger.info("Tearsheet generation complete: %d generated, %d skipped.", t_count, len(skipped))

    # 5. Sector PDF Reports
    logger.info("Step 5: Generating 11 Sector Intelligence PDF Reports...")
    sector_gen = SectorReportGenerator()
    s_count = sector_gen.generate_all_sector_reports()
    logger.info("Sector report generation complete: %d sector PDFs generated.", s_count)

    # 6. Portfolio Summary PDF
    logger.info("Step 6: Generating Master Portfolio Summary PDF...")
    port_gen = PortfolioReportGenerator()
    port_pdf = port_gen.generate_portfolio_pdf()
    logger.info("Master portfolio PDF generated at: %s", port_pdf)

    logger.info("==================================================================")
    logger.info("Sprint 5 Orchestration Completed Successfully!")
    logger.info("==================================================================")


if __name__ == "__main__":
    run_sprint5()
