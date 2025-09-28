#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE SERVICE MANAGER
===================================
Easy management of the Cultural Intelligence Windows service
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def run_command(cmd):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_service_status():
    """Check if the service is running"""
    success, stdout, stderr = run_command('sc query "CulturalIntelligenceAPI"')
    if success and "RUNNING" in stdout:
        return True, "Service is RUNNING"
    elif success and "STOPPED" in stdout:
        return False, "Service is STOPPED"
    elif success and "PAUSED" in stdout:
        return False, "Service is PAUSED"
    else:
        return False, "Service is NOT INSTALLED or ERROR"

def check_api_health():
    """Check if the API is responding"""
    try:
        response = requests.get("http://172.22.17.37:5000/api/v3.2/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def get_api_stats():
    """Get API statistics"""
    try:
        response = requests.get("http://172.22.17.37:5000/api/v3.2/stats", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def main():
    """Main menu"""
    
    print("🎵 CULTURAL INTELLIGENCE SERVICE MANAGER")
    print("=" * 45)
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = None
    
    # Check current status
    service_running, service_msg = check_service_status()
    api_healthy, api_msg = check_api_health()
    
    print(f"Service Status: {service_msg}")
    
    if service_running and api_healthy:
        print(f"API Status: ✅ HEALTHY")
        
        # Get stats
        stats_ok, stats = get_api_stats()
        if stats_ok:
            print(f"Database: {stats.get('tracks', 0)} tracks, {stats.get('artists', 0)} artists")
        
    elif service_running:
        print(f"API Status: ⚠️  Service running but API not responding")
    else:
        print(f"API Status: ❌ Not available")
    
    print()
    
    # Handle commands
    if command == "start":
        print("Starting service...")
        success, stdout, stderr = run_command('python cultural_intelligence_service.py start')
        if success:
            print("✅ Service start command sent")
            print("⏳ Waiting for API to become available...")
            for i in range(30):
                time.sleep(2)
                healthy, _ = check_api_health()
                if healthy:
                    print("✅ API is now responding!")
                    break
                print(f"   Checking... {i+1}/30")
            else:
                print("⚠️  API did not respond within 60 seconds")
        else:
            print(f"❌ Failed to start service: {stderr}")
            
    elif command == "stop":
        print("Stopping service...")
        success, stdout, stderr = run_command('python cultural_intelligence_service.py stop')
        if success:
            print("✅ Service stopped")
        else:
            print(f"❌ Failed to stop service: {stderr}")
            
    elif command == "restart":
        print("Restarting service...")
        run_command('python cultural_intelligence_service.py stop')
        time.sleep(3)
        success, stdout, stderr = run_command('python cultural_intelligence_service.py start')
        if success:
            print("✅ Service restarted")
        else:
            print(f"❌ Failed to restart service: {stderr}")
            
    elif command == "status":
        # Status already shown above
        pass
        
    elif command == "install":
        print("Installing service (requires Administrator)...")
        success, stdout, stderr = run_command('python cultural_intelligence_service.py install')
        if success:
            print("✅ Service installed")
            print("Setting auto-start...")
            run_command('sc config "CulturalIntelligenceAPI" start= auto')
            print("✅ Service configured for automatic startup")
        else:
            print(f"❌ Failed to install service: {stderr}")
            
    elif command == "remove":
        print("Removing service...")
        run_command('python cultural_intelligence_service.py stop')
        success, stdout, stderr = run_command('python cultural_intelligence_service.py remove')
        if success:
            print("✅ Service removed")
        else:
            print(f"❌ Failed to remove service: {stderr}")
            
    elif command == "logs":
        log_file = Path("service.log")
        if log_file.exists():
            print("📋 Recent service logs:")
            print("-" * 40)
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Show last 20 lines
                    print(line.rstrip())
        else:
            print("📋 No log file found")
            
    else:
        print("Available commands:")
        print("  python service_manager.py install  - Install the service")
        print("  python service_manager.py start    - Start the service") 
        print("  python service_manager.py stop     - Stop the service")
        print("  python service_manager.py restart  - Restart the service")
        print("  python service_manager.py status   - Show status (default)")
        print("  python service_manager.py logs     - Show recent logs")
        print("  python service_manager.py remove   - Remove the service")
        print()
        print("💡 The service runs 24/7 and checks itself every hour")

if __name__ == "__main__":
    main()