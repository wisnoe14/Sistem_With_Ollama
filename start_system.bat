@echo off
echo ===========================================
echo 🚀 ICONNET CS Simulation System Launcher
echo ===========================================
echo.

REM Check if Ollama is running
echo ⏳ Checking Ollama service...
curl -s http://localhost:11434/api/tags > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama not running! Please start Ollama first:
    echo    ollama serve
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama service is running
)

REM Check if backend is running
echo ⏳ Checking backend service...
curl -s http://localhost:8000/ > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend not running! Starting backend...
    echo.
    echo 🔧 Starting FastAPI Backend...
    cd backend
    start cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    cd ..
    echo ✅ Backend started in new window
    timeout /t 3 > nul
) else (
    echo ✅ Backend service is running
)

REM Check if frontend is running
echo ⏳ Checking frontend service...
curl -s http://localhost:5173/ > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Frontend not running! Starting frontend...
    echo.
    echo 🎨 Starting React Frontend...
    cd frontend
    start cmd /k "npm run dev"
    cd ..
    echo ✅ Frontend started in new window
    timeout /t 3 > nul
) else (
    echo ✅ Frontend service is running
)

echo.
echo ===========================================
echo 🎉 System Status:
echo ✅ Ollama AI: http://localhost:11434
echo ✅ Backend API: http://localhost:8000
echo ✅ Frontend UI: http://localhost:5173
echo ===========================================
echo.
echo 🌐 Opening application in browser...
timeout /t 2 > nul
start http://localhost:5173

echo.
echo 📝 System Ready! You can now:
echo   1. Test dynamic AI conversation generation
echo   2. Use Telecollection, Winback, or Retention flows
echo   3. Experience context-aware question generation
echo.
echo Press any key to exit launcher...
pause > nul