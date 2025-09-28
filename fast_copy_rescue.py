#!/usr/bin/env python3
"""
Fast File Copy Alternatives
Optimized solutions for copying large music collections
"""

import subprocess
import os
from pathlib import Path

def suggest_copy_alternatives():
    """Suggest faster alternatives to Windows Explorer copy"""
    
    print("🚀 FAST COPY ALTERNATIVES FOR 23,000 FILES")
    print("="*60)
    print("Windows Explorer is NOT optimal for large file operations!\n")
    
    print("🔧 RECOMMENDED SOLUTIONS (in order of preference):")
    
    # Option 1: Robocopy (built into Windows)
    print("\n1. 🏆 ROBOCOPY (Built-in, Enterprise-grade)")
    print("   Command:")
    print('   robocopy "source_path" "destination_path" /E /COPYALL /MT:16 /R:1 /W:1')
    print("   Benefits:")
    print("     • Multi-threaded (16 threads)")
    print("     • Resumes on interruption")
    print("     • Progress reporting")
    print("     • 5-10x faster than Explorer")
    print("     • Enterprise reliability")
    
    # Option 2: PowerShell parallel copy
    print("\n2. 🚀 POWERSHELL PARALLEL COPY")
    print("   Command:")
    print('   Copy-Item "source_path\\*" "destination_path" -Recurse -Force -Verbose')
    print("   Benefits:")
    print("     • Native PowerShell")
    print("     • Good progress info")
    print("     • Reliable")
    
    # Option 3: TeraCopy (third party)
    print("\n3. 📦 TERACOPY (Free download)")
    print("   Website: codesector.com/teracopy")
    print("   Benefits:")
    print("     • GUI interface")
    print("     • Pause/resume")
    print("     • Verification")
    print("     • Very fast")
    
    print("\n⚠️  CURRENT EXPLORER COPY ISSUES:")
    print("   • Single-threaded (uses 1 core out of 16)")
    print("   • No resume capability")
    print("   • Poor error handling")
    print("   • Can take 6-12 hours vs 30-60 minutes")
    print("   • May fail on network hiccups")

def generate_robocopy_commands():
    """Generate optimized robocopy commands"""
    
    print(f"\n🎯 OPTIMIZED ROBOCOPY COMMANDS")
    print("="*40)
    
    print("Basic syntax:")
    print('robocopy "C:\\Source\\Music" "E:\\Destination\\Music" /E /COPYALL /MT:16 /R:1 /W:1 /TEE /LOG:copy.log')
    
    print(f"\nParameter explanation:")
    print("  /E          Copy subdirectories (including empty)")
    print("  /COPYALL    Copy all file attributes")
    print("  /MT:16      Use 16 threads (max for your CPU)")
    print("  /R:1        Retry once on failure")
    print("  /W:1        Wait 1 second between retries")
    print("  /TEE        Display progress in console")
    print("  /LOG:       Save detailed log")
    
    print(f"\n🚀 TURBO MODE (if source supports it):")
    print('robocopy "source" "dest" /E /COPYALL /MT:32 /R:0 /W:0 /J /TEE')
    print("  /MT:32      32 threads (aggressive)")
    print("  /R:0        No retries (fast)")
    print("  /J          Unbuffered I/O (faster for large files)")

def check_current_copy_status():
    """Check if there's a current copy operation and suggest how to handle it"""
    
    print(f"\n📊 CURRENT COPY MANAGEMENT")
    print("="*35)
    
    print("If Windows Explorer copy is running:")
    print("  1. 🛑 CANCEL IT (Ctrl+C or close window)")
    print("  2. 🧹 Check destination for partial files")
    print("  3. 🚀 Use robocopy to resume/restart")
    
    print(f"\n🔍 Check copy progress:")
    print("  • Open Task Manager → Performance → Disk")
    print("  • Look for sustained read/write activity")
    print("  • If speeds < 50 MB/s, consider switching")
    
    print(f"\n✅ Resume with robocopy:")
    print("  • Robocopy will skip already copied files")
    print("  • Only copies missing/different files")
    print("  • Safe to run over existing partial copy")

def estimate_copy_times():
    """Estimate copy times with different methods"""
    
    print(f"\n⏱️  COPY TIME ESTIMATES (23,000 files)")
    print("="*45)
    
    # Assumptions
    avg_file_size_mb = 8  # Average music file
    total_gb = (23000 * avg_file_size_mb) / 1024
    
    print(f"Assumed collection size: ~{total_gb:.0f} GB")
    print(f"(23,000 files × {avg_file_size_mb}MB average)")
    
    print(f"\nCopy method comparison:")
    print(f"  Windows Explorer:  4-8 hours    (single-threaded)")
    print(f"  Robocopy /MT:16:   30-60 minutes (multi-threaded)")
    print(f"  Robocopy /MT:32:   20-40 minutes (aggressive)")
    print(f"  TeraCopy:          45-90 minutes (optimized)")
    
    print(f"\n🎯 RAID0 SAS advantage:")
    print(f"  Your 4×SAS RAID0 can sustain 400-600 MB/s")
    print(f"  Robocopy with /MT:16 should max out the array")
    print(f"  Expected: 30-45 minutes for full copy")

def generate_copy_script():
    """Generate a ready-to-use copy script"""
    
    script_content = '''@echo off
REM Optimized Music Collection Copy Script
REM Replace SOURCE_PATH and DEST_PATH with your actual paths

echo Starting optimized music collection copy...
echo.

REM Create destination directory if needed
if not exist "DEST_PATH" mkdir "DEST_PATH"

REM Robocopy with optimal settings for music files
robocopy "SOURCE_PATH" "DEST_PATH" /E /COPYALL /MT:16 /R:2 /W:5 /TEE /LOG:music_copy.log

echo.
echo Copy complete! Check music_copy.log for details.
echo.
pause
'''
    
    with open("fast_copy.bat", "w") as f:
        f.write(script_content)
    
    print(f"\n📝 READY-TO-USE SCRIPT GENERATED")
    print("="*35)
    print("  File: fast_copy.bat")
    print("  Edit the SOURCE_PATH and DEST_PATH")
    print("  Run as Administrator for best performance")
    print("  Will create detailed log file")

def main():
    """Main copy optimization guide"""
    print("💾 WINDOWS EXPLORER COPY RESCUE MISSION")
    print("="*50)
    print("Converting slow Explorer copy to lightning-fast robocopy!\n")
    
    # Analysis and suggestions
    suggest_copy_alternatives()
    generate_robocopy_commands()
    check_current_copy_status()
    estimate_copy_times()
    generate_copy_script()
    
    print(f"\n🚀 RECOMMENDATION:")
    print("1. Cancel Windows Explorer copy if still running")
    print("2. Use robocopy command above")
    print("3. Should complete in 30-45 minutes vs 4-8 hours")
    print("4. Then run our fingerprinting test immediately!")
    
    print(f"\n⚡ With robocopy + RAID0 SAS, we'll have:")
    print("   • Files copied: 30-45 minutes")
    print("   • Sample test: 12 minutes")  
    print("   • Results: Within 1 hour total! 🎉")

if __name__ == "__main__":
    main()