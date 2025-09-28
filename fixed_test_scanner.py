#!/usr/bin/env python3
"""
Fixed Cultural Intelligence Test Scanner
======================================
Properly working test scanner that addresses all identified issues.
"""

import os
import sys
import json
import logging
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cultural_database_client import EnhancedCulturalDatabaseClient

# Audio metadata extraction
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    print("Installing mutagen for audio metadata...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError

# Configure logging for test (UTF-8 encoding)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fixed_test_scan.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FixedTestScanner:
    """Fixed test scanner with proper classification and metadata extraction."""
    
    def __init__(self, config_file: str = "taxonomy_config.json", max_tracks: int = 100):
        """Initialize test scanner with all required methods."""
        self.max_tracks = max_tracks
        self.processed_count = 0
        
        # Load configuration
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Use default config
            self.config = {
                'scanning': {
                    'supported_formats': ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg']
                }
            }
            
        self.supported_formats = self.config.get('scanning', {}).get('supported_formats', [
            '.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'
        ])
        
        # Initialize database client
        try:
            self.db = EnhancedCulturalDatabaseClient(config_file)
            logger.info("Database client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database client: {e}")
            self.db = None
            
        # Genre classification patterns (simple rule-based system for testing)
        self.genre_patterns = {
            'Tech House': ['tech house', 'techhouse', 'tech-house'],
            'House': ['house', 'soulful house', 'jackin house', 'jackin\' house'],
            'Breakbeat': ['breakbeat', 'breaks', 'breakz', 'break beat'],
            'Techno': ['techno', 'tech', 'minimal', 'detroit'],
            'Trance': ['trance', 'uplifting', 'progressive trance'],
            'Drum & Bass': ['drum & bass', 'dnb', 'd&b', 'jungle'],
            'Dubstep': ['dubstep', 'dub step', 'dub-step'],
            'Electronic': ['electronic', 'electronica', 'dance', 'edm']
        }
        
    def scan_directory_fixed(self, directory: str) -> Dict[str, int]:
        """Fixed scan directory with proper error handling."""
        print(f"STARTING FIXED TEST SCAN of up to {self.max_tracks} tracks")
        print(f"Scanning: {directory}")
        
        if not os.path.exists(directory):
            print(f"ERROR: Directory not found: {directory}")
            return {'error': 1, 'tracks_processed': 0}
            
        if not self.db:
            print("ERROR: Database client not available")
            return {'error': 1, 'tracks_processed': 0}
            
        # Statistics
        stats = {
            'files_found': 0,
            'tracks_processed': 0,
            'tracks_classified': 0,
            'duplicates_found': 0,
            'patterns_learned': 0,
            'artist_profiles_created': 0,
            'unicode_errors': 0,
            'metadata_errors': 0,
            'database_errors': 0,
            'classification_errors': 0
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
                'scan_type': 'fixed_test_scan_100'
            }
            session_id = self.db.create_scan_session(session_data)
            
            # Process each file
            for i, file_path in enumerate(music_files[:self.max_tracks], 1):
                try:
                    print(f"Processing [{i}/{min(len(music_files), self.max_tracks)}]: {os.path.basename(file_path)}")
                    
                    # Calculate file hash for duplicate detection
                    file_hash = self.calculate_file_hash(file_path)
                    if not file_hash:
                        print(f"  -> ERROR: Could not calculate file hash")
                        stats['database_errors'] += 1
                        continue
                    
                    # Check if already exists
                    existing = self.db.get_track_by_hash(file_hash)
                    if existing:
                        print(f"  -> DUPLICATE detected (already in database)")
                        stats['duplicates_found'] += 1
                        continue
                    
                    # Get file stats
                    try:
                        file_stat = os.stat(file_path)
                    except Exception as e:
                        print(f"  -> ERROR: Could not get file stats: {e}")
                        stats['database_errors'] += 1
                        continue
                    
                    # Extract metadata with Unicode safety
                    metadata = self.extract_metadata_safe(file_path)
                    if 'error' in metadata:
                        print(f"  -> METADATA WARNING: {metadata['error']}")
                        stats['metadata_errors'] += 1
                    
                    # Clean metadata for database safety
                    clean_metadata = self.clean_metadata_for_database(metadata)
                    
                    # Create track data with safe strings
                    track_data = {
                        'file_path': self.clean_string(file_path),
                        'file_hash': file_hash,
                        'file_size': file_stat.st_size,
                        'file_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'filename': self.clean_string(os.path.basename(file_path)),
                        'folder_path': self.clean_string(os.path.dirname(file_path)),
                        'file_extension': os.path.splitext(file_path)[1].lower(),
                        'raw_metadata': clean_metadata
                    }
                    
                    print(f"  -> Artist: {clean_metadata.get('artist', 'Unknown')}")
                    print(f"  -> Title: {clean_metadata.get('title', 'Unknown')}")
                    print(f"  -> Genre: {clean_metadata.get('genre', 'Unknown')}")
                    
                    # Save to database
                    try:
                        track_id = self.db.create_discovered_track(track_data)
                        if track_id:
                            stats['tracks_processed'] += 1
                            print(f"  -> SUCCESS: Saved to database with ID {track_id}")
                            
                            # Classify the track
                            classification = self.analyze_track_fixed(track_data, clean_metadata)
                            if classification:
                                classification_data = {
                                    'track_id': track_id,
                                    'artist': classification.get('artist'),
                                    'track_name': classification.get('title'),
                                    'primary_genre': classification.get('genre'),
                                    'subgenre': classification.get('subgenre'),
                                    'genre_confidence': classification.get('confidence', 0.5),
                                    'classification_source': 'test_scanner_v2',
                                    'needs_review': classification.get('confidence', 0.5) < 0.8
                                }
                                
                                classification_id = self.db.create_track_classification(classification_data)
                                if classification_id:
                                    stats['tracks_classified'] += 1
                                    print(f"  -> CLASSIFIED: {classification.get('genre', 'Unknown')} (confidence: {classification.get('confidence', 0):.2f})")
                                else:
                                    stats['classification_errors'] += 1
                                    print(f"  -> CLASSIFICATION SAVE FAILED")
                            else:
                                stats['classification_errors'] += 1
                                print(f"  -> CLASSIFICATION FAILED")
                        else:
                            stats['database_errors'] += 1
                            print(f"  -> ERROR: Failed to save to database")
                    except Exception as e:
                        if "unsupported Unicode escape sequence" in str(e):
                            stats['unicode_errors'] += 1
                            print(f"  -> UNICODE ERROR: Skipping due to encoding issues")
                        else:
                            stats['database_errors'] += 1
                            print(f"  -> DATABASE ERROR: {e}")
                        
                    # Progress update every 10 tracks
                    if i % 10 == 0:
                        print(f"PROGRESS: {i}/{min(len(music_files), self.max_tracks)} tracks processed")
                        print(f"  -> Success: {stats['tracks_processed']}, Classified: {stats['tracks_classified']}")
                        print(f"  -> Errors: DB={stats['database_errors']}, Unicode={stats['unicode_errors']}")
                        
                except Exception as e:
                    print(f"ERROR processing {os.path.basename(file_path)}: {e}")
                    stats['database_errors'] += 1
                    
            # Update session as complete
            try:
                self.db.update_scan_session(session_id, {
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'stats': stats
                })
            except Exception as e:
                logger.error(f"Failed to update scan session: {e}")
            
            # Final results
            print("\\nFIXED TEST SCAN COMPLETED!")
            print("=" * 60)
            print(f"RESULTS SUMMARY:")
            print(f"   Files Found: {stats['files_found']}")
            print(f"   Tracks Processed: {stats['tracks_processed']}")
            print(f"   Tracks Classified: {stats['tracks_classified']}")
            print(f"   Duplicates Found: {stats['duplicates_found']}")
            print(f"\\nERROR BREAKDOWN:")
            print(f"   Unicode Errors: {stats['unicode_errors']}")
            print(f"   Metadata Errors: {stats['metadata_errors']}")
            print(f"   Database Errors: {stats['database_errors']}")
            print(f"   Classification Errors: {stats['classification_errors']}")
            print(f"\\nSUCCESS RATE: {stats['tracks_processed']}/{len(music_files[:self.max_tracks])} ({stats['tracks_processed']/min(len(music_files), self.max_tracks)*100:.1f}%)")
            print("=" * 60)
            
            return stats
            
        except Exception as e:
            print(f"CRITICAL SCAN FAILURE: {e}")
            logger.error(f"Scan failed: {e}")
            return stats
            
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate MD5 hash of file with error handling."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed for {file_path}: {e}")
            return None
            
    def extract_metadata_safe(self, file_path: str) -> Dict:
        """Extract metadata with comprehensive error handling."""
        metadata = {
            'artist': 'Unknown',
            'title': 'Unknown', 
            'genre': 'Unknown',
            'album': 'Unknown',
            'year': None,
            'bpm': None,
            'duration': None
        }
        
        try:
            # Try mutagen first
            audio_file = MutagenFile(file_path)
            if audio_file is not None:
                # Extract common tags
                if hasattr(audio_file, 'tags') and audio_file.tags:
                    tags = audio_file.tags
                    
                    # Artist
                    for key in ['TPE1', 'ARTIST', '\\xa9ART', 'Artist']:
                        if key in tags:
                            metadata['artist'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    # Title
                    for key in ['TIT2', 'TITLE', '\\xa9nam', 'Title']:
                        if key in tags:
                            metadata['title'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    # Genre
                    for key in ['TCON', 'GENRE', '\\xa9gen', 'Genre']:
                        if key in tags:
                            metadata['genre'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    # Album
                    for key in ['TALB', 'ALBUM', '\\xa9alb', 'Album']:
                        if key in tags:
                            metadata['album'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                
                # Duration
                if hasattr(audio_file, 'info') and audio_file.info and hasattr(audio_file.info, 'length'):
                    metadata['duration'] = int(audio_file.info.length)
                    
        except Exception as e:
            metadata['error'] = f"Mutagen extraction failed: {e}"
        
        # Fallback: extract from filename
        try:
            filename = os.path.basename(file_path)
            filename_parts = self.parse_filename(filename)
            
            # Use filename data if metadata is still unknown
            if metadata['artist'] == 'Unknown' and filename_parts.get('artist'):
                metadata['artist'] = filename_parts['artist']
                
            if metadata['title'] == 'Unknown' and filename_parts.get('title'):
                metadata['title'] = filename_parts['title']
                
            if metadata['genre'] == 'Unknown' and filename_parts.get('genre'):
                metadata['genre'] = filename_parts['genre']
                
        except Exception as e:
            if 'error' not in metadata:
                metadata['error'] = f"Filename parsing failed: {e}"
        
        return metadata
        
    def parse_filename(self, filename: str) -> Dict:
        """Parse artist, title, and genre from filename patterns."""
        parsed = {}
        
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Pattern 1: (Genre) Artist - Title (Mix).ext
        pattern1 = re.match(r'\\(([^)]+)\\)\\s*(.+?)\\s*-\\s*(.+)', name_without_ext)
        if pattern1:
            parsed['genre'] = pattern1.group(1).strip()
            parsed['artist'] = pattern1.group(2).strip()
            parsed['title'] = pattern1.group(3).strip()
            return parsed
        
        # Pattern 2: Artist - Title.ext
        pattern2 = re.match(r'(.+?)\\s*-\\s*(.+)', name_without_ext)
        if pattern2:
            parsed['artist'] = pattern2.group(1).strip()
            parsed['title'] = pattern2.group(2).strip()
            return parsed
        
        # Pattern 3: Just the filename as title
        parsed['title'] = name_without_ext
        return parsed
        
    def analyze_track_fixed(self, track_data: Dict, metadata: Dict) -> Optional[Dict]:
        """Fixed track analysis with proper genre classification."""
        try:
            # Get genre from metadata or filename
            detected_genre = metadata.get('genre', 'Unknown')
            artist = metadata.get('artist', 'Unknown')
            title = metadata.get('title', 'Unknown')
            
            # Classify genre using patterns
            classified_genre, confidence, subgenre = self.classify_genre(detected_genre, track_data['filename'])
            
            classification = {
                'artist': artist,
                'title': title,
                'genre': classified_genre,
                'subgenre': subgenre,
                'confidence': confidence,
                'source_genre': detected_genre,
                'classification_method': 'pattern_matching_v2'
            }
            
            return classification
            
        except Exception as e:
            logger.error(f"Track analysis failed: {e}")
            return None
            
    def classify_genre(self, detected_genre: str, filename: str) -> tuple:
        """Classify genre using pattern matching."""
        # Combine detected genre and filename for analysis
        text_to_analyze = f"{detected_genre} {filename}".lower()
        
        best_match = 'Electronic'  # Default
        best_confidence = 0.3
        best_subgenre = None
        
        # Check against known patterns
        for genre, patterns in self.genre_patterns.items():
            for pattern in patterns:
                if pattern in text_to_analyze:
                    confidence = 0.8  # High confidence for direct matches
                    
                    # Determine subgenre
                    subgenre = self.determine_subgenre(genre, text_to_analyze)
                    
                    if confidence > best_confidence:
                        best_match = genre
                        best_confidence = confidence
                        best_subgenre = subgenre
        
        # Special handling for specific genres
        if 'tech house' in text_to_analyze or 'techhouse' in text_to_analyze:
            return 'Tech House', 0.9, 'Main Room Tech House'
        elif 'progressive house' in text_to_analyze:
            return 'House', 0.8, 'Progressive House'
        elif 'deep house' in text_to_analyze:
            return 'House', 0.8, 'Deep House'
            
        return best_match, best_confidence, best_subgenre
        
    def determine_subgenre(self, genre: str, text: str) -> Optional[str]:
        """Determine subgenre based on genre and text analysis."""
        subgenre_patterns = {
            'House': {
                'Deep House': ['deep', 'deep house'],
                'Progressive House': ['progressive', 'prog'],
                'Tech House': ['tech', 'tech house', 'techhouse'],
                'Soulful House': ['soulful', 'soul'],
                'Jackin House': ['jackin', 'jacking']
            },
            'Techno': {
                'Minimal Techno': ['minimal', 'min'],
                'Detroit Techno': ['detroit'],
                'Hard Techno': ['hard', 'hard techno']
            },
            'Breakbeat': {
                'Progressive Breaks': ['progressive', 'prog'],
                'Electro Breaks': ['electro'],
                'Big Beat': ['big beat', 'bigbeat']
            }
        }
        
        if genre in subgenre_patterns:
            for subgenre, patterns in subgenre_patterns[genre].items():
                for pattern in patterns:
                    if pattern in text:
                        return subgenre
        
        return None
        
    def clean_string(self, text: str) -> str:
        """Clean string for database safety."""
        if not text:
            return ""
        
        # Remove null bytes and other problematic characters
        text = text.replace('\\x00', '').replace('\\u0000', '')
        
        # Remove other control characters
        text = re.sub(r'[\\x00-\\x1f\\x7f-\\x9f]', '', text)
        
        # Ensure it's proper UTF-8
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            text = str(text)
            
        return text[:255]  # Limit length for database
        
    def clean_metadata_for_database(self, metadata: Dict) -> Dict:
        """Clean all metadata strings for database safety."""
        clean_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, str):
                clean_metadata[key] = self.clean_string(value)
            elif isinstance(value, (int, float)):
                clean_metadata[key] = value
            elif value is None:
                clean_metadata[key] = None
            else:
                # Convert other types to string and clean
                clean_metadata[key] = self.clean_string(str(value))
                
        return clean_metadata

def run_fixed_test():
    """Run the fixed test scan."""
    print("CULTURAL INTELLIGENCE SYSTEM - FIXED TEST SCAN")
    print("=" * 60)
    print("Fixed version addressing all identified issues:")
    print("- Added proper analyze_track method")
    print("- Fixed Unicode encoding problems") 
    print("- Added comprehensive error handling")
    print("- Implemented genre classification system")
    print("=" * 60)
    
    try:
        # Initialize fixed scanner
        scanner = FixedTestScanner(max_tracks=100)
        
        # Get scan path from config
        scan_path = scanner.config.get('scan_path', 'X:\\\\lightbulb networ IUL Dropbox\\\\Automation\\\\MetaCrate\\\\USERS\\\\DJUNOHOO\\\\1-Originals')
        
        # Alternative test paths if main path not available
        test_paths = [
            scan_path,
            r"C:\\Users\\Public\\Music",
            r"E:\\Music",
            r"D:\\Music", 
            os.path.expanduser("~/Music")
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
            return None
            
        print(f"Using test directory: {available_path}")
        print()
        
        # Run the fixed test scan
        results = scanner.scan_directory_fixed(available_path)
        
        # Display final results
        print()
        if results.get('tracks_processed', 0) > 0:
            print("SUCCESS! Fixed Cultural Intelligence System working properly!")
            print()
            print("Dashboard Update: Check http://172.22.17.37:8081")
            print("New properly classified data should appear!")
        else:
            print("Issues detected. Check error breakdown above.")
            
        return results
        
    except Exception as e:
        print(f"ERROR: Fixed test scan failed: {e}")
        logger.error(f"Fixed test failed: {e}")
        return None

if __name__ == "__main__":
    results = run_fixed_test()
    
    if results:
        success_rate = results.get('tracks_processed', 0) / max(results.get('files_found', 1), 1) * 100
        print(f"\\nOverall Success Rate: {success_rate:.1f}%")
        
        if results.get('tracks_classified', 0) > 0:
            print("✅ Genre classification is working!")
        if results.get('unicode_errors', 0) == 0:
            print("✅ Unicode issues resolved!")
        if results.get('database_errors', 0) == 0:
            print("✅ Database integration stable!")
    
    input("\\nPress Enter to exit...")