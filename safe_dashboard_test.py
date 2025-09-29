#!/usr/bin/env python3
"""
Safe Dashboard Starter - Runs dashboard with error capture
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_with_timeout(cmd, timeout=10):
    """Run command with timeout and capture output"""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -2, "", str(e)

def test_dashboard_quick():
    """Quick dashboard test"""
    print("🧪 TESTING DASHBOARD STARTUP...")
    
    # Try to start dashboard with short timeout
    code, stdout, stderr = run_with_timeout("python enhanced_cultural_dashboard.py", timeout=5)
    
    print(f"Exit code: {code}")
    
    if stdout:
        print("STDOUT:")
        print(stdout)
    
    if stderr:
        print("STDERR:")
        print(stderr)
    
    # Common error patterns
    if "ModuleNotFoundError" in stderr:
        print("🔧 FIX: Missing module - run pip install")
    elif "ImportError" in stderr:
        print("🔧 FIX: Import issue - check file paths")
    elif "SyntaxError" in stderr:
        print("🔧 FIX: Syntax error in code")
    elif "PermissionError" in stderr:
        print("🔧 FIX: Permission issue - check file access")
    elif "Address already in use" in stderr:
        print("🔧 FIX: Port conflict - kill existing process")
    elif code == -1:
        print("🔧 FIX: Startup hangs - likely infinite loop or blocking call")
    
    return code == 0

def check_python_env():
    """Check Python environment"""
    print("\n🐍 PYTHON ENVIRONMENT:")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
    else:
        print("⚠️  Not in virtual environment")

def kill_python_processes():
    """Kill existing Python processes (Windows)"""
    print("\n💀 KILLING EXISTING PYTHON PROCESSES...")
    
    try:
        # Windows-specific
        subprocess.run("taskkill /F /IM python.exe /T", shell=True, capture_output=True)
        time.sleep(2)
        print("✅ Python processes terminated")
    except:
        print("❌ Could not kill processes")

def main():
    """Main diagnostic and fix routine"""
    print("🚀 SAFE DASHBOARD DIAGNOSTIC")
    print("=" * 40)
    
    # Check environment
    check_python_env()
    
    # Kill existing processes
    kill_python_processes()
    
    # Test dashboard
    if test_dashboard_quick():
        print("✅ Dashboard starts successfully!")
    else:
        print("❌ Dashboard has startup issues")
        
        print("\n🔧 ATTEMPTING BASIC FIXES...")
        
        # Try installing missing packages
        packages = ["flask", "flask-socketio", "requests", "mutagen"]
        for pkg in packages:
            print(f"Installing {pkg}...")
            subprocess.run(f"pip install {pkg}", shell=True, capture_output=True)
        
        # Test again
        print("\n🧪 RETESTING AFTER PACKAGE INSTALL...")
        if test_dashboard_quick():
            print("✅ Dashboard fixed!")
        else:
            print("❌ Still has issues - manual intervention needed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n💥 Script error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")