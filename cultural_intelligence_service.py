#!/usr/bin/env python3
"""
Cultural Intelligence Scanner - Windows Service
===============================================
Runs Cultural Intelligence Scanner as a 24/7 Windows service
with automatic startup and restart capabilities.
"""

import win32service
import win32serviceutil
import win32event
import servicemanager
import socket
import sys
import os
import time
import subprocess
import threading
import requests
from pathlib import Path

class CulturalIntelligenceService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CulturalIntelligenceScanner"
    _svc_display_name_ = "Cultural Intelligence Scanner Service"
    _svc_description_ = "Automated music file scanning and intelligence building system. Scans music directories every 6 hours for electronic music taxonomy and classification."
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True
        self.scanner_process = None
        
        # Service configuration
        self.scanner_script = str(Path(__file__).parent / "cultural_intelligence_scanner.py")
        self.check_interval = 3600  # 1 hour health check
        
        # Logging
        self.log_file = str(Path(__file__).parent / "cultural_service.log")
        
    def log(self, message):
        """Write to both service log and file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except:
            pass
            
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, log_message)
        )
    
    def SvcStop(self):
        """Stop the service"""
        self.log("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        
        # Stop scanner process
        if self.scanner_process and self.scanner_process.poll() is None:
            try:
                self.scanner_process.terminate()
                self.log("Scanner process terminated")
            except:
                pass
    
    def SvcDoRun(self):
        """Main service loop"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.log("Cultural Intelligence Service started")
        self.log(f"Scanner Script: {self.scanner_script}")
        self.log(f"Check Interval: {self.check_interval} seconds")
        
        # Start the monitoring loop
        self.monitor_scanner()
    
    def start_scanner(self):
        """Start the scanner process"""
        try:
            # Change to the script directory
            script_dir = Path(self.scanner_script).parent
            
            self.log(f"Starting scanner from directory: {script_dir}")
            
            # Start the scanner process with service mode
            self.scanner_process = subprocess.Popen([
                sys.executable, self.scanner_script, "--service"
            ], 
            cwd=str(script_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # Run hidden
            )
            
            self.log(f"Scanner process started with PID: {self.scanner_process.pid}")
            
            # Wait a moment for startup
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.log(f"Failed to start scanner: {e}")
            return False
    
    def is_scanner_healthy(self):
        """Check if scanner process is healthy"""
        try:
            if not self.scanner_process:
                return False
            
            # Check if process is still running
            if self.scanner_process.poll() is not None:
                return False
                
            # Check scanner log file for recent activity (within last 2 hours)
            log_file = Path(self.scanner_script).parent / "cultural_intelligence_scanner.log"
            if log_file.exists():
                import time
                file_age = time.time() - log_file.stat().st_mtime
                if file_age < 7200:  # 2 hours
                    return True
                    
            return True  # Assume healthy if no other indicators
            
        except Exception as e:
            self.log(f"Scanner health check failed: {e}")
            return False
    
    def monitor_scanner(self):
        """Main monitoring loop"""
        
        # Initial scanner start
        if not self.start_scanner():
            self.log("Failed to start scanner on service startup")
        
        while self.is_alive:
            try:
                # Wait for stop event or timeout
                result = win32event.WaitForSingleObject(self.hWaitStop, self.check_interval * 1000)
                
                if result == win32event.WAIT_OBJECT_0:
                    # Service stop requested
                    break
                
                # Perform health check
                self.log("Performing hourly health check...")
                
                # Check if process is still running
                if not self.scanner_process or self.scanner_process.poll() is not None:
                    self.log("Scanner process is not running - restarting...")
                    self.start_scanner()
                    continue
                
                # Check if scanner is healthy
                if not self.is_scanner_healthy():
                    self.log("Scanner health check failed - restarting...")
                    
                    # Kill existing process
                    if self.scanner_process and self.scanner_process.poll() is None:
                        try:
                            self.scanner_process.terminate()
                            time.sleep(5)
                            if self.scanner_process.poll() is None:
                                self.scanner_process.kill()
                        except:
                            pass
                    
                    # Start new process
                    self.start_scanner()
                else:
                    self.log("Scanner health check passed")
                
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before trying again

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CulturalIntelligenceService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CulturalIntelligenceService)

if __name__ == '__main__':
    main()