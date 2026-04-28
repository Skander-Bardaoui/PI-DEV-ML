# ML Service - Windows Setup Guide

## Quick Start (Easiest Method)

### Option 1: Using the Batch Script (Recommended)

Simply double-click `start-ml-service.bat` or run:

```cmd
start-ml-service.bat
```

This will:
- Create virtual environment
- Install all dependencies
- Create necessary folders
- Start the ML service

### Option 2: Manual Setup

```powershell
# 1. Create virtual environment
py -m venv venv

# 2. Activate it
.\venv\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies one by one (faster than requirements.txt)
python -m pip install fastapi uvicorn[standard] pydantic python-multipart
python -m pip install scikit-learn imbalanced-learn pandas numpy
python -m pip install psycopg2-binary python-dotenv httpx joblib loguru requests
python -m pip install pydantic-settings

# 5. Create folders
mkdir logs
mkdir models

# 6. Create .env file
echo BACKEND_URL=http://localhost:3001 > .env

# 7. Start the service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

Once started, you should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting ML service v1.0.0
📊 Loading models from ./app/models/trained_models
✅ ML service ready
INFO:     Application startup complete.
```

## Test the Service

Open browser: http://localhost:8000/api/v1/health

You should see:
```json
{
  "status": "healthy",
  "fraud_model_loaded": true,
  "version": "1.0.0"
}
```

## Troubleshooting

### Python not found
- Install Python from https://www.python.org/downloads/
- Or use `py` instead of `python`

### Permission denied
- Run PowerShell as Administrator
- Or use Command Prompt instead

### Port 8000 already in use
Change the port in the start command:
```cmd
python -m uvicorn app.main:app --reload --port 8001
```

### Dependencies fail to install
Try installing them one by one:
```cmd
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install scikit-learn
# etc...
```

## Next Steps

After ML service is running:

1. Start Backend:
   ```cmd
   cd ..\PI-DEV-BACKEND
   npm run start:dev
   ```

2. Start Frontend:
   ```cmd
   cd ..\PI-DEV-FRONT
   npm run dev
   ```

3. Test fraud detection at http://localhost:5173
