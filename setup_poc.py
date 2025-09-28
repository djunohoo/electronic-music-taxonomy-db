#!/usr/bin/env python3
"""
Setup script for Audio Fingerprinting POC
Installs dependencies and runs basic system checks
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("🔧 Installing POC requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_poc.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_audio_libraries():
    """Check if audio libraries are working"""
    print("\n🧪 Testing audio library imports...")
    
    # Core libraries (required)
    core_libraries = [
        ("librosa", "librosa"),
        ("numpy", "numpy")
    ]
    
    # Optional libraries
    optional_libraries = [
        ("chromaprint", "chromaprint"),
        ("acoustid", "acoustid")
    ]
    
    core_good = True
    
    print("  Core libraries (required):")
    for name, module in core_libraries:
        try:
            __import__(module)
            print(f"    ✅ {name}")
        except ImportError as e:
            print(f"    ❌ {name}: {e}")
            core_good = False
    
    print("  Optional libraries:")
    optional_count = 0
    for name, module in optional_libraries:
        try:
            __import__(module)
            print(f"    ✅ {name}")
            optional_count += 1
        except ImportError as e:
            print(f"    ⚠️  {name}: {e} (optional)")
    
    print(f"\n📊 Status: Core libraries {'✅ Ready' if core_good else '❌ Missing'}")
    print(f"📊 Optional: {optional_count}/{len(optional_libraries)} available")
    
    if core_good:
        print("✅ Ready to run fingerprinting POC!")
        if optional_count == 0:
            print("💡 Will use spectral analysis (often better for electronic music)")
    
    return core_good

def find_audio_directories():
    """Suggest potential audio directories to test with"""
    print("\n📁 Searching for potential audio directories...")
    
    # Common music directory locations
    potential_dirs = [
        Path.home() / "Music",
        Path("C:/Users") / os.environ.get("USERNAME", "") / "Music" if os.name == "nt" else None,
        Path("/Users") / os.environ.get("USER", "") / "Music" if os.name == "posix" else None,
        Path("./test_audio"),  # Local test directory
    ]
    
    # Filter out None values and check if directories exist
    existing_dirs = []
    for dir_path in potential_dirs:
        if dir_path and dir_path.exists():
            # Quick check for audio files
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aiff'}
            audio_files = []
            
            try:
                for ext in audio_extensions:
                    audio_files.extend(list(dir_path.rglob(f'*{ext}')))
                    if len(audio_files) >= 5:  # Stop after finding 5
                        break
                
                if audio_files:
                    existing_dirs.append((str(dir_path), len(audio_files)))
            except (PermissionError, OSError):
                continue
    
    if existing_dirs:
        print("Found directories with audio files:")
        for dir_path, count in existing_dirs:
            print(f"  📂 {dir_path} ({count}+ audio files)")
    else:
        print("  ⚠️  No audio directories found automatically")
        print("  💡 You'll need to specify a directory when running the POC")
    
    return existing_dirs

def main():
    """Main setup function"""
    print("🎵 Audio Fingerprinting POC Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("fingerprinting_poc.py").exists():
        print("❌ Please run this from the project directory containing fingerprinting_poc.py")
        return False
    
    # Install dependencies
    if not install_requirements():
        return False
    
    # Test imports
    if not check_audio_libraries():
        print("\n❌ Some libraries failed to import. Please check the error messages above.")
        return False
    
    # Find audio directories
    audio_dirs = find_audio_directories()
    
    print("\n🚀 Setup complete! Ready to run POC.")
    print("\nTo run the fingerprinting POC:")
    
    if audio_dirs:
        example_dir = audio_dirs[0][0]
        print(f"  python fingerprinting_poc.py \"{example_dir}\"")
    else:
        print("  python fingerprinting_poc.py \"<path_to_your_music_directory>\"")
    
    print("\nThe POC will:")
    print("  • Scan your directory for audio files")
    print("  • Test 3 different fingerprinting algorithms")
    print("  • Generate accuracy and performance reports")
    print("  • Save detailed results to fingerprinting_poc_report.json")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)