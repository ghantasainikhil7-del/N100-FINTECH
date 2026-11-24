@echo off
title N100 Financial Intelligence Platform (Full Stack)
echo ===================================================
echo   N100 Platform: Dashboard + REST API Server
echo ===================================================
set PYTHONPATH=%~dp0;%PYTHONPATH%
echo 1. Starting FastAPI REST server (http://127.0.0.1:8000)...
start "N100 API Server" "%~dp0venv\Scripts\uvicorn.exe" src.api.main:app --host 127.0.0.1 --port 8000
echo 2. Starting Streamlit Dashboard (http://localhost:8501)...
"%~dp0venv\Scripts\streamlit.exe" run "%~dp0app.py"
pause
