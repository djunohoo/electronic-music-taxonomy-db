@echo off
echo Cultural Intelligence Service - Quick Install
echo ============================================
echo.
echo This will install the Cultural Intelligence API as a Windows service
echo that runs 24/7 and checks itself every hour.
echo.
echo Requirements:
echo - Must run as Administrator
echo - Will bind to 172.22.17.37:5000
echo - Auto-starts with Windows
echo.
set /p continue="Continue? (Y/N): "
if /i "%continue%" neq "Y" goto :end

echo.
echo Installing service...
python service_manager.py install

echo.
echo Starting service...  
python service_manager.py start

echo.
echo Final status check...
python service_manager.py status

echo.
echo ============================================
echo Installation complete!
echo.
echo Management commands:
echo   python service_manager.py start
echo   python service_manager.py stop  
echo   python service_manager.py restart
echo   python service_manager.py status
echo   python service_manager.py logs
echo.

:end
pause