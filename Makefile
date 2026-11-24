# Nifty 100 Financial Intelligence Platform Makefile
# Production Automation for ETL, Testing, Reports, and FastAPI REST Backend

.PHONY: help install load ratios test report api clean

help:
	@echo "Nifty 100 Financial Intelligence Platform"
	@echo "=========================================="
	@echo "make install    : Install virtual environment and all requirements"
	@echo "make load       : Execute ETL pipeline to load all 12 files into SQLite nifty100.db"
	@echo "make ratios     : Run Financial Ratio Engine to compute 30+ KPIs"
	@echo "make test       : Execute pytest test suite"
	@echo "make report     : Generate PDF tearsheets and sector dossiers"
	@echo "make api        : Launch FastAPI REST server on port 8000"
	@echo "make clean      : Remove cache, temporary files, and test artifacts"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

load:
	python -m src.etl.loader

ratios:
	python -m src.analytics.ratios

test:
	pytest tests/ -v

report:
	python -m src.reports.portfolio_report

api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
