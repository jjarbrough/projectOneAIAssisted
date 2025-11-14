@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%frontend" || (
  echo [ERROR] Could not change directory to frontend folder.
  pause
  exit /b 1
)

set "PORT=5173"
echo [INFO] Starting static server on http://127.0.0.1:%PORT%
echo [INFO] Press CTRL+C to stop the server.
py -3 -m http.server %PORT%

endlocal

