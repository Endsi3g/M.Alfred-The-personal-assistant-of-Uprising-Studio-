@echo off
setlocal
title A.L.F.R.E.D. DEPLOYMENT PROTOCOL

echo ============================================================
echo   A.L.F.R.E.D. -- PROJECT B.E.L.L. -- DEPLOYMENT
echo ============================================================
echo.

echo [1/4] Checking System Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+.
    pause
    exit /b 1
)

echo [2/4] Installing Core Dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARN] Some dependencies failed to install.
)

echo [3/4] Running Alfred's Smart Setup...
python setup.py
if %errorlevel% neq 0 (
    echo [ERROR] Setup protocol failed.
    pause
    exit /b 1
)

echo [4/4] Initializing Skills Arsenal...
python scripts/update_skills.py
if %errorlevel% neq 0 (
    echo [WARN] Skill indexing had issues.
)

echo.
echo ============================================================
echo   MISSION PREP COMPLETE. Alfred is ready for Master Bell.
echo   Execute 'python main.py' to begin.
echo ============================================================
echo.
pause
