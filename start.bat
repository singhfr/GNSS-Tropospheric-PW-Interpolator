@echo off
echo 🎯 GNSS Dashboard - Starting Services
echo ====================================

echo.
echo 🚀 Starting Backend Server...
cd backend
start "GNSS Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo ✅ Backend started in new window
echo 📍 API: http://localhost:8000
echo 📍 Docs: http://localhost:8000/docs

echo.
echo 🚀 Starting Frontend Server...
cd ../frontend
start "GNSS Frontend" cmd /k "pnpm dev"

echo ✅ Frontend started in new window
echo 📍 Dashboard: http://localhost:3000

echo.
echo 🎉 All services started!
echo.
echo 📋 Quick Start:
echo 1. Wait 10-15 seconds for services to fully start
echo 2. Open http://localhost:3000 in your browser
echo 3. Click 'Load Demo Data' to see the interpolation
echo.
echo ⏹️  To stop services, close the console windows
echo.
pause
