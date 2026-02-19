@echo off
echo ============================================
echo  MECHANICAL BIBLE - Local Development Server
echo ============================================
echo.
echo Starting server at http://localhost:8000
echo.
echo Open your browser and go to:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo ============================================
echo.
cd /d "C:\mechanical-bible"
python -m http.server 8000
