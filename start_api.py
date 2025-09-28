#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE API - BACKGROUND LAUNCHER
==============================================
Starts the API service in background mode so it doesn't lock up your terminal.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def main():
    """Start API in background and verify it's running"""
    
    print("🎵 CULTURAL INTELLIGENCE API - Background Launcher")
    print("=" * 50)
    
    # Start API in background
    print("🚀 Starting API service in background...")
    
    try:
        # Use subprocess to start in background
        process = subprocess.Popen([
            sys.executable, 
            'metacrate_api.py'
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
        )
        
        print(f"✅ API process started (PID: {process.pid})")
        print("🔄 Waiting for service to initialize...")
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Test if it's responding
        try:
            response = requests.get('http://172.22.17.37:5000/api/v3.2/health', timeout=5)
            if response.status_code == 200:
                print("✅ API service is responding!")
                print(f"📡 Available at: http://172.22.17.37:5000")
                print()
                print("🔗 API Endpoints:")
                print("   - Health Check: http://172.22.17.37:5000/api/v3.2/health")
                print("   - File Analysis: http://172.22.17.37:5000/api/v3.2/analyze")
                print("   - Hash Lookup: http://172.22.17.37:5000/api/v3.2/lookup/<hash>")
                print()
                print("✅ Cultural Intelligence API is LIVE!")
                print("💡 Terminal is free to use - API running in background")
                
            else:
                print(f"⚠️ API responded with status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not connect to API: {e}")
            print("🔍 Check if the service started properly")
            
            # Show any startup errors
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                print(f"❌ Startup errors: {stderr}")
        
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())