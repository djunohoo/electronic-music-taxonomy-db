@echo off
REM Cultural Intelligence Service Installer
REM Run this as Administrator to install the Windows service

echo Cultural Intelligence Service Installer
echo ========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Running as Administrator
) else (
    echo ❌ ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Install required Python packages
echo.
echo Installing required Python packages...
pip install pywin32 requests

REM Install the service
echo.
echo Installing Cultural Intelligence Service...
python cultural_intelligence_service.py install

REM Set service to start automatically
echo.
echo Setting service to start automatically...
sc config "CulturalIntelligenceAPI" start= auto

REM Start the service
echo.
echo Starting service...
python cultural_intelligence_service.py start

REM Check service status
echo.
echo Checking service status...
python cultural_intelligence_service.py status

echo.
echo ========================================
echo Installation Complete!
echo.
echo The Cultural Intelligence API will now:
echo - Start automatically when Windows boots
echo - Run even when no user is logged in
echo - Check itself every hour and restart if needed
echo - Bind to your static IP: 172.22.17.37:5000
echo.
echo Service Management Commands:
echo - Start:   python cultural_intelligence_service.py start
echo - Stop:    python cultural_intelligence_service.py stop
echo - Restart: python cultural_intelligence_service.py restart
echo - Status:  python cultural_intelligence_service.py status
echo - Remove:  python cultural_intelligence_service.py remove
echo.
echo Check logs at: service.log
echo.
pause