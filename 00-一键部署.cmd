@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0.agents\skills\plane-capture-deploy\scripts\Deploy.ps1" %*
if errorlevel 1 pause
