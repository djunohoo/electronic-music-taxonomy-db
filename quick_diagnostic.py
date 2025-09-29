#!/usr/bin/env python3
"""Quick diagnostic to check system components without locking up"""

import sys
import os
from pathlib import Path

def print_diagnostic_summary():
    """Print diagnostic summary"""
    print("\nDIAGNOSTIC SUMMARY")
    issues = []
    
    if not issues:
        print("✅ [OK] No critical issues found")
        return True
    else:
        print(f"❌ Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    print("\nSUGGESTED FIXES:")
    return False

def test_imports():
    """Test critical imports"""
    issues = []
    
    # Test core imports
    try:
        import flask
        import flask_socketio  
        print("✅ Flask/SocketIO imports OK")
    except ImportError as e:
        issues.append(f"Flask imports failed: {e}")
        
    try:
        import psycopg2
        print("✅ PostgreSQL adapter OK")
    except ImportError as e:
        issues.append(f"psycopg2 missing: {e}")
        
    return issues

def test_database():
    """Test database connectivity"""
    try:
        from cultural_database_client import CulturalDatabaseClient
        client = CulturalDatabaseClient()
        print("✅ Database client OK")
        return []
    except Exception as e:
        return [f"Database connection failed: {e}"]

def test_dashboard_syntax():
    """Test dashboard syntax"""
    try:
        import ast
        with open("enhanced_cultural_dashboard.py", 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Dashboard syntax OK")
        return []
    except Exception as e:
        return [f"Dashboard syntax error: {e}"]

def test_scanner():
    """Test scanner initialization"""
    try:
        from cultural_intelligence_scanner import CulturalIntelligenceScanner
        scanner = CulturalIntelligenceScanner()
        print("✅ Scanner initialization OK")
        return []
    except Exception as e:
        return [f"Scanner failed: {e}"]

def check_ports():
    """Check if ports are available"""
    import socket
    ports_to_check = [8081, 5000]
    issues = []
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            issues.append(f"Port {port} is already in use")
        else:
            print(f"✅ Port {port} available")
            
    return issues

def main():
    """Run comprehensive diagnostic"""
    print("🔍 Running comprehensive system diagnostic...")
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_imports())
    all_issues.extend(test_database())  
    all_issues.extend(test_dashboard_syntax())
    all_issues.extend(test_scanner())
    all_issues.extend(check_ports())
    
    # Print summary
    if not all_issues:
        print("\n✅ [OK] No critical issues found")
    else:
        print(f"\n❌ Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
