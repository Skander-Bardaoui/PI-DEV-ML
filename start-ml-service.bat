@echo off
echo ========================================
echo Starting ML Fraud Detection Service
echo ========================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn[standard] pydantic python-multipart scikit-learn imbalanced-learn pandas numpy psycopg2-binary python-dotenv httpx joblib loguru requests pydantic-settings

REM Create necessary directories
if not exist "logs\" mkdir logs
if not exist "models\" mkdir models

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    echo BACKEND_URL=http://localhost:3001 > .env
)

REM Start the service
echo.
echo ========================================
echo Starting ML Service on port 8000...
echo ========================================
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
