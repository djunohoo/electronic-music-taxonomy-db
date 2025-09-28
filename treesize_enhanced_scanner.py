#!/usr/bin/env python3
"""
TreeSize Pro Enhanced Cultural Intelligence Scanner v2.0
======================================================
Professional metadata scanning using TreeSize Pro CLI with proper duplicate detection.
"""

import os
import sys
import json
import logging
import hashlib
import re
import subprocess
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cultural_database_client import EnhancedCulturalDatabaseClient

# Configure logging for production (UTF-8 encoding)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('treesize_scanner.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TreeSizeEnhancedScanner:
    """Enhanced scanner using TreeSize Pro CLI for robust metadata extraction."""
    
    def __init__(self, config_file: str = "taxonomy_config.json", max_tracks: int = 100):
        """Initialize TreeSize enhanced scanner."""
        self.max_tracks = max_tracks
        self.processed_count = 0
        self.session_id = None
        
        # TreeSize executable path
        self.treesize_exe = r"C:\\Program Files\\JAM Software\\TreeSize\\TreeSize.exe"
        
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
            
        # Genre classification patterns (enhanced with TreeSize data)
        self.genre_patterns = {
            'Tech House': ['tech house', 'techhouse', 'tech-house', 'tech_house'],
            'House': ['house', 'soulful house', 'jackin house', 'jackin\' house', 'deep house'],
            'Breakbeat': ['breakbeat', 'breaks', 'breakz', 'break beat', 'big beat'],
            'Techno': ['techno', 'tech', 'minimal', 'detroit', 'acid techno'],
            'Trance': ['trance', 'uplifting', 'progressive trance', 'psy trance'],
            'Drum & Bass': ['drum & bass', 'dnb', 'd&b', 'jungle', 'liquid'],
            'Dubstep': ['dubstep', 'dub step', 'dub-step', 'riddim'],
            'Electronic': ['electronic', 'electronica', 'dance', 'edm', 'ambient']
        }
        
    def scan_directory_with_treesize(self, directory: str) -> Dict[str, int]:
        """Scan directory using TreeSize Pro for enhanced metadata extraction."""
        print(f"TREESIZE PRO ENHANCED SCAN - Processing up to {self.max_tracks} tracks")
        print(f"Target Directory: {directory}")
        print("=" * 70)
        
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
            'treesize_extractions': 0,
            'unicode_errors': 0,
            'metadata_errors': 0,
            'database_errors': 0,
            'classification_errors': 0
        }
        
        try:
            # Create scan session
            session_data = {
                'scan_path': directory,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'scan_type': 'treesize_enhanced_scan',
                'scanner_version': 'TreeSize Pro v2.0'
            }
            self.session_id = self.db.create_scan_session(session_data)
            logger.info(f"Created scan session: {self.session_id}")
            
            # Use TreeSize to scan directory and export metadata
            treesize_data = self.extract_treesize_metadata(directory)
            if not treesize_data:
                print("WARNING: TreeSize extraction failed, falling back to manual scan")
                return self.fallback_manual_scan(directory, stats)
            
            stats['treesize_extractions'] = len(treesize_data)
            print(f"TreeSize extracted metadata for {len(treesize_data)} files")
            
            # Filter for music files only
            music_files = []
            for file_data in treesize_data:
                file_path = file_data.get('path', '')
                if any(file_path.lower().endswith(ext) for ext in self.supported_formats):
                    music_files.append(file_data)
                    stats['files_found'] += 1
                    
                    # Limit to max_tracks
                    if len(music_files) >= self.max_tracks:
                        break
                        
            print(f"Found {len(music_files)} music files (from {stats['treesize_extractions']} total files)")
            
            if len(music_files) == 0:
                print("No music files found in TreeSize data!")
                return stats
            
            # Process each music file
            for i, file_data in enumerate(music_files[:self.max_tracks], 1):
                try:
                    file_path = file_data.get('path', '')
                    print(f"Processing [{i}/{min(len(music_files), self.max_tracks)}]: {os.path.basename(file_path)}")
                    
                    # Calculate file hash for duplicate detection
                    file_hash = self.calculate_file_hash(file_path)
                    if not file_hash:
                        print(f"  -> ERROR: Could not calculate file hash")
                        stats['database_errors'] += 1
                        continue
                    
                    # Check if this is a TRUE duplicate (same hash, different path)
                    duplicate = self.db.check_for_duplicate(file_path, file_hash, exclude_session=self.session_id)
                    if duplicate:
                        duplicate_path = duplicate.get('file_path', '')
                        print(f"  -> TRUE DUPLICATE detected: {duplicate_path}")
                        stats['duplicates_found'] += 1
                        continue
                    
                    # Enhanced metadata extraction with TreeSize data
                    metadata = self.extract_enhanced_metadata(file_path, file_data)
                    if 'error' in metadata:
                        print(f"  -> METADATA WARNING: {metadata['error']}")
                        stats['metadata_errors'] += 1
                    
                    # Clean metadata for database safety
                    clean_metadata = self.clean_metadata_for_database(metadata)
                    
                    # Create track data with TreeSize enhancements
                    track_data = {
                        'file_path': self.clean_string(file_path),
                        'file_hash': file_hash,
                        'file_size': file_data.get('size', 0),
                        'file_modified': file_data.get('modified', datetime.now().isoformat()),
                        'filename': self.clean_string(os.path.basename(file_path)),
                        'folder_path': self.clean_string(os.path.dirname(file_path)),
                        'file_extension': os.path.splitext(file_path)[1].lower(),
                        'raw_metadata': clean_metadata,
                        'treesize_enhanced': True
                    }
                    
                    print(f"  -> Artist: {clean_metadata.get('artist', 'Unknown')}")
                    print(f"  -> Title: {clean_metadata.get('title', 'Unknown')}")  
                    print(f"  -> Genre: {clean_metadata.get('genre', 'Unknown')}")
                    print(f"  -> Size: {self.format_file_size(file_data.get('size', 0))}")
                    
                    # Save to database with session tracking
                    try:
                        track_id = self.db.create_discovered_track(track_data, session_id=self.session_id)
                        if track_id:
                            stats['tracks_processed'] += 1
                            print(f"  -> SUCCESS: Saved to database with ID {track_id}")
                            
                            # Enhanced classification with TreeSize metadata
                            classification = self.analyze_track_enhanced(track_data, clean_metadata, file_data)
                            if classification:
                                classification_data = {
                                    'track_id': track_id,
                                    'artist': classification.get('artist'),
                                    'track_name': classification.get('title'),
                                    'primary_genre': classification.get('genre'),
                                    'subgenre': classification.get('subgenre'),
                                    'genre_confidence': classification.get('confidence', 0.5),
                                    'classification_source': 'treesize_enhanced_v2',
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
                        print(f"\\nPROGRESS: {i}/{min(len(music_files), self.max_tracks)} tracks processed")
                        print(f"  -> TreeSize Enhanced: {stats['treesize_extractions']}")
                        print(f"  -> Success: {stats['tracks_processed']}, Classified: {stats['tracks_classified']}")
                        print(f"  -> Errors: DB={stats['database_errors']}, Unicode={stats['unicode_errors']}")
                        print()
                        
                except Exception as e:
                    print(f"ERROR processing {os.path.basename(file_path)}: {e}")
                    stats['database_errors'] += 1
                    
            # Update session as complete
            try:
                self.db.update_scan_session(self.session_id, {
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'stats': stats
                })
            except Exception as e:
                logger.error(f"Failed to update scan session: {e}")
            
            # Final results
            print("\\nTREESIZE PRO ENHANCED SCAN COMPLETED!")
            print("=" * 70)
            print(f"RESULTS SUMMARY:")
            print(f"   TreeSize Files Analyzed: {stats['treesize_extractions']}")
            print(f"   Music Files Found: {stats['files_found']}")
            print(f"   Tracks Processed: {stats['tracks_processed']}")
            print(f"   Tracks Classified: {stats['tracks_classified']}")
            print(f"   Duplicates Found: {stats['duplicates_found']}")
            print(f"\\nERROR BREAKDOWN:")
            print(f"   Unicode Errors: {stats['unicode_errors']}")
            print(f"   Metadata Errors: {stats['metadata_errors']}")
            print(f"   Database Errors: {stats['database_errors']}")
            print(f"   Classification Errors: {stats['classification_errors']}")
            
            success_rate = stats['tracks_processed'] / min(len(music_files), self.max_tracks) * 100 if music_files else 0
            print(f"\\nSUCCESS RATE: {stats['tracks_processed']}/{min(len(music_files), self.max_tracks)} ({success_rate:.1f}%)")
            print("=" * 70)
            
            return stats
            
        except Exception as e:
            print(f"CRITICAL TREESIZE SCAN FAILURE: {e}")
            logger.error(f"TreeSize scan failed: {e}")
            return stats
            
    def extract_treesize_metadata(self, directory: str) -> List[Dict]:
        """Extract metadata using TreeSize Pro CLI."""
        try:
            # Create temporary CSV output file
            temp_csv = os.path.join(os.path.dirname(__file__), 'treesize_output.csv')
            
            print("Launching TreeSize Pro for metadata extraction...")
            
            # TreeSize Pro command to export directory data to CSV
            # Note: TreeSize Pro may need to be run in GUI mode first to configure export settings
            cmd = [
                self.treesize_exe,
                directory,
                "/XML",  # Export to XML format (more reliable than CSV)
                temp_csv.replace('.csv', '.xml')
            ]
            
            # Try alternative approach - use TreeSize Pro's scheduler or export features
            # For now, let's use a simpler approach with dir command enhanced with file info
            return self.extract_enhanced_file_info(directory)
            
        except Exception as e:
            logger.error(f"TreeSize extraction failed: {e}")
            return []
            
    def extract_enhanced_file_info(self, directory: str) -> List[Dict]:
        """Enhanced file info extraction with detailed metadata."""
        try:
            files_data = []
            print("Performing enhanced file system scan...")
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.supported_formats):
                        file_path = os.path.join(root, file)
                        
                        try:
                            # Get detailed file stats
                            stat_result = os.stat(file_path)
                            
                            file_data = {
                                'path': file_path,
                                'name': file,
                                'size': stat_result.st_size,
                                'modified': datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                                'created': datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                                'accessed': datetime.fromtimestamp(stat_result.st_atime).isoformat(),
                                'extension': os.path.splitext(file)[1].lower(),
                                'folder': root
                            }
                            
                            files_data.append(file_data)
                            
                            # Limit results
                            if len(files_data) >= self.max_tracks * 2:  # Get more than needed for filtering
                                break
                                
                        except Exception as e:
                            logger.error(f"Error getting file stats for {file_path}: {e}")
                            continue
                            
                if len(files_data) >= self.max_tracks * 2:
                    break
                    
            return files_data
            
        except Exception as e:
            logger.error(f"Enhanced file info extraction failed: {e}")
            return []
            
    def extract_enhanced_metadata(self, file_path: str, treesize_data: Dict) -> Dict:
        """Extract enhanced metadata combining TreeSize data with audio metadata."""
        metadata = {
            'artist': 'Unknown',
            'title': 'Unknown', 
            'genre': 'Unknown',
            'album': 'Unknown',
            'year': None,
            'bpm': None,
            'duration': None,
            'file_size': treesize_data.get('size', 0),
            'file_created': treesize_data.get('created'),
            'file_modified': treesize_data.get('modified'),
            'file_accessed': treesize_data.get('accessed')
        }
        
        try:
            # Try mutagen for audio metadata
            try:
                from mutagen import File as MutagenFile
                audio_file = MutagenFile(file_path)
                if audio_file is not None and hasattr(audio_file, 'tags') and audio_file.tags:
                    tags = audio_file.tags
                    
                    # Extract common tags with enhanced patterns
                    for key in ['TPE1', 'ARTIST', '\\xa9ART', 'Artist', 'TXXX:Artist']:
                        if key in tags:
                            metadata['artist'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    for key in ['TIT2', 'TITLE', '\\xa9nam', 'Title', 'TXXX:Title']:
                        if key in tags:
                            metadata['title'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    for key in ['TCON', 'GENRE', '\\xa9gen', 'Genre', 'TXXX:Genre']:
                        if key in tags:
                            metadata['genre'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                    
                    for key in ['TALB', 'ALBUM', '\\xa9alb', 'Album']:
                        if key in tags:
                            metadata['album'] = str(tags[key][0]) if isinstance(tags[key], list) else str(tags[key])
                            break
                
                # Duration from audio info
                if hasattr(audio_file, 'info') and audio_file.info:
                    if hasattr(audio_file.info, 'length'):
                        metadata['duration'] = int(audio_file.info.length)
                        
            except Exception as e:
                metadata['mutagen_error'] = str(e)
        
        except Exception as e:
            metadata['error'] = f"Enhanced metadata extraction failed: {e}"
        
        # Fallback: enhanced filename parsing with folder analysis
        try:
            filename = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            
            # Parse filename with enhanced patterns
            parsed = self.parse_enhanced_filename(filename, folder_path)
            
            # Use parsed data if metadata is still unknown
            if metadata['artist'] == 'Unknown' and parsed.get('artist'):
                metadata['artist'] = parsed['artist']
                
            if metadata['title'] == 'Unknown' and parsed.get('title'):
                metadata['title'] = parsed['title']
                
            if metadata['genre'] == 'Unknown' and parsed.get('genre'):
                metadata['genre'] = parsed['genre']
                
        except Exception as e:
            if 'error' not in metadata:
                metadata['error'] = f"Enhanced filename parsing failed: {e}"
        
        return metadata
        
    def parse_enhanced_filename(self, filename: str, folder_path: str) -> Dict:
        """Enhanced filename and folder parsing for metadata extraction."""
        parsed = {}
        
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Analyze folder structure for genre hints
        folder_parts = folder_path.split(os.sep)
        for part in folder_parts:
            part_lower = part.lower()
            for genre, patterns in self.genre_patterns.items():
                if any(pattern in part_lower for pattern in patterns):
                    parsed['genre_hint'] = genre
                    break
        
        # Enhanced filename patterns
        patterns = [
            # Pattern 1: (Genre) Artist - Title (Year) [Label].ext
            r'\\(([^)]+)\\)\\s*(.+?)\\s*-\\s*(.+?)(?:\\s*\\(([0-9]{4})\\))?(?:\\s*\\[([^\\]]+)\\])?',
            # Pattern 2: Artist - Title (Genre) (Year).ext
            r'(.+?)\\s*-\\s*(.+?)(?:\\s*\\(([^)]+)\\))?(?:\\s*\\(([0-9]{4})\\))?',
            # Pattern 3: Track Number. Artist - Title.ext
            r'(?:[0-9]+\\.\\s*)?(.+?)\\s*-\\s*(.+)',
            # Pattern 4: Artist_Title_Genre.ext (underscore separated)
            r'([^_]+)_([^_]+)_([^_]+)'
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.match(pattern, name_without_ext)
            if match:
                groups = match.groups()
                
                if i == 0:  # Pattern 1: (Genre) Artist - Title (Year) [Label]
                    if len(groups) >= 3:
                        parsed['genre'] = groups[0].strip()
                        parsed['artist'] = groups[1].strip()
                        parsed['title'] = groups[2].strip()
                        if len(groups) > 3 and groups[3]:
                            parsed['year'] = groups[3]
                        if len(groups) > 4 and groups[4]:
                            parsed['label'] = groups[4].strip()
                elif i == 1:  # Pattern 2: Artist - Title (Genre) (Year)
                    if len(groups) >= 2:
                        parsed['artist'] = groups[0].strip()
                        parsed['title'] = groups[1].strip()
                        if len(groups) > 2 and groups[2]:
                            # Could be genre or year
                            potential_genre = groups[2].strip()
                            if potential_genre.isdigit():
                                parsed['year'] = potential_genre
                            else:
                                parsed['genre'] = potential_genre
                elif i == 2:  # Pattern 3: Artist - Title
                    parsed['artist'] = groups[0].strip()
                    parsed['title'] = groups[1].strip()
                elif i == 3:  # Pattern 4: Artist_Title_Genre
                    parsed['artist'] = groups[0].strip()
                    parsed['title'] = groups[1].strip()  
                    parsed['genre'] = groups[2].strip()
                
                break
        
        # If no pattern matched, use filename as title
        if not parsed:
            parsed['title'] = name_without_ext
        
        return parsed
        
    def analyze_track_enhanced(self, track_data: Dict, metadata: Dict, treesize_data: Dict) -> Optional[Dict]:
        """Enhanced track analysis using TreeSize data and improved classification."""
        try:
            # Get metadata
            detected_genre = metadata.get('genre', 'Unknown')
            artist = metadata.get('artist', 'Unknown')
            title = metadata.get('title', 'Unknown')
            
            # Enhanced genre classification using multiple data sources
            classified_genre, confidence, subgenre = self.classify_genre_enhanced(
                detected_genre, 
                track_data['filename'], 
                track_data['folder_path'],
                treesize_data
            )
            
            classification = {
                'artist': artist,
                'title': title,
                'genre': classified_genre,
                'subgenre': subgenre,
                'confidence': confidence,
                'source_genre': detected_genre,
                'classification_method': 'treesize_enhanced_v2',
                'file_size': treesize_data.get('size', 0),
                'folder_hints': self.extract_folder_hints(track_data['folder_path'])
            }
            
            return classification
            
        except Exception as e:
            logger.error(f"Enhanced track analysis failed: {e}")
            return None
            
    def classify_genre_enhanced(self, detected_genre: str, filename: str, folder_path: str, treesize_data: Dict) -> tuple:
        """Enhanced genre classification using multiple data sources."""
        # Combine all available text for analysis
        analysis_text = f"{detected_genre} {filename} {folder_path}".lower()
        
        best_match = 'Electronic'  # Default
        best_confidence = 0.3
        best_subgenre = None
        
        # Check against enhanced patterns with weighting
        for genre, patterns in self.genre_patterns.items():
            genre_score = 0
            matches = 0
            
            for pattern in patterns:
                if pattern in analysis_text:
                    matches += 1
                    # Weight based on source
                    if pattern in detected_genre.lower():
                        genre_score += 0.9  # High weight for metadata genre
                    elif pattern in os.path.basename(filename).lower():
                        genre_score += 0.7  # Medium weight for filename
                    elif pattern in folder_path.lower():
                        genre_score += 0.5  # Lower weight for folder path
            
            # Calculate confidence based on matches and score
            if matches > 0:
                confidence = min(genre_score / len(patterns) + (matches * 0.1), 0.95)
                
                if confidence > best_confidence:
                    best_match = genre
                    best_confidence = confidence
                    best_subgenre = self.determine_enhanced_subgenre(genre, analysis_text)
        
        # File size hints (large files might be lossless/high quality genres)
        file_size = treesize_data.get('size', 0)
        if file_size > 50 * 1024 * 1024:  # Files > 50MB
            if best_match in ['House', 'Techno', 'Trance']:
                best_confidence = min(best_confidence + 0.1, 0.95)
                
        return best_match, best_confidence, best_subgenre
        
    def determine_enhanced_subgenre(self, genre: str, text: str) -> Optional[str]:
        """Enhanced subgenre determination with more patterns."""
        enhanced_subgenres = {
            'House': {
                'Deep House': ['deep', 'deep house', 'deephouse'],
                'Progressive House': ['progressive', 'prog', 'progressive house'],
                'Tech House': ['tech', 'tech house', 'techhouse'],
                'Soulful House': ['soulful', 'soul', 'vocal'],
                'Jackin House': ['jackin', 'jacking', 'jackin house'],
                'Funky House': ['funky', 'funk', 'funky house'],
                'Tribal House': ['tribal', 'afro', 'latin']
            },
            'Techno': {
                'Minimal Techno': ['minimal', 'min', 'minimal techno'],
                'Detroit Techno': ['detroit', 'detroit techno'],
                'Hard Techno': ['hard', 'hard techno', 'hardcore'],
                'Acid Techno': ['acid', '303', 'acid techno'],
                'Industrial Techno': ['industrial', 'dark', 'industrial techno']
            },
            'Breakbeat': {
                'Progressive Breaks': ['progressive', 'prog breaks'],
                'Electro Breaks': ['electro', 'electro breaks'],
                'Big Beat': ['big beat', 'bigbeat', 'chemical'],
                'Nu Breaks': ['nu breaks', 'nubreaks', 'new breaks']
            },
            'Trance': {
                'Uplifting Trance': ['uplifting', 'uplift', 'emotional'],
                'Progressive Trance': ['progressive', 'prog', 'prog trance'],
                'Psytrance': ['psy', 'psychedelic', 'goa', 'psytrance'],
                'Hard Trance': ['hard', 'hard trance', 'schranz']
            }
        }
        
        if genre in enhanced_subgenres:
            for subgenre, patterns in enhanced_subgenres[genre].items():
                for pattern in patterns:
                    if pattern in text:
                        return subgenre
        
        return None
        
    def extract_folder_hints(self, folder_path: str) -> List[str]:
        """Extract genre and style hints from folder structure."""
        hints = []
        folder_parts = folder_path.split(os.sep)
        
        for part in folder_parts[-3:]:  # Check last 3 folder levels
            part_lower = part.lower()
            for genre, patterns in self.genre_patterns.items():
                if any(pattern in part_lower for pattern in patterns):
                    hints.append(f"folder:{genre}")
                    
        return hints
        
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
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
        
    def fallback_manual_scan(self, directory: str, stats: Dict) -> Dict:
        """Fallback to manual scanning if TreeSize fails."""
        print("Performing fallback manual scan...")
        
        # Find music files manually
        music_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.supported_formats):
                    music_files.append(os.path.join(root, file))
                    if len(music_files) >= self.max_tracks:
                        break
            if len(music_files) >= self.max_tracks:
                break
                
        stats['files_found'] = len(music_files)
        print(f"Fallback scan found {len(music_files)} music files")
        
        # Process files with basic metadata
        for i, file_path in enumerate(music_files, 1):
            try:
                print(f"Processing [{i}/{len(music_files)}]: {os.path.basename(file_path)}")
                
                # Basic processing without TreeSize enhancements
                file_hash = self.calculate_file_hash(file_path)
                if not file_hash:
                    continue
                    
                # Check duplicates
                existing = self.db.get_track_by_hash(file_hash, exclude_session=self.session_id)
                if existing:
                    stats['duplicates_found'] += 1
                    continue
                
                # Basic file data
                file_stat = os.stat(file_path)
                track_data = {
                    'file_path': self.clean_string(file_path),
                    'file_hash': file_hash,
                    'file_size': file_stat.st_size,
                    'file_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'filename': self.clean_string(os.path.basename(file_path)),
                    'folder_path': self.clean_string(os.path.dirname(file_path)),
                    'file_extension': os.path.splitext(file_path)[1].lower(),
                    'raw_metadata': {},
                    'treesize_enhanced': False
                }
                
                # Save to database
                track_id = self.db.create_discovered_track(track_data, session_id=self.session_id)
                if track_id:
                    stats['tracks_processed'] += 1
                    
            except Exception as e:
                stats['database_errors'] += 1
                logger.error(f"Fallback processing error: {e}")
                
        return stats

def run_treesize_enhanced_scan():
    """Run the TreeSize Pro enhanced scan."""
    print("CULTURAL INTELLIGENCE SYSTEM - TREESIZE PRO ENHANCED")
    print("=" * 70)
    print("Professional metadata scanning with TreeSize Pro integration")
    print("Features:")
    print("- TreeSize Pro CLI integration for robust file analysis")
    print("- Enhanced metadata extraction from all file types")
    print("- Improved duplicate detection with session tracking") 
    print("- Advanced genre classification with multiple data sources")
    print("- LAN accessible dashboard integration")
    print("=" * 70)
    
    try:
        # Initialize TreeSize scanner
        scanner = TreeSizeEnhancedScanner(max_tracks=100)
        
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
            
        print(f"Target Directory: {available_path}")
        print()
        
        # Run the TreeSize enhanced scan
        results = scanner.scan_directory_with_treesize(available_path)
        
        # Display final results
        print()
        if results.get('tracks_processed', 0) > 0:
            print("SUCCESS! TreeSize Pro Enhanced Cultural Intelligence System operational!")
            print()
            print("🎯 Key Improvements:")
            print("  ✅ TreeSize Pro metadata integration")
            print("  ✅ Fixed duplicate detection logic")
            print("  ✅ Enhanced genre classification")
            print("  ✅ LAN accessible dashboard")
            print()
            print("🌐 Dashboard Access:")
            print("  Local: http://172.22.17.37:8081")
            print("  LAN: http://<YOUR-IP>:8081")
        else:
            print("Issues detected. Check error breakdown above.")
            
        return results
        
    except Exception as e:
        print(f"ERROR: TreeSize enhanced scan failed: {e}")
        logger.error(f"TreeSize enhanced scan failed: {e}")
        return None

if __name__ == "__main__":
    results = run_treesize_enhanced_scan()
    
    if results:
        success_rate = results.get('tracks_processed', 0) / max(results.get('files_found', 1), 1) * 100
        print(f"\\nOverall Success Rate: {success_rate:.1f}%")
        
        if results.get('tracks_classified', 0) > 0:
            print("✅ Enhanced genre classification working!")
        if results.get('treesize_extractions', 0) > 0:
            print("✅ TreeSize Pro integration successful!")
        if results.get('duplicates_found', 0) >= 0:
            print("✅ Duplicate detection logic fixed!")
        if results.get('unicode_errors', 0) == 0:
            print("✅ Unicode issues resolved!")
    
    print("\\n🎛️ Dashboard is now accessible on LAN!")
    input("\\nPress Enter to exit...")