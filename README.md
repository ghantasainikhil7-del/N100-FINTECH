# Nifty 100 Financial Intelligence Platform (N100)

> **Production-Grade Fundamental Analytics & Multibagger Screener for 92 Nifty 100 Companies**  
> *Full-Stack Architecture: React 18 (Vite + Tailwind CSS + Lucide) + FastAPI Backend + SQLite Relational Engine*  
> *All monetary values standardized in ₹ Crore*

---

## 📌 Executive Summary

The **N100 Financial Intelligence Platform** is an institutional-grade investment research system built for equity analysts, portfolio managers, and fundamental investors. It transforms 10–13 years of audited annual financial filings across 92 premier Nifty 100 constituents into automated quantitative analytics, dynamic multibagger screener filters, composite health scores (0–100), automated PDF tearsheet generation, and peer comparison radar insights.

---

## 🚀 Quickstart: How to Run the Project

Running the project requires **two terminal windows**: one for the **FastAPI Backend** and one for the **React Frontend**.

### Prerequisites
- **Python 3.10+** (with virtual environment)
- **Node.js 18+** & **npm**

---

### Step 1: Start the Backend (FastAPI REST Server)

1. Open your terminal in the project root folder (`Bluestock project N100`):
   ```powershell
   # Activate Python Virtual Environment
   .\.venv\Scripts\Activate.ps1
   ```
2. Verify dependencies are installed:
   ```powershell
   pip install -r requirements.txt
   ```
3. Launch the FastAPI server:
   ```powershell
   python -m uvicorn src.api.main:app --port 8000 --reload
   ```
   - 🌐 **API Base:** `http://127.0.0.1:8000`
   - 📑 **Swagger Interactive Docs:** `http://127.0.0.1:8000/docs`
   - ⚡ **Redoc API Specification:** `http://127.0.0.1:8000/redoc`

---

### Step 2: Start the Frontend (React 18 + Vite)

1. Open a **second terminal tab** and navigate into the `frontend` folder:
   ```powershell
   cd frontend
   ```
2. Install npm dependencies (if not already installed):
   ```powershell
   npm install
   ```
3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   - 💻 **Web Application:** `http://localhost:3000` (or `http://localhost:5173`)

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CLIENT LAYER (Modern React 18)                       │
│  • Vite Bundler  • Tailwind CSS 3.4  • Recharts  • Lucide Icons        │
│  • iOS-Inspired Dark Design  • Stock Screener  • PDF Tearsheet Engine  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (JSON REST / Static Stream)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI Server)                         │
│  • Port 8000  • 16 REST Endpoints  • CORS Enabled  • Swagger UI Docs   │
│  • Uvicorn ASGI Engine  • Static File Mounting for PDF Reports        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  ANALYTICS & ETL PIPELINE (Python)                     │
│  • Source-to-Table Deterministic Mapping (12 Datasets)                 │
│  • 16 Automated Data Quality (DQ) Rules Engine                         │
│  • 50+ Financial KPIs: Altman Z-Score, Piotroski F-Score, CAGR, ROE   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER (SQLite Engine)                        │
│  • nifty100.db  • 11 Relational Tables with PRAGMA foreign_keys = ON   │
│  • 0 Foreign Key Violations  • Normalized Financial Statement Store    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Application Modules & Features

| Module | Route / Component | Features & Purpose |
| :--- | :--- | :--- |
| **1. Home Overview** | `HomeOverview.jsx` | Nifty 100 aggregate metrics, sector weight breakdowns, composite health distribution, and quick market insights. |
| **2. Stock Screener** | `StockScreener.jsx` | Multi-factor fundamental screener with sliders for ROE, P/E, Market Cap, Debt/Equity, and instant filter presets (Quality Compounders, Debt-Free Giants, Undervalued). Left-aligned clean table layout. |
| **3. Company Profile** | `CompanyProfile.jsx` | Deep-dive fundamental tearsheet for any of the 92 constituents: 10-year P&L, Balance Sheet, Cash Flow lifecycle (Dickinson matrix), valuation radar, and direct PDF downloads. |
| **4. Peer Comparison** | `PeerComparison.jsx` | Cross-sectional cohort benchmarking across industry clusters with percentile rankings. |
| **5. Trend Analysis** | `TrendAnalysis.jsx` | Multi-year historical growth trajectories (Revenue, EBITDA, PAT margins, Free Cash Flow). |
| **6. Sector Analysis** | `SectorAnalysis.jsx` | Sector-wise concentration, median ROE, and aggregate market capitalization distribution. |
| **7. Capital Allocation** | `CapitalAllocation.jsx` | Capex vs. Operating Cash Flow analysis, dividend payout ratio, and reinvestment efficiency. |
| **8. Annual Reports** | `AnnualReports.jsx` | Centralized repository with direct one-click PDF downloads for statutory filings, financial tearsheets, and sector dossiers. |
| **9. Executive Dashboard** | `ExecutiveDashboard.jsx` | Institutional high-level surveillance, top compounders, and portfolio valuation percentiles. |

---

## 📊 Data Pipeline & Database Design

### 1. Ingested Datasets (12 Sources)
The platform integrates **7 Core Financial Statements** and **5 Supplementary Datasets** covering 92 companies:
- **Core:** `companies.xlsx`, `profitandloss.xlsx`, `balancesheet.xlsx`, `cashflow.xlsx`, `analysis.xlsx`, `documents.xlsx`, `prosandcons.xlsx`.
- **Supplementary:** `sectors.xlsx`, `stock_prices.xlsx`, `financial_ratios.xlsx`, `peer_groups.xlsx`, `company_master.csv`.

### 2. Relational Schema (`db/schema.sql` → `nifty100.db`)
- **Master Table:** `companies` (Primary Key: `id` / Ticker symbol).
- **Child Statement Tables:** `profitandloss`, `balancesheet`, `cashflow` (Composite PK: `company_id, year`).
- **Enrichment & Supporting Tables:** `sectors`, `analysis`, `documents`, `prosandcons`, `stock_prices`, `market_cap`, `peer_groups`, `financial_ratios`.
- **Referential Integrity:** 100% enforced via SQLite `PRAGMA foreign_keys = ON;` with cascade safety. Zero foreign key violations.

---

## 🔌 Core FastAPI Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/v1/health` | `GET` | Health check, uptime, and database table row counts |
| `/api/v1/companies` | `GET` | All 92 constituent companies with sector & metric filters |
| `/api/v1/companies/{ticker}` | `GET` | Detailed company profile and overview |
| `/api/v1/companies/{ticker}/pl` | `GET` | 10-year historical Profit & Loss statements |
| `/api/v1/companies/{ticker}/bs` | `GET` | 10-year historical Balance Sheet statements |
| `/api/v1/companies/{ticker}/cashflow`| `GET` | 10-year Cash Flow & Dickinson lifecycle stage |
| `/api/v1/companies/{ticker}/ratios` | `GET` | 30+ pre-calculated and derived financial ratios |
| `/api/v1/screener` | `GET` | Dynamic multi-parameter stock screening engine |
| `/api/v1/sectors` | `GET` | Aggregate sector metrics and constituents |
| `/api/v1/peers/{group_name}` | `GET` | Cross-sectional peer comparison cohort |
| `/api/v1/reports/tearsheet/{ticker}` | `GET` | Direct PDF download of 2-page company tearsheet |

---

## 📁 Repository & Submission Structure

```
Bluestock project N100/
│
├── 📁 frontend/                 # Modern React 18 Application (Vite + Tailwind)
│   ├── 📁 src/
│   │   ├── 📁 components/       # Reusable UI widgets & navigation
│   │   ├── 📁 context/          # Bluestock data provider & state
│   │   ├── 📁 pages/            # 11 Core analyst screens
│   │   └── 📁 data/             # Constituents & benchmark dataset
│   ├── 📄 package.json          # Node dependencies
│   └── 📄 vite.config.js        # Vite config with PDF streaming middleware
│
├── 📁 src/                      # Python Backend & Data Engine
│   ├── 📁 api/                  # FastAPI routers & REST server
│   │   ├── 📄 main.py           # Application entrypoint & static mount
│   │   └── 📁 routers/          # Endpoints (companies, screener, reports, etc.)
│   ├── 📁 etl/                  # ETL pipeline & data normalizers
│   │   ├── 📄 database.py       # SQLite connection manager
│   │   └── 📄 source_mapping.py # Deterministic source mapping
│   └── 📁 analytics/            # Financial ratios, scoring & clustering
│
├── 📁 db/                       # Database DDL
│   └── 📄 schema.sql            # SQLite relational domain schema
│
├── 📁 data/                     # Raw & processed source datasets
│   ├── 📁 raw/                  # 7 core statement Excel files
│   ├── 📁 supporting/           # 5 supplementary Excel/CSV files
│   └── 📄 nifty100.db           # Fully populated SQLite relational database
│
├── 📁 reports/                  # Generated PDF tearsheets & dossiers
├── 📁 tests/                    # Automated regression test suite (70+ unit tests)
├── 📄 requirements.txt          # Python dependencies
└── 📄 README.md                 # Complete platform documentation
```

---

## 🧪 Testing & Verification

Run automated backend tests using pytest:
```powershell
python -m pytest tests/ -v
```
All unit tests verify:
- Complete ingestion and schema validation across all 92 constituents.
- Foreign key constraint adherence (`PRAGMA foreign_key_check`).
- Financial ratio calculation integrity (ROE, Piotroski, D/E).
