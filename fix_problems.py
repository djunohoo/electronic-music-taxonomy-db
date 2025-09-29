#!/usr/bin/env python3
"""
Fix VS Code Problems - Install missing packages and rename problem files
"""

import subprocess
import sys
import os
import shutil

def install_missing_packages():
    """Install missing Python packages"""
    print("=== INSTALLING MISSING PACKAGES ===")
    
    packages = [
        "librosa",
        "numpy", 
        "chromaprint",
        "pyacoustid",  # acoustid package name
        "soundfile",
        "psutil"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"[OK] {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] {package} failed: {e}")
        except Exception as e:
            print(f"[ERROR] {package} error: {e}")

def fix_documentation_files():
    """Rename .py files that contain markdown/documentation"""
    print("\n=== FIXING DOCUMENTATION FILES ===")
    
    problem_files = [
        "production_deploy_v32.py"
    ]
    
    for file_path in problem_files:
        if os.path.exists(file_path):
            new_name = file_path.replace(".py", ".md")
            try:
                shutil.move(file_path, new_name)
                print(f"[OK] Renamed {file_path} -> {new_name}")
            except Exception as e:
                print(f"[FAIL] Could not rename {file_path}: {e}")
        else:
            print(f"[SKIP] {file_path} not found")

def create_optional_imports():
    """Create wrapper for optional audio processing imports"""
    print("\n=== CREATING OPTIONAL IMPORT WRAPPERS ===")
    
    wrapper_content = '''"""
Optional Audio Processing Imports
Only import these if needed for advanced audio analysis
"""

# Optional audio processing libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("[INFO] librosa not available - advanced audio analysis disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[INFO] numpy not available - numerical processing limited")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("[INFO] soundfile not available - audio file I/O limited")

try:
    import chromaprint
    import acoustid
    FINGERPRINTING_AVAILABLE = True
except ImportError:
    FINGERPRINTING_AVAILABLE = False
    print("[INFO] audio fingerprinting not available")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[INFO] psutil not available - system monitoring limited")

def get_available_features():
    """Return dict of available optional features"""
    return {
        'librosa': LIBROSA_AVAILABLE,
        'numpy': NUMPY_AVAILABLE,
        'soundfile': SOUNDFILE_AVAILABLE,
        'fingerprinting': FINGERPRINTING_AVAILABLE,
        'system_monitoring': PSUTIL_AVAILABLE
    }
'''
    
    with open("optional_imports.py", "w") as f:
        f.write(wrapper_content)
    
    print("[OK] Created optional_imports.py wrapper")

def main():
    """Main fix routine"""
    print("FIXING VS CODE PROBLEMS")
    print("=" * 40)
    
    # Install missing packages
    install_missing_packages()
    
    # Fix documentation files
    fix_documentation_files()
    
    # Create optional import wrappers
    create_optional_imports()
    
    print("\n" + "=" * 40)
    print("PROBLEM FIXES COMPLETED")
    print("\nNext steps:")
    print("1. Restart VS Code to clear cached problems")
    print("2. Run the diagnostics again")
    print("3. Test dashboard startup")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError during fixes: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")