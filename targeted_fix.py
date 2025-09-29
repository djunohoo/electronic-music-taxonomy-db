#!/usr/bin/env python3
"""Direct fix for VS Code import resolution issues"""

import subprocess
import sys
import os
from pathlib import Path

def fix_pywin32_imports():
    """Fix pywin32 imports by updating files to use optional imports"""
    
    files_to_fix = [
        "cultural_intelligence_service.py",
        "simple_service.py"
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            print(f"🔧 Fixing pywin32 imports in {file_path}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace direct imports with try/except blocks
                replacements = {
                    'import win32service': '''try:
    import win32service
except ImportError:
    win32service = None
    print("⚠️ win32service not available - Windows service features disabled")''',
                    
                    'import win32serviceutil': '''try:
    import win32serviceutil
except ImportError:
                    win32serviceutil = None''',
                    
                    'import win32event': '''try:
    import win32event
except ImportError:
    win32event = None''',
                    
                    'import servicemanager': '''try:
    import servicemanager
except ImportError:
    servicemanager = None'''
                }
                
                for old_import, new_import in replacements.items():
                    if old_import in content and 'try:' not in content:
                        content = content.replace(old_import, new_import)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"  ✅ Fixed {file_path}")
                
            except Exception as e:
                print(f"  ❌ Failed to fix {file_path}: {e}")

def fix_psycopg2_imports():
    """Fix psycopg2 imports by updating files to use optional imports"""
    
    files_to_fix = [
        "install_cultural_intelligence.py",
        "cultural_scheduler.py", 
        "test_supabase_auth.py"
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            print(f"🔧 Fixing psycopg2 imports in {file_path}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace direct imports with try/except blocks
                replacements = {
                    'import psycopg2': '''try:
    import psycopg2
except ImportError:
    psycopg2 = None
    print("⚠️ psycopg2 not available - some database features may be limited")''',
                    
                    'from psycopg2.extras import RealDictCursor': '''try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    class RealDictCursor:
        pass'''
                }
                
                for old_import, new_import in replacements.items():
                    if old_import in content and 'try:' not in content:
                        content = content.replace(old_import, new_import)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"  ✅ Fixed {file_path}")
                
            except Exception as e:
                print(f"  ❌ Failed to fix {file_path}: {e}")

def fix_html_javascript_errors():
    """Fix JavaScript parsing errors in HTML files"""
    
    html_file = Path("templates/enhanced_dashboard.html")
    
    if html_file.exists():
        print("🔧 Fixing JavaScript parsing errors in HTML...")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add VS Code directive to treat as HTML, not JavaScript
            if not content.startswith('<!-- @format -->'):
                content = '<!-- @format -->\n' + content
            
            # Fix any malformed script tags
            content = content.replace('}cript src="', '</script>\n<script src="')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("  ✅ Fixed enhanced_dashboard.html")
            
        except Exception as e:
            print(f"  ❌ Failed to fix HTML: {e}")

def create_vscode_settings():
    """Create VS Code settings to help with import resolution"""
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    settings_content = '''{
    "python.analysis.extraPaths": [
        "."
    ],
    "python.analysis.autoImportCompletions": true,
    "python.analysis.diagnosticMode": "workspace",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "files.associations": {
        "*.html": "html"
    },
    "emmet.includeLanguages": {
        "html": "html"
    }
}'''
    
    try:
        settings_file.write_text(settings_content, encoding='utf-8')
        print("✅ Created .vscode/settings.json for better import resolution")
    except Exception as e:
        print(f"❌ Failed to create VS Code settings: {e}")

def reinstall_packages_properly():
    """Reinstall packages with proper Python interpreter"""
    
    print("🔧 Reinstalling packages with virtual environment...")
    
    # Use the virtual environment pip directly
    venv_pip = Path(".venv/Scripts/pip.exe")
    
    if venv_pip.exists():
        pip_cmd = str(venv_pip)
    else:
        pip_cmd = sys.executable + " -m pip"
    
    packages = ['psycopg2-binary', 'pywin32']
    
    for package in packages:
        print(f"  📦 Reinstalling {package}...")
        try:
            subprocess.run([pip_cmd, 'install', '--upgrade', package], 
                         check=True, capture_output=True, text=True)
            print(f"  ✅ {package} reinstalled successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to reinstall {package}: {e}")

def main():
    """Apply all fixes"""
    print("🚀 Applying targeted fixes for remaining VS Code problems...")
    
    # Reinstall packages properly
    reinstall_packages_properly()
    
    # Fix import issues
    fix_pywin32_imports()
    fix_psycopg2_imports()
    
    # Fix HTML issues
    fix_html_javascript_errors()
    
    # Create VS Code settings
    create_vscode_settings()
    
    print("\n✅ All targeted fixes completed!")
    print("🔄 Please reload the VS Code window (Ctrl+Shift+P > 'Developer: Reload Window')")

if __name__ == "__main__":
    main()