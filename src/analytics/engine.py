"""Financial Ratio Engine Orchestrator (Sprint 2 entry point).

Maintains complete backwards compatibility with existing pipelines and make targets
by wrapping the full RatioEngine implementation in src.analytics.ratio_engine.
"""
from __future__ import annotations

import logging
from src.analytics.ratio_engine import RatioEngine

logger = logging.getLogger(__name__)

__all__ = ["RatioEngine"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engine = RatioEngine()
    result = engine.run()
    logger.info("Engine completed successfully: %s", result)
