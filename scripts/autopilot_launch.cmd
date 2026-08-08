@echo off
rem CALIBURN autopilot launcher — run by the CALIBURN-AUTOPILOT logon task.
rem Self-deregisters once DONE_ALL.md exists; otherwise starts the runner,
rem which infers all state from disk and is single-instance guarded.
set REPO=C:\Users\CYBERWIZARD\projects\rcbsid-paper
if exist "%REPO%\DONE_ALL.md" (
  schtasks /delete /tn CALIBURN-AUTOPILOT /f >nul 2>&1
  del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CALIBURN-AUTOPILOT.cmd" >nul 2>&1
  exit /b 0
)
cd /d "%REPO%"
"%REPO%\.venv\Scripts\python.exe" "%REPO%\scripts\autopilot_runner.py" >> "%REPO%\logs\autopilot_launch.log" 2>&1
