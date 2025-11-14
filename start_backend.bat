@echo off
setlocal

REM Resolve repository root
set "ROOT=%~dp0"
cd /d "%ROOT%backend" || (
  echo [ERROR] Could not change directory to backend folder.
  pause
  exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
  echo [INFO] Creating Python virtual environment...
  py -3 -m venv venv || (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
  )
)

call "venv\Scripts\activate.bat"

echo [INFO] Ensuring backend dependencies are installed...
pip install --upgrade pip >nul
pip install -r requirements.txt >nul

echo.
echo [INFO] Starting FastAPI server on http://127.0.0.1:8000
echo [INFO] Press CTRL+C to stop the server.
uvicorn app.main:app --reload

endlocal

