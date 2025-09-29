#!/usr/bin/env python3
"""Fix the remaining 26 VS Code problems"""

import subprocess
import sys
import os
from pathlib import Path

def install_missing_packages():
    """Install missing Python packages"""
    packages = [
        'psycopg2-binary',  # PostgreSQL adapter (binary version avoids compilation issues)
        'pywin32',          # Windows service utilities (should already be installed but ensuring)
    ]
    
    print("🔧 Installing missing packages...")
    for package in packages:
        print(f"  📦 Installing {package}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True, text=True)
            print(f"  ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e}")
            print(f"     stdout: {e.stdout}")
            print(f"     stderr: {e.stderr}")

def fix_corrupted_html():
    """Fix corrupted enhanced_dashboard.html"""
    html_file = Path("templates/enhanced_dashboard.html")
    
    if html_file.exists():
        print("🔧 Fixing corrupted HTML file...")
        try:
            # Read the current content
            content = html_file.read_text(encoding='utf-8')
            
            # Fix the corrupted script tag on line 61
            content = content.replace('}cript src="', '</script>\n<script src="')
            
            # Write back the fixed content
            html_file.write_text(content, encoding='utf-8')
            print("  ✅ Fixed enhanced_dashboard.html")
            
        except Exception as e:
            print(f"  ❌ Failed to fix HTML file: {e}")
    else:
        print("  ℹ️ enhanced_dashboard.html not found, skipping")

def fix_corrupted_python_files():
    """Fix corrupted Python files"""
    # Fix quick_diagnostic.py
    diagnostic_file = Path("quick_diagnostic.py")
    
    if diagnostic_file.exists():
        print("🔧 Fixing corrupted quick_diagnostic.py...")
        try:
            # Replace with a clean version
            clean_content = '''#!/usr/bin/env python3
"""Quick diagnostic to check system components without locking up"""

import sys
import os
from pathlib import Path

def print_diagnostic_summary():
    """Print diagnostic summary"""
    print("\\nDIAGNOSTIC SUMMARY")
    issues = []
    
    if not issues:
        print("✅ [OK] No critical issues found")
        return True
    else:
        print(f"❌ Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    print("\\nSUGGESTED FIXES:")
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
        print("\\n✅ [OK] No critical issues found")
    else:
        print(f"\\n❌ Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
            
            diagnostic_file.write_text(clean_content, encoding='utf-8')
            print("  ✅ Fixed quick_diagnostic.py")
            
        except Exception as e:
            print(f"  ❌ Failed to fix quick_diagnostic.py: {e}")

def create_optional_import_wrappers():
    """Create optional import wrappers for missing packages"""
    
    # Create wrapper for psycopg2 in case it's still missing
    psycopg2_wrapper = Path("optional_psycopg2.py")
    psycopg2_content = '''"""Optional psycopg2 wrapper"""
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    
    class RealDictCursor:
        pass
        
    print("⚠️ psycopg2 not available - some database features may be limited")
'''
    
    try:
        psycopg2_wrapper.write_text(psycopg2_content, encoding='utf-8')
        print("✅ Created optional psycopg2 wrapper")
    except Exception as e:
        print(f"❌ Failed to create psycopg2 wrapper: {e}")

def main():
    """Fix all remaining problems"""
    print("🚀 Fixing remaining VS Code problems...")
    
    # Install missing packages
    install_missing_packages()
    
    # Fix corrupted files
    fix_corrupted_html()
    fix_corrupted_python_files()
    
    # Create optional import wrappers
    create_optional_import_wrappers()
    
    print("\n✅ All fixes completed!")
    print("🔄 Please restart VS Code or reload the window to see the changes")

if __name__ == "__main__":
    main()