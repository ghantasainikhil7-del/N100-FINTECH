@echo off
title N100 Financial Intelligence Platform
echo ===================================================
echo   N100 Financial Intelligence Platform
echo ===================================================
echo Starting Streamlit Dashboard on http://localhost:8501...
echo.
set PYTHONPATH=%~dp0;%PYTHONPATH%
"%~dp0venv\Scripts\streamlit.exe" run "%~dp0app.py"
pause
