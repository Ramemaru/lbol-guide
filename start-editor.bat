@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
where node >nul 2>nul
if errorlevel 1 (
    echo Node.js 20 or newer is required: https://nodejs.org/
    pause
    exit /b 1
)
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYCMD=py -3"
) else (
    set "PYCMD=python"
)
%PYCMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Python installation failed. Install Python 3.10 or newer.
    pause
    exit /b 1
)
%PYCMD% dev.py
if errorlevel 1 pause
