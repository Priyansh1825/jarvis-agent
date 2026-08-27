@echo off
title J.A.R.V.I.S. Mark VII Protocol
color 0b
echo ====================================================================
echo            J.A.R.V.I.S. - CLOUD AI VOICE AGENT
echo               Stark Industries Mark VII Protocol
echo ====================================================================
echo.

:: 1. Try Miniconda / Anaconda environment Python
if exist "%USERPROFILE%\Miniconda3\python.exe" (
    "%USERPROFILE%\Miniconda3\python.exe" run_jarvis.py
    goto end
)

if exist "%USERPROFILE%\anaconda3\python.exe" (
    "%USERPROFILE%\anaconda3\python.exe" run_jarvis.py
    goto end
)

:: 2. Try Local Virtual Environment
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_jarvis.py
    goto end
)

:: 3. Fallback to System Python
python run_jarvis.py

:end
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Encountered an issue running JARVIS.
    pause
)
