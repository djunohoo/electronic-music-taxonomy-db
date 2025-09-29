#!/usr/bin/env python3
"""Test dashboard startup with timeout"""

import subprocess
import time
import signal
import os
import sys

def test_dashboard_startup():
    """Test if dashboard can start successfully"""
    print("🧪 Testing Enhanced Cultural Dashboard startup...")
    
    try:
        # Start the dashboard process
        process = subprocess.Popen(
            [sys.executable, "enhanced_cultural_dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a few seconds for startup
        print("⏳ Waiting for startup...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Dashboard started successfully!")
            
            # Terminate the process
            process.terminate()
            time.sleep(1)
            
            if process.poll() is None:
                process.kill()
            
            print("🛑 Dashboard stopped")
            return True
        else:
            # Process exited, get the error
            stdout, stderr = process.communicate()
            print("❌ Dashboard failed to start:")
            if stderr:
                print(f"Error: {stderr}")
            if stdout:
                print(f"Output: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

def test_scanner_quick():
    """Test scanner initialization"""
    print("🧪 Testing Scanner initialization...")
    
    try:
        from cultural_intelligence_scanner import CulturalIntelligenceScanner
        scanner = CulturalIntelligenceScanner()
        print("✅ Scanner initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Scanner initialization failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("🔍 COMPREHENSIVE SYSTEM CHECK")
    print("=" * 40)
    
    results = []
    
    # Test scanner
    results.append(("Scanner", test_scanner_quick()))
    
    # Test dashboard
    results.append(("Dashboard", test_dashboard_startup()))
    
    # Print summary
    print("\n📊 SYSTEM CHECK RESULTS:")
    print("-" * 30)
    
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component:12} | {status}")
        if not passed:
            all_passed = False
    
    print("-" * 30)
    if all_passed:
        print("🎉 All systems operational!")
    else:
        print("⚠️  Some systems have issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)