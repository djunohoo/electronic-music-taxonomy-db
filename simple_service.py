#!/usr/bin/env python3
"""
Cultural Intelligence Service - Simple Version
Uses working Supabase REST client in background service
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import subprocess
import sys
import os
from pathlib import Path

class CulturalIntelligenceService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CulturalIntelligence"
    _svc_display_name_ = "Cultural Intelligence System"
    _svc_description_ = "Electronic music taxonomy intelligence using Supabase REST API"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True
        self.api_process = None

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        
        # Stop API process
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            except:
                if self.api_process:
                    self.api_process.kill()
        
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STOPPED,
                            (self._svc_name_, ''))

    def SvcDoRun(self):
        """Main service loop"""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Start the API
        self.start_api()
        
        # Main loop with health checks every hour
        while self.is_alive:
            # Wait for stop event (1 hour timeout for health checks)
            if win32event.WaitForSingleObject(self.hWaitStop, 3600000) == win32event.WAIT_OBJECT_0:
                break
                
            # Health check
            if self.is_alive:
                self.health_check()

    def start_api(self):
        """Start the Cultural Intelligence API"""
        try:
            # Use Python from virtual environment if available
            venv_python = Path(".venv/Scripts/python.exe")
            python_exe = str(venv_python) if venv_python.exists() else "python"
            
            # Start API process
            self.api_process = subprocess.Popen(
                [python_exe, "simple_rest_api.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            servicemanager.LogInfoMsg(f"Started Cultural Intelligence API (PID: {self.api_process.pid})")
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Failed to start API: {e}")

    def health_check(self):
        """Check if API is still running"""
        if not self.api_process or self.api_process.poll() is not None:
            servicemanager.LogWarningMsg("API process died, restarting...")
            self.start_api()
        else:
            servicemanager.LogInfoMsg(f"API health check OK (PID: {self.api_process.pid})")

def install_service():
    """Install the Windows service"""
    try:
        # Use HandleCommandLine for proper installation
        sys.argv = ['simple_service.py', 'install']
        win32serviceutil.HandleCommandLine(CulturalIntelligenceService)
        print("✅ Cultural Intelligence Service installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Service installation failed: {e}")
        return False

def start_service():
    """Start the Windows service"""
    try:
        win32serviceutil.StartService(CulturalIntelligenceService._svc_name_)
        print("✅ Cultural Intelligence Service started!")
        return True
    except Exception as e:
        print(f"❌ Service start failed: {e}")
        return False

def stop_service():
    """Stop the Windows service"""
    try:
        win32serviceutil.StopService(CulturalIntelligenceService._svc_name_)
        print("✅ Cultural Intelligence Service stopped!")
        return True
    except Exception as e:
        print(f"❌ Service stop failed: {e}")
        return False

def remove_service():
    """Remove the Windows service"""
    try:
        win32serviceutil.RemoveService(CulturalIntelligenceService._svc_name_)
        print("✅ Cultural Intelligence Service removed!")
        return True
    except Exception as e:
        print(f"❌ Service removal failed: {e}")
        return False

def main():
    """Main service management"""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CulturalIntelligenceService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'remove':
            remove_service()
        elif command == 'debug':
            # Run in debug mode (foreground)
            print("🔧 Running in debug mode...")
            service = CulturalIntelligenceService([])
            service.SvcDoRun()
        else:
            print("Usage:")
            print("  python simple_service.py install  - Install service")
            print("  python simple_service.py start    - Start service")
            print("  python simple_service.py stop     - Stop service")
            print("  python simple_service.py remove   - Remove service")
            print("  python simple_service.py debug    - Run in foreground")

if __name__ == '__main__':
    main()