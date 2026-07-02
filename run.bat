@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [StartupSpark] Missing .venv. Create it first:
  echo   python -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  echo   .\.venv\Scripts\python.exe -m pip install -r api\requirements.txt
  pause
  exit /b 1
)

if not exist "ui\node_modules" (
  echo [StartupSpark] Missing ui\node_modules. Installing frontend dependencies...
  pushd ui
  call npm install
  if errorlevel 1 (
    popd
    echo [StartupSpark] npm install failed.
    pause
    exit /b 1
  )
  popd
)

set "API_PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /R /C:":8001 .*LISTENING"') do set "API_PORT_PID=%%P"
if defined API_PORT_PID (
  set "API_PORT_NAME=unknown"
  for /f "tokens=1 delims=," %%N in ('tasklist /FI "PID eq !API_PORT_PID!" /FO CSV /NH') do set "API_PORT_NAME=%%~N"
  echo [StartupSpark] Port 8001 is in use by PID !API_PORT_PID! (!API_PORT_NAME!^).
  echo [StartupSpark] Port 8001 is already in use. Stop the existing API server, then run this script again.
  pause
  exit /b 1
)

set "UI_PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /R /C:":5173 .*LISTENING"') do set "UI_PORT_PID=%%P"
if defined UI_PORT_PID (
  set "UI_PORT_NAME=unknown"
  for /f "tokens=1 delims=," %%N in ('tasklist /FI "PID eq !UI_PORT_PID!" /FO CSV /NH') do set "UI_PORT_NAME=%%~N"
  echo [StartupSpark] Port 5173 is in use by PID !UI_PORT_PID! (!UI_PORT_NAME!^).
  echo [StartupSpark] Port 5173 is already in use. Stop the existing UI server, then run this script again.
  pause
  exit /b 1
)

echo [StartupSpark] Starting FastAPI backend on http://127.0.0.1:8001
start "StartupSpark API" cmd /k ".\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8001"

echo [StartupSpark] Starting React UI on http://localhost:5173
start "StartupSpark UI" cmd /k "cd /d ""%~dp0ui"" && npm run dev -- --strictPort"

echo.
echo StartupSpark is starting.
echo API: http://127.0.0.1:8001
echo UI:  http://localhost:5173
echo.
echo Close the two opened terminal windows to stop the servers.

endlocal
