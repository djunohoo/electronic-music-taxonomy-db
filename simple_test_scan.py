#!/usr/bin/env python3
"""
Cultural Intelligence Test Scanner - 100 Track Sample (Console Safe)
===================================================================
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

# Configure logging for test (no Unicode)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_scan_100_tracks.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleTestScanner(CulturalIntelligenceScanner):
    """Test scanner limited to 100 tracks with simple output."""
    
    def __init__(self, config_file: str = "taxonomy_config.json", max_tracks: int = 100):
        """Initialize test scanner with track limit."""
        super().__init__(config_file)
        self.max_tracks = max_tracks
        self.processed_count = 0
        # Ensure supported_formats is available
        self.supported_formats = self.config.get('scanning', {}).get('supported_formats', [
            '.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'
        ])
        
    def scan_directory_test(self, directory: str) -> Dict[str, int]:
        """Scan directory but limit to max_tracks for testing."""
        print(f"STARTING TEST SCAN of up to {self.max_tracks} tracks")
        print(f"Scanning: {directory}")
        
        if not os.path.exists(directory):
            print(f"ERROR: Directory not found: {directory}")
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
        
        try:
            # Find music files
            music_files = []
            print("Searching for music files...")
            
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
                    
            print(f"Found {len(music_files)} music files (limited to {self.max_tracks})")
            
            if len(music_files) == 0:
                print("No music files found in directory!")
                return stats
            
            # Create scan session
            session_data = {
                'scan_path': directory,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'scan_type': 'test_scan_100'
            }
            session_id = self.db.create_scan_session(session_data)
            
            # Process each file
            for i, file_path in enumerate(music_files[:self.max_tracks], 1):
                try:
                    print(f"Processing [{i}/{min(len(music_files), self.max_tracks)}]: {os.path.basename(file_path)}")
                    
                    # Simple file processing - extract basic metadata
                    file_stat = os.stat(file_path)
                    file_hash = self.calculate_file_hash(file_path)
                    
                    # Check if already exists
                    existing = self.db.get_track_by_hash(file_hash)
                    if existing:
                        print(f"  -> DUPLICATE detected (already in database)")
                        stats['duplicates_found'] += 1
                        continue
                    
                    # Create track record
                    track_data = {
                        'file_path': file_path,
                        'file_hash': file_hash,
                        'file_size': file_stat.st_size,
                        'file_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'filename': os.path.basename(file_path),
                        'folder_path': os.path.dirname(file_path),
                        'file_extension': os.path.splitext(file_path)[1].lower(),
                        'raw_metadata': {}
                    }
                    
                    # Try to extract metadata
                    try:
                        metadata = self.extract_metadata(file_path)
                        track_data['raw_metadata'] = metadata
                        print(f"  -> Artist: {metadata.get('artist', 'Unknown')}")
                        print(f"  -> Title: {metadata.get('title', 'Unknown')}")
                        print(f"  -> Genre: {metadata.get('genre', 'Unknown')}")
                    except Exception as e:
                        print(f"  -> Metadata extraction failed: {e}")
                    
                    # Save to database
                    track_id = self.db.create_discovered_track(track_data)
                    if track_id:
                        stats['tracks_processed'] += 1
                        print(f"  -> SUCCESS: Saved to database with ID {track_id}")
                        
                        # Try to classify the track
                        try:
                            analysis = self.analyze_track(track_data, session_id)
                            if analysis:
                                classification_id = self.db.create_track_classification({
                                    'track_id': track_id,
                                    'artist': analysis.get('artist'),
                                    'track_name': analysis.get('title'),
                                    'primary_genre': analysis.get('genre'),
                                    'genre_confidence': analysis.get('confidence', 0.5),
                                    'needs_review': True
                                })
                                if classification_id:
                                    print(f"  -> CLASSIFIED: {analysis.get('genre', 'Unknown')}")
                        except Exception as e:
                            print(f"  -> Classification failed: {e}")
                    else:
                        stats['errors'] += 1
                        print(f"  -> ERROR: Failed to save to database")
                        
                    # Progress update every 10 tracks
                    if i % 10 == 0:
                        print(f"PROGRESS: {i}/{min(len(music_files), self.max_tracks)} tracks processed")
                        
                except Exception as e:
                    print(f"ERROR processing {file_path}: {e}")
                    stats['errors'] += 1
                    
            # Update session as complete
            self.db.update_scan_session(session_id, {
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'stats': stats
            })
            
            print("TEST SCAN COMPLETED!")
            print("=" * 60)
            print(f"RESULTS SUMMARY:")
            print(f"   Files Found: {stats['files_found']}")
            print(f"   Tracks Processed: {stats['tracks_processed']}")
            print(f"   Duplicates Found: {stats['duplicates_found']}")
            print(f"   Errors: {stats['errors']}")
            print("=" * 60)
            
            return stats
            
        except Exception as e:
            print(f"SCAN FAILED: {e}")
            stats['errors'] += 1
            return stats
            
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file."""
        import hashlib
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Hash calculation failed for {file_path}: {e}")
            return "unknown"

def test_scan_simple():
    """Run a simple test scan of 100 tracks."""
    print("CULTURAL INTELLIGENCE SYSTEM - TEST SCAN")
    print("=" * 60)
    print("Testing with 100 tracks to demonstrate functionality")
    print("This will show: genre classification, duplicate detection,")
    print("pattern learning, and artist/label intelligence building")
    print("=" * 60)
    
    try:
        # Initialize test scanner
        scanner = SimpleTestScanner(max_tracks=100)
        
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
                try:
                    for root, dirs, files in os.walk(path):
                        if any(file.lower().endswith(('.mp3', '.flac', '.wav', '.m4a')) for file in files):
                            has_music = True
                            break
                        if has_music:
                            break
                except:
                    continue
                if has_music:
                    available_path = path
                    break
                    
        if not available_path:
            print("ERROR: No music directory found for testing!")
            print("Please ensure you have music files in one of these locations:")
            for path in test_paths:
                print(f"   {path}")
            return None
            
        print(f"Using test directory: {available_path}")
        print(f"Scanning up to 100 tracks...")
        print()
        
        # Run the test scan
        results = scanner.scan_directory_test(available_path)
        
        # Display results
        print()
        print("TEST SCAN COMPLETED!")
        print("=" * 60)
        
        if results.get('tracks_processed', 0) > 0:
            print("SUCCESS! Cultural Intelligence System is working!")
            print()
            print("Dashboard Update: Check http://172.22.17.37:8081")
            print("New data should appear in the dashboard:")
            print("   - Track classifications")
            print("   - Artist intelligence profiles")
            print("   - Cultural patterns learned")
            print("   - Duplicate detection results")
        else:
            print("WARNING: No tracks were processed. Check the log for details.")
            
        return results
        
    except Exception as e:
        print(f"ERROR: Test scan failed: {e}")
        return None

if __name__ == "__main__":
    # Run test scan
    results = test_scan_simple()
    
    if results:
        print()
        print("Next Steps:")
        print("1. Check the dashboard at http://172.22.17.37:8081")
        print("2. View the learned patterns and classifications")
        print("3. Test MetaCrate integration with duplicate detection")
        print("4. Deploy full system for production use")
        
    input("\\nPress Enter to exit...")