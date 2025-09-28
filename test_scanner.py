#!/usr/bin/env python3
"""
Cultural Intelligence Scanner - Quick Test
==========================================
Test the scanner with a small sample to verify everything works.
"""

import os
import json
import sys
from pathlib import Path
from cultural_intelligence_scanner import CulturalIntelligenceScanner

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    
    try:
        from cultural_database_client import CulturalDatabaseClient
        client = CulturalDatabaseClient()
        
        # Test basic operations
        tracks_count = client.count_discovered_tracks()
        patterns_count = client.count_learned_patterns()
        
        print(f"✅ Database connected successfully")
        print(f"   Existing tracks: {tracks_count}")
        print(f"   Learned patterns: {patterns_count}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_config_file():
    """Test configuration file."""
    print("\n🔍 Testing configuration file...")
    
    config_path = "taxonomy_config.json"
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
        
    try:
        with open(config_path) as f:
            config = json.load(f)
            
        # Check required fields
        if 'supabase' not in config:
            print("❌ Missing 'supabase' section in config")
            return False
            
        if 'url' not in config['supabase']:
            print("❌ Missing 'url' in supabase config")
            return False
            
        if 'service_role_key' not in config['supabase']:
            print("❌ Missing 'service_role_key' in supabase config")
            return False
            
        print("✅ Configuration file is valid")
        
        # Check scan path
        scan_path = config.get('scan_path')
        if scan_path:
            if os.path.exists(scan_path):
                print(f"✅ Scan directory exists: {scan_path}")
            else:
                print(f"⚠️ Scan directory not found: {scan_path}")
                print("   (This is OK for testing)")
        else:
            print("⚠️ No scan_path configured, using default")
            
        return True
        
    except Exception as e:
        print(f"❌ Config file error: {e}")
        return False

def test_scanner_initialization():
    """Test scanner initialization."""
    print("\n🔍 Testing scanner initialization...")
    
    try:
        scanner = CulturalIntelligenceScanner()
        print("✅ Scanner initialized successfully")
        
        # Test status
        status = scanner.get_status()
        print(f"   Scanner running: {status['running']}")
        print(f"   Total tracks: {status['total_tracks']}")
        print(f"   Total patterns: {status['total_patterns']}")
        
        return True, scanner
        
    except Exception as e:
        print(f"❌ Scanner initialization failed: {e}")
        return False, None

def test_file_processing(scanner):
    """Test file processing with a sample file."""
    print("\n🔍 Testing file processing...")
    
    # Look for any audio file in common directories
    test_paths = [
        "C:\\Users\\Administrator\\Music",
        "C:\\Users\\Public\\Music", 
        "D:\\Music",
        "E:\\Music"
    ]
    
    audio_extensions = {'.mp3', '.flac', '.wav', '.m4a'}
    test_file = None
    
    for test_path in test_paths:
        if os.path.exists(test_path):
            for root, dirs, files in os.walk(test_path):
                for file in files:
                    if Path(file).suffix.lower() in audio_extensions:
                        test_file = os.path.join(root, file)
                        break
                if test_file:
                    break
            if test_file:
                break
    
    if not test_file:
        print("⚠️ No audio files found for testing")
        print("   File processing test skipped")
        return True
        
    try:
        print(f"   Testing with: {Path(test_file).name}")
        
        # Test file hash calculation
        file_hash = scanner.calculate_file_hash(test_file)
        if file_hash:
            print(f"✅ File hash calculated: {file_hash[:16]}...")
        else:
            print("❌ File hash calculation failed")
            return False
            
        # Test metadata extraction
        metadata = scanner.extract_metadata(test_file)
        if metadata:
            print(f"✅ Metadata extracted: {len(metadata)} fields")
            if metadata.get('artist'):
                print(f"   Artist: {metadata['artist']}")
            if metadata.get('title'):
                print(f"   Title: {metadata['title']}")
        else:
            print("⚠️ No metadata extracted (file may not have tags)")
            
        # Test filename analysis
        filename_analysis = scanner.analyze_filename(Path(test_file).name)
        print(f"✅ Filename analysis completed")
        if filename_analysis['artist']:
            print(f"   Filename artist: {filename_analysis['artist']}")
            
        return True
        
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CULTURAL INTELLIGENCE SCANNER - SYSTEM TEST")
    print("=" * 60)
    
    # Test database
    db_ok = test_database_connection()
    
    # Test config
    config_ok = test_config_file()
    
    # Test scanner
    scanner_ok, scanner = test_scanner_initialization()
    
    # Test file processing
    if scanner_ok and scanner:
        file_ok = test_file_processing(scanner)
    else:
        file_ok = False
        
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Configuration File:  {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Scanner Init:        {'✅ PASS' if scanner_ok else '❌ FAIL'}")
    print(f"File Processing:     {'✅ PASS' if file_ok else '❌ FAIL'}")
    
    if all([db_ok, config_ok, scanner_ok]):
        print("\n🎯 SYSTEM READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("   1. python service_manager.py install")
        print("   2. python service_manager.py start")
        print("   3. python service_manager.py status")
    else:
        print("\n❌ SYSTEM NOT READY - Please fix errors above")
        
    return all([db_ok, config_ok, scanner_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)