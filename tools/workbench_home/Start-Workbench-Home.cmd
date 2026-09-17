@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 home.py
goto finish
:python_fallback
where python >nul 2>nul
if errorlevel 1 goto missing
python home.py
goto finish
:missing
echo Python 3.10 or later is required. This launcher does not install software.
pause
exit /b 1
:finish
if errorlevel 1 pause
