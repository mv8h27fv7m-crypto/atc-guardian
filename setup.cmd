@echo off
setlocal
cd /d "%~dp0"
echo Setting up ATC Guardian v0.1. Internet is needed to install dependencies.
where node >nul 2>nul
if errorlevel 1 (
  echo Install Node.js 22.12 or newer, then reopen this script.
  goto failed
)
where py >nul 2>nul
if errorlevel 1 (
  python -m venv .venv
) else (
  py -3 -m venv .venv
)
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
pushd frontend
call npm ci --no-fund
if errorlevel 1 (
  popd
  goto failed
)
call npm run build
if errorlevel 1 (
  popd
  goto failed
)
popd
.venv\Scripts\python.exe -m pytest
if errorlevel 1 goto failed
echo Setup complete. Double-click start.cmd to launch the simulator.
pause
exit /b 0
:failed
echo Setup could not finish. Read the error above and docs\GETTING_STARTED.md.
pause
exit /b 1
