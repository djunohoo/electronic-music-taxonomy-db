@echo off
REM METACRATE BATCH ORCHESTRATOR INSTALLER
REM =====================================
REM Automated installation and setup script for MetaCrate Batch Orchestrator
REM
REM Prerequisites:
REM - Python 3.8+ installed
REM - Administrative privileges (for Windows service installation)
REM - Network access to X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS

echo.
echo ==========================================
echo  METACRATE BATCH ORCHESTRATOR INSTALLER
echo ==========================================
echo.
echo This script will:
echo   - Install required Python dependencies
echo   - Validate system configuration
echo   - Install Windows service for automatic startup
echo   - Test the system functionality
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ ERROR: This script requires Administrator privileges
    echo    Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python is installed
    python --version
) else (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo    Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  STEP 1: Installing Python Dependencies
echo ==========================================
echo.

echo Installing core dependencies...
pip install psycopg2-binary mutagen schedule

echo.
echo Installing Windows service dependencies...
pip install pywin32

echo.
echo Registering Python service components...
python -m win32serviceutil --register-quiet

echo.
echo ==========================================
echo  STEP 2: Validating System Configuration
echo ==========================================
echo.

echo Checking MetaCrate USERS directory...
if exist "X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS" (
    echo ✅ MetaCrate USERS directory accessible
) else (
    echo ❌ WARNING: MetaCrate USERS directory not found
    echo    Expected: X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS
    echo    Please ensure network drive is mapped
)

echo.
echo Testing Cultural Intelligence components...
python -c "from cultural_intelligence_scanner import CulturalIntelligenceScanner; from cultural_database_client import CulturalDatabaseClient; print('✅ Core components loaded successfully')" 2>nul
if %errorLevel% == 0 (
    echo ✅ Cultural Intelligence components OK
) else (
    echo ❌ ERROR: Cultural Intelligence components failed to load
    echo    Please ensure cultural_intelligence_scanner.py and cultural_database_client.py are present
    pause
    exit /b 1
)

echo.
echo Testing database connectivity...
python -c "from cultural_database_client import CulturalDatabaseClient; db = CulturalDatabaseClient(); print(f'✅ Database connected: {db.count_discovered_tracks()} tracks found')" 2>nul
if %errorLevel% == 0 (
    echo ✅ Database connectivity OK
) else (
    echo ❌ WARNING: Database connectivity issues
    echo    The system may work but won't store data properly
)

echo.
echo ==========================================
echo  STEP 3: Installing Windows Service
echo ==========================================
echo.

echo Installing MetaCrate Batch Orchestrator service...
python metacrate_service.py install
if %errorLevel% == 0 (
    echo ✅ Service installed successfully
) else (
    echo ❌ ERROR: Service installation failed
    pause
    exit /b 1
)

echo.
echo Starting the service...
python metacrate_service.py start
if %errorLevel% == 0 (
    echo ✅ Service started successfully
) else (
    echo ❌ ERROR: Service failed to start
    echo    Check logs: metacrate_service.log
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  STEP 4: Verification & Status
echo ==========================================
echo.

echo Waiting 10 seconds for service to initialize...
timeout /t 10 /nobreak >nul

echo.
echo Service status:
python metacrate_batch_orchestrator.py --status

echo.
echo ==========================================
echo  INSTALLATION COMPLETE!
echo ==========================================
echo.
echo ✅ MetaCrate Batch Orchestrator is now running as a Windows service
echo.
echo Key Features:
echo   - Processes 250 tracks per batch
echo   - 15-minute intervals for AI analysis
echo   - Full Cultural Intelligence integration  
echo   - Automatic startup on system boot
echo   - Continuous pattern learning
echo.
echo Log Files:
echo   - metacrate_orchestrator.log (batch processing)
echo   - metacrate_service.log (Windows service)
echo   - cultural_intelligence_scanner.log (AI analysis)
echo.
echo Management Commands:
echo   python metacrate_service.py start    # Start service
echo   python metacrate_service.py stop     # Stop service  
echo   python metacrate_service.py remove   # Uninstall service
echo.
echo Manual Operation (alternative):
echo   python metacrate_batch_orchestrator.py --start
echo.
echo The system will now continuously process your MetaCrate USERS directory!
echo Your dashboard at http://172.22.17.37:8081 will show the results.
echo.
pause
