@echo off
rem Pre-authorized power settings for the CALIBURN autopilot (operator-run).
rem The agent does not modify system settings; double-click this file to apply.
rem Effect: never sleep on AC or battery (critical-battery hibernate safety is
rem untouched), and switch to the highest-performance power plan available.
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
rem Try Ultimate Performance, then High Performance:
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61 2>nul || powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
echo Applied. Logged for RUN_REPORT: standby-timeout-ac=0, standby-timeout-dc=0, high-performance plan active.
powercfg /getactivescheme
pause
