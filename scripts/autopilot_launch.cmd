@echo off
rem CALIBURN autopilot launcher (manual resume). Starts the runner WINDOWLESS
rem via pythonw so no console exists anywhere for a human to close. The
rem runner is single-instance guarded and infers all state from disk.
set REPO=C:\Users\CYBERWIZARD\projects\rcbsid-paper
if exist "%REPO%\DONE_ALL.md" (
  del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CALIBURN-AUTOPILOT.vbs" >nul 2>&1
  exit /b 0
)
start "" "%REPO%\.venv\Scripts\pythonw.exe" "%REPO%\scripts\autopilot_runner.py"
