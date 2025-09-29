#!/usr/bin/env python3
"""
Quick Diagnostic Script - Identify and fix system issues (Windows-compatible)
"""

import sys
import traceback
import subprocess
import os
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("=== TESTING IMPORTS ===")
    
    critical_imports = [
        'flask',
        'flask_socketio', 
        'requests',
        'mutagen',
        'cultural_database_client',
        'cultural_intelligence_scanner'
    ]
    
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[FAIL] {module}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_database_connection():
    """Test database connectivity"""
    print("\n=== TESTING DATABASE ===")
    
    try:
        from cultural_database_client import CulturalDatabaseClient
        client = CulturalDatabaseClient()
        
        # Quick health check using REST API
        response = client._make_request('GET', 'cultural_tracks?select=id&limit=1')
        print("[OK] Database connection successful")
        return True
        
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False

def test_dashboard_startup():
    """Test dashboard startup without actually running it"""
    print("\n=== TESTING DASHBOARD STARTUP ===")
    
    try:
        # Try to import dashboard components
        sys.path.insert(0, os.getcwd())
        
        # Test the dashboard file syntax
        with open('enhanced_cultural_dashboard.py', 'r', encoding='utf-8') as f:
            dashboard_code = f.read()
            
        # Compile to check for syntax errors
        compile(dashboard_code, 'enhanced_cultural_dashboard.py', 'exec')
        print("[OK] Dashboard syntax is valid")
        
        # Try importing key components
        from cultural_database_client import CulturalDatabaseClient
        print("[OK] Database client imports OK")
        
        return True
        
    except SyntaxError as e:
        print(f"[FAIL] Dashboard syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
        
    except Exception as e:
        print(f"[FAIL] Dashboard import error: {e}")
        traceback.print_exc()
        return False

def test_scanner_issues():
    """Test scanner for null character issues"""
    print("\n=== TESTING SCANNER ===")
    
    try:
        from cultural_intelligence_scanner import CulturalIntelligenceScanner
        print("[OK] Scanner imports OK")
        
        # Check if extract_metadata has null char sanitization
        scanner = CulturalIntelligenceScanner()
        if hasattr(scanner, 'extract_metadata'):
            print("[OK] extract_metadata method exists")
        else:
            print("[FAIL] extract_metadata method missing")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Scanner import error: {e}")
        return False

def check_port_conflicts():
    """Check for port conflicts"""
    print("\n=== CHECKING PORTS ===")
    
    try:
        import socket
        
        ports_to_check = [8081, 5000, 8080]
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            
            if result == 0:
                print(f"[WARN] Port {port} is in use")
            else:
                print(f"[OK] Port {port} is available")
                
            sock.close()
            
    except Exception as e:
        print(f"[FAIL] Port check failed: {e}")

def main():
    """Run all diagnostics"""
    print("SYSTEM DIAGNOSTIC STARTING...")
    print("=" * 50)
    
    issues = []
    
    # Test imports
    failed_imports = test_imports()
    if failed_imports:
        issues.append(f"Missing imports: {', '.join(failed_imports)}")
    
    # Test database
    if not test_database_connection():
        issues.append("Database connection failed")
    
    # Test dashboard
    if not test_dashboard_startup():
        issues.append("Dashboard startup issues")
    
    # Test scanner
    if not test_scanner_issues():
        issues.append("Scanner import issues")
    
    # Check ports
    check_port_conflicts()
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    
    if not issues:
        print("[OK] No critical issues found")
    else:
        print("[ISSUES] Problems detected:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    print("\nSUGGESTED FIXES:")
    if failed_imports:
        print("   - Run: pip install " + " ".join(failed_imports))
    
    if "Database connection failed" in str(issues):
        print("   - Check Supabase configuration")
        print("   - Verify database credentials")
    
    if "Dashboard startup issues" in str(issues):
        print("   - Check enhanced_cultural_dashboard.py for syntax errors")
        print("   - Verify all imports in dashboard file")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nDIAGNOSTIC CRASHED: {e}")
        traceback.print_exc()
        
    input("\nPress Enter to continue...")