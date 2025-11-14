@echo off
setlocal

set "ROOT=%~dp0"

echo [INFO] Launching TaskTrack backend and frontend in separate windows...
start "TaskTrack Backend" cmd /k "\"%ROOT%start_backend.bat\""
start "TaskTrack Frontend" cmd /k "\"%ROOT%start_frontend.bat\""

echo [INFO] Servers are starting. Close this window if you don't need it anymore.
pause

endlocal

