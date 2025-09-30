#!/usr/bin/env python3
"""
METACRATE BATCH ORCHESTRATOR SERVICE
====================================
Windows service wrapper for MetaCrate Batch Orchestrator.
Enables automatic startup and background operation.
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    HAS_PYWIN32 = True
except ImportError:
    print("PyWin32 not available. Install with: pip install pywin32")
    HAS_PYWIN32 = False

from metacrate_batch_orchestrator import MetaCrateBatchOrchestrator

class MetaCrateService(win32serviceutil.ServiceFramework):
    """Windows service for MetaCrate Batch Orchestrator"""
    
    _svc_name_ = "MetaCrateBatchOrchestrator"
    _svc_display_name_ = "MetaCrate Batch Orchestrator"
    _svc_description_ = "Automated batch processing of MetaCrate USERS directory with AI analysis"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.orchestrator = None
        self.running = False
        
        # Setup service logging
        log_file = Path(__file__).parent / "metacrate_service.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("MetaCrate Service stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        if self.orchestrator:
            self.orchestrator.stop()
        
        self.running = False
        win32event.SetEvent(self.hWaitStop)
        
        self.logger.info("MetaCrate Service stopped")
    
    def SvcDoRun(self):
        """Main service execution"""
        self.logger.info("MetaCrate Service starting...")
        
        # Log to Windows Event Log
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.running = True
        
        try:
            # Initialize orchestrator
            self.orchestrator = MetaCrateBatchOrchestrator()
            
            # Start orchestrator in background thread
            orchestrator_thread = threading.Thread(
                target=self.orchestrator.run_continuous_batches,
                daemon=True
            )
            orchestrator_thread.start()
            
            self.logger.info("MetaCrate Service running - waiting for stop signal")
            
            # Wait for stop signal
            while self.running:
                # Wait for stop event or timeout (check every 30 seconds)
                rc = win32event.WaitForSingleObject(self.hWaitStop, 30000)
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop event was signaled
                    break
                elif rc == win32event.WAIT_TIMEOUT:
                    # Timeout - service still running, continue
                    continue
                else:
                    # Some other event
                    self.logger.warning(f"Unexpected wait result: {rc}")
                    break
            
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            servicemanager.LogErrorMsg(f"MetaCrate Service error: {e}")
        
        finally:
            if self.orchestrator:
                self.orchestrator.stop()
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )

def main():
    """Main entry point for service management"""
    if not HAS_PYWIN32:
        print("❌ PyWin32 is required for Windows service functionality")
        print("Install with: pip install pywin32")
        print()
        print("Alternative - Run directly:")
        print("python metacrate_batch_orchestrator.py --start")
        return
    
    if len(sys.argv) == 1:
        # No arguments - show usage
        print("MetaCrate Batch Orchestrator Service")
        print("====================================")
        print()
        print("Service Management Commands:")
        print("  python metacrate_service.py install    # Install Windows service")
        print("  python metacrate_service.py start      # Start service")
        print("  python metacrate_service.py stop       # Stop service")
        print("  python metacrate_service.py remove     # Uninstall service")
        print("  python metacrate_service.py debug      # Run in debug mode")
        print()
        print("Manual Operation:")
        print("  python metacrate_batch_orchestrator.py --start")
        print()
        return
    
    # Handle service commands
    if 'install' in sys.argv:
        try:
            win32serviceutil.InstallService(
                MetaCrateService._svc_reg_class_,
                MetaCrateService._svc_name_,
                MetaCrateService._svc_display_name_,
                description=MetaCrateService._svc_description_,
                startType=win32service.SERVICE_AUTO_START
            )
            print(f"✅ Service '{MetaCrateService._svc_display_name_}' installed successfully")
            print("   Service will start automatically at boot")
            print(f"   Use 'python {sys.argv[0]} start' to start now")
        except Exception as e:
            print(f"❌ Service installation failed: {e}")
            print("   Make sure you're running as Administrator")
    
    elif 'remove' in sys.argv:
        try:
            win32serviceutil.RemoveService(MetaCrateService._svc_name_)
            print(f"✅ Service '{MetaCrateService._svc_display_name_}' removed successfully")
        except Exception as e:
            print(f"❌ Service removal failed: {e}")
    
    else:
        # Standard service commands (start, stop, debug, etc.)
        win32serviceutil.HandleCommandLine(MetaCrateService)

if __name__ == '__main__':
    main()
