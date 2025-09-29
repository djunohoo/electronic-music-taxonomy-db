#!/usr/bin/env python3
"""
Dashboard Startup Test - Safe dashboard launch with error capture
"""

import subprocess
import sys
import time
import os

def test_dashboard_startup():
    """Test actual dashboard startup"""
    print("TESTING DASHBOARD STARTUP...")
    print("=" * 40)
    
    try:
        # Start dashboard with timeout
        print("Starting enhanced_cultural_dashboard.py...")
        
        process = subprocess.Popen(
            [sys.executable, "enhanced_cultural_dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("[SUCCESS] Dashboard is running!")
            print("Process ID:", process.pid)
            
            # Try to terminate gracefully
            process.terminate()
            try:
                process.wait(timeout=5)
                print("[INFO] Dashboard terminated gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("[INFO] Dashboard force-killed")
                
            return True
            
        else:
            # Process exited - capture output
            stdout, stderr = process.communicate()
            
            print(f"[FAIL] Dashboard exited with code: {process.returncode}")
            
            if stdout:
                print("\nSTDOUT:")
                print(stdout)
                
            if stderr:
                print("\nSTDERR:")
                print(stderr)
                
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to start dashboard: {e}")
        return False

def main():
    """Main test function"""
    print("DASHBOARD STARTUP TEST")
    print("=" * 40)
    
    success = test_dashboard_startup()
    
    if success:
        print("\n[SUCCESS] Dashboard can start successfully!")
        print("You can now run: python enhanced_cultural_dashboard.py")
    else:
        print("\n[FAIL] Dashboard still has startup issues")
        print("Check the error output above for details")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        
    input("\nPress Enter to continue...")