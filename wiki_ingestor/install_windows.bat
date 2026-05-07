@echo off
REM install_windows.bat — Install wiki_ingestor as a Windows Task Scheduler entry
REM Usage: install_windows.bat [--uninstall]

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SERVICE_NAME=wiki-ingestor"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "WIKI_DIR=%USERPROFILE%\wiki"

REM Check for uninstall
if "%1" == "--uninstall" (
    echo Uninstalling wiki_ingestor...
    schtasks /end /tn "%SERVICE_NAME%" 2>nul || ver >nul
    schtasks /delete /tn "%SERVICE_NAME%" /f 2>nul || ver >nul
    echo Uninstalled. Virtualenv kept at %VENV_DIR%
    exit /b 0
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python not found. Install Python 3.10+ first.
    exit /b 1
)

REM Create virtual environment
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtualenv at %VENV_DIR%...
    python -m venv "%VENV_DIR%"
)

REM Install dependencies
echo Installing dependencies...
"%VENV_DIR%\Scripts\pip" install --quiet --upgrade pip
"%VENV_DIR%\Scripts\pip" install --quiet markitdown[all] watchdog openai

REM Create wiki directory
if not exist "%WIKI_DIR%" mkdir "%WIKI_DIR%"

REM Check for existing wiki-linux config
set "WIKI_LINUX_CONFIG=%LOCALAPPDATA%\wiki-linux\config.json"
if exist "%WIKI_LINUX_CONFIG%" (
    echo Found wiki-linux config at %WIKI_LINUX_CONFIG%
    echo wiki_ingestor will automatically use its watch_dirs setting
)

REM Write default config
set "CONFIG=%WIKI_DIR%\wiki_ingestor_config.json"
if not exist "%CONFIG%" (
    echo Writing default config to %CONFIG%...
    "%VENV_DIR%\Scripts\python" -m wiki_ingestor init
) else (
    echo Config already exists at %CONFIG% — not overwriting.
)

REM Create Task Scheduler entry
set "TASK_CMD=schtasks /create /tn "%SERVICE_NAME%" /tr "\"%VENV_DIR%\Scripts\python.exe\" -m wiki_ingestor watch" /sc onlogon /rl highest /f"
%TASK_CMD%

REM Set working directory
schtasks /change /tn "%SERVICE_NAME%" /ru "%USERNAME%" /rp "" /start "%SCRIPT_DIR%" 2>nul || ver >nul

REM Start the task
schtasks /run /tn "%SERVICE_NAME%"

echo.
echo wiki_ingestor is installed as a Task Scheduler entry.
echo   Logs: Check Event Viewer for Application logs
echo   Stop: schtasks /end /tn "%SERVICE_NAME%"
echo   Config: %CONFIG%
echo   Output: %WIKI_DIR%\converted\\
