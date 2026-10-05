@echo off
echo ================================================================
echo Starting Local GitHub Repository Code Explainer Full Stack
echo ================================================================
start "FastAPI Backend" cmd /k "python run_backend.py"
timeout /t 3 /nobreak >nul
start "Streamlit Frontend" cmd /k "python run_frontend.py"
echo Both Backend and Frontend launched!
