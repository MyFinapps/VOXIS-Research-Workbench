@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 bridge.py
goto finish
:python_fallback
where python >nul 2>nul
if errorlevel 1 goto missing
python bridge.py
goto finish
:missing
echo Python 3 is required. This launcher does not install software.
:finish
pause
