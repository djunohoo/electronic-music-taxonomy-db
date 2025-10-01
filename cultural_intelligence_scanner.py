#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE SCANNER
============================
Automated music file scanning and intelligence building system.
Scans music directories every 6 hours, extracts metadata, detects duplicates,
analyzes filenames/folders/metadata for classification, builds artist/label profiles,
and continuously learns patterns for improved accuracy.
"""

import os
import sys
import hashlib
import json
import re
import time
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import schedule

# Audio metadata extraction
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    print("Installing required audio libraries...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError

# Database client
from cultural_database_client import CulturalDatabaseClient as SupabaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cultural_intelligence_scanner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CulturalIntelligenceScanner:
    """Main scanner class for automated music intelligence gathering."""
    
    def __init__(self, config_file: str = "taxonomy_config.json"):
        """Initialize scanner with configuration."""
        self.config = self._load_config(config_file)
        self.db = SupabaseClient()
        self.running = False
        self.scan_thread = None
        
        # Audio file extensions to scan
        self.audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
        
        # Pattern matching for filename analysis
        self.remix_patterns = [
            r'\(([^)]*(?:remix|mix|edit|version|rework)[^)]*)\)',
            r'\[([^\]]*(?:remix|mix|edit|version|rework)[^\]]*)\]',
        ]
        
        # Genre keywords for folder/filename analysis
        self.genre_keywords = {
            'house': ['house', 'deep house', 'tech house', 'progressive house', 'electro house'],
            'trance': ['trance', 'uplifting', 'progressive trance', 'psy trance', 'vocal trance'],
            'techno': ['techno', 'minimal', 'tech', 'industrial'],
            'dubstep': ['dubstep', 'brostep', 'melodic dubstep'],
            'drum_and_bass': ['drum and bass', 'dnb', 'jungle', 'liquid'],
            'breaks': ['breaks', 'breakbeat', 'nu breaks'],
            'ambient': ['ambient', 'chillout', 'downtempo', 'lounge']
        }
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_file} not found!")
            sys.exit(1)
            
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for duplicate detection."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
            
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract ALL metadata from audio file."""
        metadata = {}
        
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return metadata
                
            # Extract all available tags
            for key, value in audio_file.tags.items() if audio_file.tags else []:
                # Convert to string and clean up
                if isinstance(value, list):
                    metadata[key] = [str(v) for v in value]
                else:
                    metadata[key] = str(value)
                    
            # Extract common fields with standardized names
            if audio_file.tags:
                # Artist
                for artist_key in ['TPE1', 'ARTIST', 'albumartist', '©ART']:
                    if artist_key in audio_file.tags:
                        metadata['artist'] = str(audio_file.tags[artist_key][0])
                        break
                        
                # Title
                for title_key in ['TIT2', 'TITLE', '©nam']:
                    if title_key in audio_file.tags:
                        metadata['title'] = str(audio_file.tags[title_key][0])
                        break
                        
                # Album
                for album_key in ['TALB', 'ALBUM', '©alb']:
                    if album_key in audio_file.tags:
                        metadata['album'] = str(audio_file.tags[album_key][0])
                        break
                        
                # Genre
                for genre_key in ['TCON', 'GENRE', '©gen']:
                    if genre_key in audio_file.tags:
                        metadata['genre'] = str(audio_file.tags[genre_key][0])
                        break
                        
                # Year
                for year_key in ['TDRC', 'DATE', '©day']:
                    if year_key in audio_file.tags:
                        year_str = str(audio_file.tags[year_key][0])
                        # Extract year from date string
                        year_match = re.search(r'(\d{4})', year_str)
                        if year_match:
                            metadata['year'] = int(year_match.group(1))
                        break
                        
                # BPM
                for bpm_key in ['TBPM', 'BPM']:
                    if bpm_key in audio_file.tags:
                        try:
                            metadata['bpm'] = int(str(audio_file.tags[bpm_key][0]))
                        except ValueError:
                            pass
                        break
                        
                # Comment (often contains label/catalog info)
                for comment_key in ['COMM', 'COMMENT']:
                    if comment_key in audio_file.tags:
                        metadata['comment'] = str(audio_file.tags[comment_key][0])
                        break
                        
            # Audio properties
            if hasattr(audio_file, 'info') and audio_file.info:
                metadata['duration'] = getattr(audio_file.info, 'length', 0)
                metadata['bitrate'] = getattr(audio_file.info, 'bitrate', 0)
                metadata['channels'] = getattr(audio_file.info, 'channels', 0)
                metadata['sample_rate'] = getattr(audio_file.info, 'sample_rate', 0)
                
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            
        return metadata
        
    def analyze_filename(self, filename: str) -> Dict[str, Any]:
        """Analyze filename for artist, title, remix info, and genre hints."""
        analysis = {
            'artist': None,
            'title': None,
            'remix': None,
            'genre_hints': []
        }
        
        # Remove file extension
        name = Path(filename).stem
        
        # Extract remix/mix information
        for pattern in self.remix_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                analysis['remix'] = match.group(1).strip()
                name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
                break
                
        # Look for genre hints in filename
        name_lower = name.lower()
        for genre, keywords in self.genre_keywords.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    analysis['genre_hints'].append(genre)
                    
        # Try to parse artist - title format
        # Common patterns: "Artist - Title", "Artist_Title", "Artist Title"
        for separator in [' - ', '_', '  ']:
            if separator in name:
                parts = name.split(separator, 1)
                if len(parts) == 2:
                    analysis['artist'] = parts[0].strip()
                    analysis['title'] = parts[1].strip()
                    break
                    
        return analysis
        
    def analyze_folder_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze folder structure for genre and organizational hints."""
        path = Path(file_path)
        folders = [p.name.lower() for p in path.parents if p.name]
        
        analysis = {
            'genre_hints': [],
            'depth': len(folders),
            'structure': folders
        }
        
        # Look for genre indicators in folder names
        for folder in folders:
            for genre, keywords in self.genre_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in folder:
                        analysis['genre_hints'].append(genre)
                        
        return analysis
        
    def build_artist_profile(self, artist: str, tracks: List[Dict]) -> Dict[str, Any]:
        """Build/update artist intelligence profile."""
        if len(tracks) < 10:  # Need at least 10 tracks for reliable profile
            return None
            
        profile = {
            'name': artist,
            'normalized_name': artist.lower().replace(' ', '').replace('&', 'and'),
            'total_tracks': len(tracks),
            'genres': {},
            'labels': set(),
            'confidence': 0.0
        }
        
        # Analyze genre distribution
        genre_counts = {}
        for track in tracks:
            if track.get('genre'):
                genre = track['genre'].lower()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                
        # Calculate genre probabilities
        if genre_counts:
            total = len(tracks)
            for genre, count in genre_counts.items():
                profile['genres'][genre] = count / total
                
        # Collect labels
        for track in tracks:
            if track.get('label'):
                profile['labels'].add(track['label'])
                
        profile['labels'] = list(profile['labels'])
        
        # Calculate confidence based on consistency and sample size
        if profile['genres']:
            max_genre_ratio = max(profile['genres'].values())
            sample_confidence = min(len(tracks) / 50, 1.0)  # Max confidence at 50+ tracks
            profile['confidence'] = max_genre_ratio * sample_confidence
            
        return profile
        
    def learn_pattern(self, pattern_type: str, pattern_value: str, 
                     genre: str, confidence: float) -> None:
        """Learn or reinforce a classification pattern."""
        try:
            # Check if pattern exists
            existing = self.db.get_patterns(pattern_type, pattern_value, genre)
            
            if existing:
                # Reinforce existing pattern
                pattern = existing[0]
                old_confidence = pattern['confidence']
                new_sample_size = pattern['sample_size'] + 1
                
                # Update confidence using weighted average
                weight = 0.1  # Learning rate
                new_confidence = old_confidence * (1 - weight) + confidence * weight
                
                self.db.update_pattern(
                    pattern['id'],
                    confidence=new_confidence,
                    sample_size=new_sample_size,
                    reinforcement_count=pattern.get('reinforcement_count', 1) + 1
                )
                logger.debug(f"Reinforced pattern: {pattern_type}={pattern_value} -> {genre}")
            else:
                # Create new pattern
                self.db.create_pattern(
                    pattern_type=pattern_type,
                    pattern_value=pattern_value,
                    genre=genre,
                    confidence=confidence,
                    sample_size=1
                )
                logger.info(f"Learned new pattern: {pattern_type}={pattern_value} -> {genre}")
                
        except Exception as e:
            logger.error(f"Error learning pattern: {e}")
            
    def classify_track(self, track_data: Dict) -> Dict[str, Any]:
        """Classify track using learned patterns and profiles."""
        classification = {
            'artist': None,
            'track_name': None,
            'remix_info': None,
            'label': None,
            'primary_genre': None,
            'secondary_genre': None,
            'subgenre': None,
            'confidence_scores': {},
            'sources': []
        }
        
        # Get filename analysis
        filename_analysis = self.analyze_filename(track_data['filename'])
        folder_analysis = self.analyze_folder_structure(track_data['file_path'])
        
        # Extract from metadata first (most reliable)
        if track_data.get('raw_metadata'):
            metadata = track_data['raw_metadata']
            if metadata.get('artist'):
                classification['artist'] = metadata['artist']
                classification['confidence_scores']['artist'] = 0.95
                classification['sources'].append('metadata_artist')
                
            if metadata.get('title'):
                classification['track_name'] = metadata['title']
                
            if metadata.get('genre'):
                classification['primary_genre'] = metadata['genre']
                classification['confidence_scores']['genre'] = 0.85
                classification['sources'].append('metadata_genre')
                
            if metadata.get('comment'):
                # Look for label info in comments
                comment = metadata['comment'].lower()
                labels = self.db.get_all_label_profiles()
                for label in labels:
                    if label['normalized_name'] in comment:
                        classification['label'] = label['name']
                        classification['confidence_scores']['label'] = 0.75
                        classification['sources'].append('metadata_comment')
                        break
                        
        # Fallback to filename analysis
        if not classification['artist'] and filename_analysis['artist']:
            classification['artist'] = filename_analysis['artist']
            classification['confidence_scores']['artist'] = 0.70
            classification['sources'].append('filename_artist')
            
        if not classification['track_name'] and filename_analysis['title']:
            classification['track_name'] = filename_analysis['title']
            
        if filename_analysis['remix']:
            classification['remix_info'] = filename_analysis['remix']
            
        # Genre classification from patterns
        if not classification['primary_genre']:
            # Check folder patterns
            for genre_hint in folder_analysis['genre_hints']:
                patterns = self.db.get_patterns('folder', genre_hint)
                if patterns:
                    best_pattern = max(patterns, key=lambda p: p['confidence'])
                    classification['primary_genre'] = best_pattern['genre']
                    classification['confidence_scores']['genre'] = best_pattern['confidence']
                    classification['sources'].append('folder_pattern')
                    break
                    
        # Artist profile lookup for additional context
        if classification['artist']:
            artist_profile = self.db.get_artist_profile(classification['artist'])
            if artist_profile and artist_profile['confidence_score'] > 0.7:
                if not classification['primary_genre'] and artist_profile['primary_genres']:
                    # Use most likely genre from artist profile
                    genres = json.loads(artist_profile['primary_genres']) if isinstance(artist_profile['primary_genres'], str) else artist_profile['primary_genres']
                    if genres:
                        best_genre = max(genres.keys(), key=lambda g: genres[g])
                        classification['primary_genre'] = best_genre
                        classification['confidence_scores']['genre'] = genres[best_genre] * 0.8  # Slightly lower confidence
                        classification['sources'].append('artist_profile')
                        
        # Calculate overall confidence
        if classification['confidence_scores']:
            classification['overall_confidence'] = sum(classification['confidence_scores'].values()) / len(classification['confidence_scores'])
        else:
            classification['overall_confidence'] = 0.0
            
        return classification
        
    def process_file(self, file_path: str, session_id: int, version: str = 'v1.8') -> Optional[Dict]:
        """Process a single audio file through the full pipeline."""
        try:
            logger.info(f"Processing: {Path(file_path).name}")
            
            # Check if file already processed with current version
            file_hash = self.calculate_file_hash(file_path)
            if not file_hash:
                logger.warning(f"ERROR - Could not calculate hash for: {file_path}")
                return None
                
            existing = self.db.get_track_by_hash_and_version(file_hash, version)
            if existing:
                logger.info(f"SKIPPED - Already processed with {version}: {Path(file_path).name}")
                return existing
                
            # File stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            file_modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Extract metadata
            raw_metadata = self.extract_metadata(file_path)
            
            # Store discovered track
            track_data = {
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'file_modified': file_modified.isoformat(),
                'filename': Path(file_path).name,
                'folder_path': str(Path(file_path).parent),
                'file_extension': Path(file_path).suffix.lower(),
                'raw_metadata': raw_metadata,
                'processing_status': 'discovered',
                'processing_version': version
            }
            
            # SANITIZE METADATA: Remove null bytes that PostgreSQL can't handle
            def sanitize_data(data):
                """Recursively remove null bytes from strings"""
                if isinstance(data, str):
                    return data.replace('\x00', '').replace('\u0000', '')
                elif isinstance(data, dict):
                    return {k: sanitize_data(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [sanitize_data(item) for item in data]
                else:
                    return data
            
            track_data = sanitize_data(track_data)
            
            # Insert into database
            track_id = self.db.create_discovered_track(track_data)
            if not track_id:
                return None
                
            track_data['id'] = track_id
            
            # Analyze filename and folder structure
            filename_analysis = self.analyze_filename(track_data['filename'])
            folder_analysis = self.analyze_folder_structure(track_data['file_path'])
            
            # Store analysis
            analysis_data = {
                'track_id': track_id,
                'filename_artist': filename_analysis.get('artist'),
                'filename_track': filename_analysis.get('title'),
                'filename_remix': filename_analysis.get('remix'),
                'filename_genre_hints': filename_analysis.get('genre_hints', []),
                'folder_genre_hints': folder_analysis.get('genre_hints', []),
                'folder_depth': folder_analysis.get('depth'),
                'folder_structure': folder_analysis.get('structure', []),
                'metadata_artist': raw_metadata.get('artist'),
                'metadata_title': raw_metadata.get('title'),
                'metadata_album': raw_metadata.get('album'),
                'metadata_genre': raw_metadata.get('genre'),
                'metadata_comment': raw_metadata.get('comment'),
                'metadata_year': raw_metadata.get('year'),
                'metadata_bpm': raw_metadata.get('bpm'),
                'metadata_duration': raw_metadata.get('duration')
            }
            
            self.db.create_track_analysis(analysis_data)
            
            # Classify track
            classification = self.classify_track(track_data)
            
            # Store classification
            classification_data = {
                'track_id': track_id,
                'artist': classification.get('artist'),
                'track_name': classification.get('track_name'),
                'remix_info': classification.get('remix_info'),
                'label': classification.get('label'),
                'primary_genre': classification.get('primary_genre'),
                'secondary_genre': classification.get('secondary_genre'),
                'subgenre': classification.get('subgenre'),
                'artist_confidence': classification['confidence_scores'].get('artist', 0.0),
                'genre_confidence': classification['confidence_scores'].get('genre', 0.0),
                'overall_confidence': classification.get('overall_confidence', 0.0),
                'classification_sources': classification.get('sources', []),
                'needs_review': classification.get('overall_confidence', 0.0) < 0.6
            }
            
            self.db.create_track_classification(classification_data)
            
            # Learn patterns from successful classifications
            if classification.get('primary_genre') and classification.get('overall_confidence', 0.0) > 0.7:
                # Learn filename patterns
                if filename_analysis.get('genre_hints'):
                    for hint in filename_analysis['genre_hints']:
                        self.learn_pattern('filename', hint, classification['primary_genre'], 0.8)
                        
                # Learn folder patterns  
                if folder_analysis.get('genre_hints'):
                    for hint in folder_analysis['genre_hints']:
                        self.learn_pattern('folder', hint, classification['primary_genre'], 0.9)
                        
                # Learn metadata patterns
                if raw_metadata.get('genre'):
                    self.learn_pattern('metadata', raw_metadata['genre'], classification['primary_genre'], 0.85)
                    
            logger.info(f"Processed: {Path(file_path).name} -> {classification.get('artist', 'Unknown')} - {classification.get('primary_genre', 'Unknown')}")
            return track_data
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self.db.log_processing_error(session_id, f"Error processing {file_path}: {str(e)}")
            return None
            
    def scan_directory(self, directory: str) -> Dict[str, int]:
        """Scan directory for audio files and process them."""
        logger.info(f"Starting scan of directory: {directory}")
        
        # Create scan session
        session_data = {
            'scan_path': directory,
            'status': 'running'
        }
        session_id = self.db.create_scan_session(session_data)
        
        stats = {
            'files_discovered': 0,
            'files_processed': 0,
            'files_classified': 0,
            'duplicates_found': 0,
            'errors': 0
        }
        
        start_time = time.time()
        
        try:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if Path(file).suffix.lower() in self.audio_extensions:
                        stats['files_discovered'] += 1
                        file_path = os.path.join(root, file)
                        
                        result = self.process_file(file_path, session_id, version='v1.8')
                        if result:
                            stats['files_processed'] += 1
                        else:
                            stats['errors'] += 1
                            
                        # Progress logging every 100 files
                        if stats['files_discovered'] % 100 == 0:
                            logger.info(f"Processed {stats['files_processed']}/{stats['files_discovered']} files")
                            
            # Detect duplicates
            logger.info("Detecting duplicates...")
            duplicates = self.detect_duplicates()
            stats['duplicates_found'] = len(duplicates)
            
            # Update artist profiles
            logger.info("Building artist profiles...")
            self.build_all_artist_profiles()
            
            # Update label profiles
            logger.info("Building label profiles...")
            self.build_all_label_profiles()
            
            end_time = time.time()
            processing_time = int(end_time - start_time)
            
            # Update scan session
            self.db.update_scan_session(session_id, {
                'completed_at': datetime.now().isoformat(),
                'files_discovered': stats['files_discovered'],
                'files_analyzed': stats['files_processed'],
                'files_classified': stats['files_processed'],
                'duplicates_found': stats['duplicates_found'],
                'processing_time_seconds': processing_time,
                'files_per_second': stats['files_processed'] / max(processing_time, 1),
                'status': 'completed'
            })
            
            logger.info(f"Scan completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during directory scan: {e}")
            self.db.update_scan_session(session_id, {
                'status': 'failed',
                'error_message': str(e)
            })
            return stats
            
    def detect_duplicates(self) -> List[Dict]:
        """Detect duplicate files by hash and group them."""
        duplicates = []
        hash_groups = {}
        
        # Group tracks by hash
        all_tracks = self.db.get_all_discovered_tracks()
        for track in all_tracks:
            file_hash = track['file_hash']
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(track)
            
        # Process groups with duplicates
        for file_hash, tracks in hash_groups.items():
            if len(tracks) > 1:
                # Sort by file path to get consistent primary
                tracks.sort(key=lambda t: t['file_path'])
                primary = tracks[0]
                duplicate_ids = [t['id'] for t in tracks[1:]]
                
                total_size = sum(t['file_size'] for t in tracks)
                waste_size = total_size - primary['file_size']
                
                duplicate_data = {
                    'file_hash': file_hash,
                    'primary_track_id': primary['id'],
                    'duplicate_track_ids': duplicate_ids,
                    'duplicate_count': len(tracks) - 1,
                    'total_size_bytes': total_size,
                    'space_waste_bytes': waste_size
                }
                
                self.db.create_duplicate_group(duplicate_data)
                duplicates.append(duplicate_data)
                
        return duplicates
        
    def build_all_artist_profiles(self) -> None:
        """Build intelligence profiles for all artists with 10+ tracks."""
        # Get artist track counts
        artist_tracks = {}
        all_tracks = self.db.get_all_track_analyses()
        
        for track in all_tracks:
            artist = track.get('metadata_artist') or track.get('filename_artist')
            if artist:
                if artist not in artist_tracks:
                    artist_tracks[artist] = []
                artist_tracks[artist].append(track)
                
        # Build profiles for artists with enough tracks
        for artist, tracks in artist_tracks.items():
            if len(tracks) >= 10:
                profile_data = self.build_artist_profile(artist, tracks)
                if profile_data:
                    # Check if profile exists
                    existing = self.db.get_artist_profile(artist)
                    if existing:
                        self.db.update_artist_profile(existing['id'], profile_data)
                    else:
                        self.db.create_artist_profile(profile_data)
                        
    def build_all_label_profiles(self) -> None:
        """Build intelligence profiles for all labels with 20+ releases."""
        # Similar to artist profiles but for labels
        # Implementation would be similar but looking for label info in metadata/comments
        pass
        
    def run_single_scan(self) -> None:
        """Run a single scan of the configured directory."""
        scan_path = self.config.get('scan_path', 'X:\\lightbulb networ IUL Dropbox\\Automation\\MetaCrate\\USERS\\DJUNOHOO\\1-Originals')
        
        if not os.path.exists(scan_path):
            logger.error(f"Scan path does not exist: {scan_path}")
            return
            
        logger.info("=== CULTURAL INTELLIGENCE SCAN STARTING ===")
        stats = self.scan_directory(scan_path)
        logger.info(f"=== SCAN COMPLETED ===")
        logger.info(f"Files discovered: {stats['files_discovered']}")
        logger.info(f"Files processed: {stats['files_processed']}")
        logger.info(f"Duplicates found: {stats['duplicates_found']}")
        logger.info(f"Errors: {stats['errors']}")
        
    def start_scheduled_scanning(self) -> None:
        """Start the scheduled scanning process (every 6 hours)."""
        logger.info("Starting Cultural Intelligence Scanner with 6-hour intervals")
        
        # Schedule scans every 6 hours
        schedule.every(6).hours.do(self.run_single_scan)
        
        # Run initial scan
        self.run_single_scan()
        
        self.running = True
        
        # Main loop
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    def start_service(self) -> None:
        """Start scanner as background service."""
        if self.running:
            logger.warning("Scanner is already running")
            return
            
        logger.info("Starting Cultural Intelligence Scanner service")
        self.scan_thread = threading.Thread(target=self.start_scheduled_scanning, daemon=True)
        self.scan_thread.start()
        
    def stop_service(self) -> None:
        """Stop scanner service."""
        logger.info("Stopping Cultural Intelligence Scanner service")
        self.running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
            
    def get_status(self) -> Dict[str, Any]:
        """Get current scanner status and statistics."""
        return {
            'running': self.running,
            'last_scan': self.db.get_latest_scan_session(),
            'total_tracks': self.db.count_discovered_tracks(),
            'total_duplicates': self.db.count_duplicate_groups(),
            'total_artists': self.db.count_artist_profiles(),
            'total_patterns': self.db.count_learned_patterns()
        }

def main():
    """Main entry point for Cultural Intelligence Scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cultural Intelligence Scanner')
    parser.add_argument('--scan', action='store_true', help='Run single scan')
    parser.add_argument('--service', action='store_true', help='Run as service (6-hour intervals)')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--config', default='taxonomy_config.json', help='Config file path')
    
    args = parser.parse_args()
    
    scanner = CulturalIntelligenceScanner(args.config)
    
    if args.scan:
        scanner.run_single_scan()
    elif args.service:
        try:
            scanner.start_scheduled_scanning()
        except KeyboardInterrupt:
            logger.info("Shutting down scanner...")
            scanner.stop_service()
    elif args.status:
        status = scanner.get_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --scan, --service, or --status")
        
if __name__ == '__main__':
    main()