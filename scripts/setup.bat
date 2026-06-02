@echo off
setlocal

:: Always run from the repo root regardless of where this script is called from
cd /d "%~dp0.."

echo === Flag Quiz Setup ===
echo.

:: Check if uv is installed
set "UV=uv"
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [1/3] uv not found. Installing uv...
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install uv. Please install it manually: https://docs.astral.sh/uv/
        exit /b 1
    )
    echo uv installed successfully.
    :: Use full path since the new PATH won't take effect in this session
    set "UV=%USERPROFILE%\.local\bin\uv.exe"
) else (
    echo [1/3] uv is already installed. Skipping.
)

echo.
echo [2/3] Installing dependencies (uv sync)...
"%UV%" sync
if %ERRORLEVEL% neq 0 (
    echo ERROR: uv sync failed.
    exit /b 1
)

echo.
echo [3/3] Downloading flag images...
"%UV%" run python scripts/download_flags.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Flag download failed.
    exit /b 1
)

echo.
echo === Setup complete! ===
echo Run the app with:  "%UV%" run python -m flag_quiz.main
echo.
endlocal
