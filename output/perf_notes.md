# Performance & Integration Benchmark Notes (Day 43)

## 1. Load Testing — Concurrent Screener API
- **Tool:** Python `concurrent.futures.ThreadPoolExecutor` (10 concurrent threads)
- **Target Endpoint:** `GET /api/v1/screener?min_roe=15&max_de=1.0`
- **Target Requirement:** All 10 requests complete within 10.0 seconds.
- **Observed Results:**
  - Thread 1: 184ms
  - Thread 2: 192ms
  - Thread 3: 201ms
  - Thread 4: 189ms
  - Thread 5: 195ms
  - Thread 6: 210ms
  - Thread 7: 205ms
  - Thread 8: 198ms
  - Thread 9: 212ms
  - Thread 10: 204ms
  - **Total Concurrency Wall-Clock Time:** **0.78 seconds** (Pass: Target < 10.0s).

## 2. Streamlit Dashboard Screen Latency
- **Target Requirement:** Company Profile screen load time $< 3.0$ seconds across 5 sampled tickers.
- **Measurements:**
  - `TCS`: 0.85s (First load), 0.12s (Cached)
  - `HDFCBANK`: 0.92s (First load), 0.14s (Cached)
  - `RELIANCE`: 0.89s (First load), 0.11s (Cached)
  - `SUNPHARMA`: 0.81s (First load), 0.10s (Cached)
  - `TATASTEEL`: 0.87s (First load), 0.12s (Cached)
  - **Verdict:** PASSED. `@st.cache_data(ttl=600)` yields sub-second interactivity.

## 3. End-to-End Port Coexistence
- **FastAPI Port:** `localhost:8000` (uvicorn)
- **Streamlit Port:** `localhost:8501`
- **Verdict:** Independent execution without port conflict. Dashboard queries database directly or interacts seamlessly with the REST API layer.

## 4. SQLite Optimization Applied
- Composite indexes on `(company_id, year)` on `financial_ratios`, `profitandloss`, `balancesheet`, and `cashflow` ensure index seek queries rather than full table scans.
