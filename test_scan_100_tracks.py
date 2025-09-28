#!/usr/bin/env python3
"""
Cultural Intelligence Test Scanner - 100 Track Sample
===================================================
Quick test scan of 100 tracks to demonstrate the Cultural Intelligence System.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cultural_intelligence_scanner import CulturalIntelligenceScanner

# Configure logging for test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_scan_100_tracks.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestScanner(CulturalIntelligenceScanner):
    """Test scanner limited to 100 tracks."""
    
    def __init__(self, config_file: str = "taxonomy_config.json", max_tracks: int = 100):
        """Initialize test scanner with track limit."""
        super().__init__(config_file)
        self.max_tracks = max_tracks
        self.processed_count = 0
        # Ensure supported_formats is available
        self.supported_formats = self.config.get('scanning', {}).get('supported_formats', [
            '.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'
        ])
        
    def scan_directory_limited(self, directory: str) -> Dict[str, int]:
        """Scan directory but limit to max_tracks for testing."""
        logger.info(f"🔍 Starting TEST SCAN of up to {self.max_tracks} tracks")
        logger.info(f"📁 Scanning: {directory}")
        
        if not os.path.exists(directory):
            logger.warning(f"❌ Directory not found: {directory}")
            return {'error': 1, 'tracks_processed': 0}
            
        # Statistics
        stats = {
            'files_found': 0,
            'tracks_processed': 0,
            'duplicates_found': 0,
            'patterns_learned': 0,
            'artist_profiles_created': 0,
            'label_profiles_created': 0,
            'errors': 0
        }
        
        # Create scan session
        session_data = {
            'scan_path': directory,
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'scan_type': 'test_scan_100'
        }
        session_id = self.db.create_scan_session(session_data)
        
        try:
            # Find music files
            music_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.supported_formats):
                        music_files.append(os.path.join(root, file))
                        stats['files_found'] += 1
                        
                        # Stop when we have enough files
                        if len(music_files) >= self.max_tracks:
                            break
                if len(music_files) >= self.max_tracks:
                    break
                    
            logger.info(f"🎵 Found {len(music_files)} music files (limited to {self.max_tracks})")
            
            # Process each file
            for i, file_path in enumerate(music_files[:self.max_tracks], 1):
                try:
                    logger.info(f"🎵 Processing [{i}/{min(len(music_files), self.max_tracks)}]: {os.path.basename(file_path)}")
                    
                    # Process the track
                    result = self.process_track(file_path, session_id)
                    
                    if result.get('success'):
                        stats['tracks_processed'] += 1
                        
                        if result.get('is_duplicate'):
                            stats['duplicates_found'] += 1
                            
                        if result.get('patterns_learned', 0) > 0:
                            stats['patterns_learned'] += result['patterns_learned']
                            
                        if result.get('artist_profile_created'):
                            stats['artist_profiles_created'] += 1
                            
                        if result.get('label_profile_created'):
                            stats['label_profiles_created'] += 1
                    else:
                        stats['errors'] += 1
                        
                    # Progress update every 10 tracks
                    if i % 10 == 0:
                        logger.info(f"📊 Progress: {i}/{min(len(music_files), self.max_tracks)} tracks processed")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path}: {e}")
                    stats['errors'] += 1
                    
            # Update session as complete
            self.db.update_scan_session(session_id, {
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'stats': stats
            })
            
            logger.info("🎉 TEST SCAN COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"📊 RESULTS SUMMARY:")
            logger.info(f"   🎵 Files Found: {stats['files_found']}")
            logger.info(f"   ✅ Tracks Processed: {stats['tracks_processed']}")
            logger.info(f"   🔍 Duplicates Found: {stats['duplicates_found']}")
            logger.info(f"   🧠 Patterns Learned: {stats['patterns_learned']}")
            logger.info(f"   🎤 Artist Profiles: {stats['artist_profiles_created']}")
            logger.info(f"   🏷️ Label Profiles: {stats['label_profiles_created']}")
            logger.info(f"   ❌ Errors: {stats['errors']}")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            self.db.update_scan_session(session_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })
            stats['errors'] += 1
            return stats

def test_scan_100_tracks():
    """Run a test scan of 100 tracks."""
    print("🎛️ CULTURAL INTELLIGENCE SYSTEM - TEST SCAN")
    print("=" * 60)
    print("🎯 Testing with 100 tracks to demonstrate functionality")
    print("📊 This will show: genre classification, duplicate detection,")
    print("   pattern learning, and artist/label intelligence building")
    print("=" * 60)
    
    try:
        # Initialize test scanner
        scanner = TestScanner(max_tracks=100)
        
        # Get scan path from config
        scan_path = scanner.config.get('scan_path', 'X:\\lightbulb networ IUL Dropbox\\Automation\\MetaCrate\\USERS\\DJUNOHOO\\1-Originals')
        
        # Alternative test paths if main path not available
        test_paths = [
            scan_path,
            r"C:\Users\Public\Music",  # Windows default
            r"E:\Music",  # Common music drive
            r"D:\Music",  # Alternative music drive
            os.path.expanduser("~/Music")  # User music folder
        ]
        
        # Find available test path
        available_path = None
        for path in test_paths:
            if os.path.exists(path):
                # Check if it has music files
                has_music = False
                for root, dirs, files in os.walk(path):
                    if any(file.lower().endswith(('.mp3', '.flac', '.wav', '.m4a')) for file in files):
                        has_music = True
                        break
                if has_music:
                    available_path = path
                    break
                    
        if not available_path:
            print("❌ No music directory found for testing!")
            print("💡 Please ensure you have music files in one of these locations:")
            for path in test_paths:
                print(f"   📁 {path}")
            return
            
        print(f"📁 Using test directory: {available_path}")
        print(f"🎵 Scanning up to 100 tracks...")
        print()
        
        # Run the test scan
        results = scanner.scan_directory_limited(available_path)
        
        # Display results
        print()
        print("🎉 TEST SCAN COMPLETED!")
        print("=" * 60)
        
        if results.get('tracks_processed', 0) > 0:
            print("✅ SUCCESS! Cultural Intelligence System is working!")
            print()
            print("🎛️ Dashboard Update: Check http://172.22.17.37:8081")
            print("📊 New data should appear in the dashboard:")
            print("   - Track classifications")
            print("   - Artist intelligence profiles")
            print("   - Cultural patterns learned")
            print("   - Duplicate detection results")
        else:
            print("⚠️ No tracks were processed. Check the log for details.")
            
        return results
        
    except Exception as e:
        logger.error(f"❌ Test scan failed: {e}")
        print(f"❌ Test scan failed: {e}")
        return None

if __name__ == "__main__":
    # Run test scan
    results = test_scan_100_tracks()
    
    if results:
        print()
        print("💡 Next Steps:")
        print("1. 🖥️ Check the dashboard at http://172.22.17.37:8081")
        print("2. 📊 View the learned patterns and classifications")
        print("3. 🎵 Test MetaCrate integration with duplicate detection")
        print("4. 🚀 Deploy full system for production use")
        
    input("\\n🎯 Press Enter to exit...")