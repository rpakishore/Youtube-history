@echo off
cd /d "%~dp0"  REM Switch to the script's directory

taskkill /IM chrome.exe /F

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Run the app
app

REM Deactivate the virtual environment (optional)
deactivate
