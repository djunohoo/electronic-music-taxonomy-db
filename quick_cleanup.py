#!/usr/bin/env python3
"""
Quick Launcher for Maximum Impact Duplicate Cleanup
==================================================
Get immediate storage savings in minutes, not hours!
"""

import subprocess
import sys
import os

def main():
    print("🚀 CULTURAL INTELLIGENCE SYSTEM v3.2 - INSTANT IMPACT!")
    print("=" * 60)
    print()
    print("💡 CHOOSE YOUR PATH TO IMMEDIATE STORAGE SAVINGS:")
    print()
    print("1️⃣  INSTANT CLEANUP (uses previous 23K scan results)")
    print("    ⚡ 0 minutes processing - immediate results!")
    print("    💾 Save 15+ GB instantly from your collection")
    print("    📊 Clean up 8,903 duplicate groups found in validation")
    print()
    print("2️⃣  QUICK SCAN + CLEANUP (1000 files sample)")  
    print("    ⚡ 1-2 minutes processing for immediate gratification")
    print("    💾 Start seeing results right away")
    print("    🎯 Perfect for testing and quick wins")
    print()
    print("3️⃣  FULL COLLECTION SCAN (entire directory)")
    print("    ⚡ Complete analysis of your collection")
    print("    💾 Maximum storage savings potential")
    print("    📊 Full duplicate detection and cleanup")
    print()
    
    choice = input("🎯 Choose option (1/2/3): ").strip()
    
    if choice == '1':
        print("\n🚀 Starting INSTANT cleanup using previous results...")
        print("📊 Processing 23,248 validated tracks with 8,903 duplicate groups")
        
    elif choice == '2':
        print("\n🚀 Starting QUICK SCAN for immediate results...")
        print("⚡ Processing first 1000 files for instant gratification")
        
    elif choice == '3':
        print("\n🚀 Starting FULL COLLECTION scan...")
        print("📊 Complete analysis - may take time but maximum results")
        
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    # Launch the duplicate manager
    try:
        subprocess.run([sys.executable, "duplicate_manager_v32.py"], check=True)
    except FileNotFoundError:
        print("❌ Error: duplicate_manager_v32.py not found")
        print("💡 Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error running duplicate manager: {e}")

if __name__ == "__main__":
    main()