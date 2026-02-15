@echo off
cls
echo ============================================
echo    Starting usecase.ai Platform
echo ============================================
echo.

echo [1/5] Starting Landing Page (port 3000)...
start "Landing Page" cmd /k "cd src\landingzone && npm run dev"
timeout /t 3 /nobreak >nul

echo [2/5] Starting Insurance Backend (port 8000)...
start "Insurance Backend" cmd /k "cd src\AI_Insurance_Underwriter\Backend && call .venv\Scripts\activate.bat && uv run uvicorn api.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo [3/5] Starting Insurance Frontend (port 5173)...
start "Insurance Frontend" cmd /k "cd src\AI_Insurance_Underwriter\Frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo [4/5] Starting Video Backend (port 8001)...
start "Video Backend" cmd /k "cd src\videotranscriber\Backend && call .venv\Scripts\activate.bat && uv run uvicorn api:app --host 0.0.0.0 --port 8001"
timeout /t 3 /nobreak >nul

echo [5/5] Starting Video Frontend (port 3002)...
start "Video Frontend" cmd /k "cd src\videotranscriber\Frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo    All services should be starting now!
echo ============================================
echo.
echo Landing Page:        http://localhost:3000
echo Insurance App:       http://localhost:5173
echo Video Transcriber:   http://localhost:3002
echo Insurance API:       http://localhost:8000/docs
echo Video API:           http://localhost:8001
echo.
echo Check each terminal window for status
echo Close each window to stop that service
echo.
pause
