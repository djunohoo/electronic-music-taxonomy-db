#!/usr/bin/env python3
"""
Cultural Intelligence System v3.2 - Taxonomy Scanner
===================================================

Main scanning and classification engine for electronic music collections.
Processes files, extracts metadata, detects duplicates, and classifies genres.
"""

import os
import json
import hashlib
import time
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import uuid

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    print("⚠️  Installing required package: mutagen")
    os.system("pip install mutagen")
    from mutagen import File as MutagenFile

from taxonomy_v32 import TaxonomyConfig, DatabaseSchema

class MetadataExtractor:
    """Extract comprehensive metadata from audio files"""
    
    def __init__(self):
        self.supported_formats = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'}
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract all available metadata from audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return {"error": "Unsupported format"}
            
            # Extract all tags
            metadata = {}
            
            # Common tags (normalize across formats)
            tag_mapping = {
                'title': ['TIT2', 'TITLE', '\xa9nam'],
                'artist': ['TPE1', 'ARTIST', '\xa9ART'],
                'album': ['TALB', 'ALBUM', '\xa9alb'], 
                'genre': ['TCON', 'GENRE', '\xa9gen'],
                'date': ['TDRC', 'DATE', '\xa9day'],
                'label': ['TPUB', 'ORGANIZATION', '\xa9pub'],
                'bpm': ['TBPM', 'BPM'],
                'key': ['TKEY', 'INITIALKEY'],
                'comment': ['COMM::eng', 'COMMENT', '\xa9cmt'],
                'composer': ['TCOM', 'COMPOSER', '\xa9wrt'],
                'albumartist': ['TPE2', 'ALBUMARTIST', 'aART'],
                'tracknumber': ['TRCK', 'TRACKNUMBER', 'trkn'],
                'discnumber': ['TPOS', 'DISCNUMBER', 'disk'],
                'isrc': ['TSRC', 'ISRC'],
                'catalog': ['TXXX:CATALOG', 'CATALOGNUMBER']
            }
            
            # Extract normalized metadata
            for field, possible_keys in tag_mapping.items():
                for key in possible_keys:
                    if key in audio_file:
                        value = audio_file[key]
                        if isinstance(value, list) and value:
                            metadata[field] = str(value[0])
                        else:
                            metadata[field] = str(value)
                        break
            
            # Extract all raw tags for complete record
            raw_tags = {}
            if hasattr(audio_file, 'tags') and audio_file.tags:
                for key, value in audio_file.tags.items():
                    if isinstance(value, list):
                        raw_tags[str(key)] = [str(v) for v in value]
                    else:
                        raw_tags[str(key)] = str(value)
            
            # Audio properties
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata.update({
                    'duration': getattr(info, 'length', 0),
                    'bitrate': getattr(info, 'bitrate', 0),
                    'sample_rate': getattr(info, 'sample_rate', 0),
                    'channels': getattr(info, 'channels', 0)
                })
            
            return {
                'normalized': metadata,
                'raw_tags': raw_tags,
                'extraction_success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'extraction_success': False
            }

class PatternAnalyzer:
    """Analyze filenames, folders, and metadata for genre classification patterns"""
    
    def __init__(self):
        # Common electronic music genre patterns
        self.genre_patterns = {
            'house': r'(?i)\b(house|deep\s*house|tech\s*house|progressive\s*house|future\s*house|big\s*room)\b',
            'trance': r'(?i)\b(trance|progressive\s*trance|uplifting\s*trance|psytrance|vocal\s*trance)\b',
            'techno': r'(?i)\b(techno|minimal\s*techno|detroit\s*techno|acid\s*techno)\b',
            'dubstep': r'(?i)\b(dubstep|brostep|future\s*bass|trap)\b',
            'dnb': r'(?i)\b(drum\s*and\s*bass|dnb|d&b|jungle|liquid\s*dnb)\b',
            'ambient': r'(?i)\b(ambient|chillout|downtempo|lounge)\b',
            'electro': r'(?i)\b(electro|electro\s*house|fidget\s*house)\b'
        }
        
        self.remix_patterns = {
            'original': r'(?i)\(original\s*mix\)',
            'radio_edit': r'(?i)\(radio\s*edit\)',
            'extended': r'(?i)\(extended\s*mix\)',
            'club': r'(?i)\(club\s*mix\)',
            'dub': r'(?i)\(dub\s*mix\)',
            'remix': r'(?i)\((.+)\s*remix\)',
            'bootleg': r'(?i)\((.+)\s*bootleg\)',
            'edit': r'(?i)\((.+)\s*edit\)'
        }
        
        self.artist_track_pattern = r'^([^-]+)\s*-\s*(.+?)(?:\s*\([^)]+\))?\s*$'
    
    def analyze_filename(self, filename: str) -> Dict:
        """Extract artist, track, remix info from filename"""
        result = {
            'artist': None,
            'track': None,
            'remix_type': None,
            'remix_artist': None,
            'genre_hints': [],
            'confidence': 0.0
        }
        
        # Remove file extension
        name = Path(filename).stem
        
        # Check for genre patterns in filename
        for genre, pattern in self.genre_patterns.items():
            if re.search(pattern, name):
                result['genre_hints'].append(genre)
        
        # Extract remix information
        for remix_type, pattern in self.remix_patterns.items():
            match = re.search(pattern, name)
            if match:
                result['remix_type'] = remix_type
                if remix_type == 'remix' and match.groups():
                    result['remix_artist'] = match.group(1).strip()
                break
        
        # Extract artist and track name
        # Remove remix info for cleaner extraction
        clean_name = re.sub(r'\([^)]+\)', '', name).strip()
        
        match = re.match(self.artist_track_pattern, clean_name)
        if match:
            result['artist'] = match.group(1).strip()
            result['track'] = match.group(2).strip()
            result['confidence'] = 0.8
        else:
            # Fallback: assume entire name is track if no dash found
            result['track'] = clean_name
            result['confidence'] = 0.3
        
        return result
    
    def analyze_folder_path(self, folder_path: str) -> Dict:
        """Extract genre hints from folder structure"""
        result = {
            'genre_hints': [],
            'organizational_hints': [],
            'confidence': 0.0
        }
        
        # Split path into components
        parts = Path(folder_path).parts
        
        # Check each folder level for genre patterns
        for part in parts:
            for genre, pattern in self.genre_patterns.items():
                if re.search(pattern, part):
                    result['genre_hints'].append(genre)
                    result['confidence'] = max(result['confidence'], 0.9)
            
            # Check for organizational patterns
            if re.search(r'(?i)(download|new|incoming|unsorted)', part):
                result['organizational_hints'].append('unorganized')
            elif re.search(r'(?i)(collection|library|music)', part):
                result['organizational_hints'].append('organized')
        
        return result
    
    def analyze_metadata_fields(self, metadata: Dict) -> Dict:
        """Analyze metadata for classification hints"""
        result = {
            'genre_hints': [],
            'artist': None,
            'track': None,
            'label': None,
            'bpm': None,
            'confidence': 0.0
        }
        
        normalized = metadata.get('normalized', {})
        
        # Direct genre field
        if 'genre' in normalized:
            genre_text = normalized['genre'].lower()
            for genre, pattern in self.genre_patterns.items():
                if re.search(pattern, genre_text):
                    result['genre_hints'].append(genre)
                    result['confidence'] = max(result['confidence'], 0.95)
        
        # Comment field analysis
        if 'comment' in normalized:
            comment = normalized['comment'].lower()
            for genre, pattern in self.genre_patterns.items():
                if re.search(pattern, comment):
                    result['genre_hints'].append(genre)
                    result['confidence'] = max(result['confidence'], 0.7)
        
        # Extract other useful fields
        result['artist'] = normalized.get('artist')
        result['track'] = normalized.get('title')
        result['label'] = normalized.get('label')
        
        # BPM analysis for genre hints
        if 'bpm' in normalized:
            try:
                bpm = int(float(normalized['bpm']))
                result['bpm'] = bpm
                
                # BPM-based genre classification
                if 120 <= bpm <= 130:
                    result['genre_hints'].append('house')
                elif 130 <= bpm <= 140:
                    result['genre_hints'].append('trance')
                elif 140 <= bpm <= 150:
                    result['genre_hints'].append('techno')
                elif bpm >= 170:
                    result['genre_hints'].append('dnb')
                
                result['confidence'] = max(result['confidence'], 0.6)
            except (ValueError, TypeError):
                pass
        
        return result

class TaxonomyScanner:
    """Main scanning engine for the Cultural Intelligence System"""
    
    def __init__(self, config: TaxonomyConfig):
        self.config = config
        self.metadata_extractor = MetadataExtractor()
        self.pattern_analyzer = PatternAnalyzer()
        
        # Processing statistics
        self.stats = {
            'run_id': str(uuid.uuid4()),
            'start_time': time.time(),
            'files_scanned': 0,
            'files_processed': 0,
            'errors': 0,
            'duplicates_found': 0,
            'classifications_made': 0
        }
        
        # Duplicate tracking
        self.file_hashes = {}
        self.duplicate_groups = []
        
        # Classification results
        self.classifications = []
        
    def generate_file_hash(self, file_path: str) -> Optional[str]:
        """Generate SHA-256 hash for file (validated FILE_HASH algorithm)"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  Hash generation failed for {file_path}: {e}")
            return None
    
    def scan_directory(self, directory: str) -> Dict:
        """Scan directory and process all audio files"""
        print(f"🔍 Starting Cultural Intelligence System v3.2 scan")
        print(f"📁 Directory: {directory}")
        print(f"🆔 Run ID: {self.stats['run_id']}")
        print()
        
        # Find all audio files
        audio_files = []
        supported_formats = set(self.config.get('scanning.supported_formats'))
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in supported_formats:
                    audio_files.append(os.path.join(root, file))
        
        print(f"📊 Found {len(audio_files)} audio files")
        self.stats['files_scanned'] = len(audio_files)
        
        # Process files in batches
        batch_size = self.config.get('scanning.batch_size', 400)
        
        for i in range(0, len(audio_files), batch_size):
            batch = audio_files[i:i + batch_size]
            self._process_batch(batch, i // batch_size + 1, len(audio_files) // batch_size + 1)
        
        # Analyze duplicates
        self._analyze_duplicates()
        
        # Generate final report
        return self._generate_report()
    
    def _process_batch(self, batch: List[str], batch_num: int, total_batches: int):
        """Process a batch of files"""
        print(f"⚙️  Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
        
        start_time = time.time()
        
        for file_path in batch:
            try:
                self._process_single_file(file_path)
                self.stats['files_processed'] += 1
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                self.stats['errors'] += 1
        
        elapsed = time.time() - start_time
        rate = len(batch) / elapsed if elapsed > 0 else 0
        
        print(f"✅ Batch {batch_num} complete | {rate:.1f} files/sec")
    
    def _process_single_file(self, file_path: str):
        """Process individual audio file"""
        # Generate file hash (duplicate detection)
        file_hash = self.generate_file_hash(file_path)
        if not file_hash:
            return
        
        # Track for duplicate detection
        if file_hash not in self.file_hashes:
            self.file_hashes[file_hash] = []
        self.file_hashes[file_hash].append(file_path)
        
        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata(file_path)
        
        # Analyze patterns
        filename_analysis = self.pattern_analyzer.analyze_filename(Path(file_path).name)
        folder_analysis = self.pattern_analyzer.analyze_folder_path(str(Path(file_path).parent))
        metadata_analysis = self.pattern_analyzer.analyze_metadata_fields(metadata)
        
        # Combine analysis results
        classification = self._combine_analysis_results(
            file_path, file_hash, metadata, 
            filename_analysis, folder_analysis, metadata_analysis
        )
        
        self.classifications.append(classification)
        self.stats['classifications_made'] += 1
    
    def _combine_analysis_results(self, file_path: str, file_hash: str, metadata: Dict, 
                                filename_analysis: Dict, folder_analysis: Dict, 
                                metadata_analysis: Dict) -> Dict:
        """Combine all analysis results into final classification"""
        
        # Collect all genre hints with sources
        genre_hints = []
        
        for hint in filename_analysis.get('genre_hints', []):
            genre_hints.append(('filename', hint, 0.7))
        
        for hint in folder_analysis.get('genre_hints', []):
            genre_hints.append(('folder', hint, 0.9))
            
        for hint in metadata_analysis.get('genre_hints', []):
            genre_hints.append(('metadata', hint, 0.95))
        
        # Determine best genre classification
        if genre_hints:
            # Weight by confidence and count
            genre_scores = defaultdict(float)
            for source, genre, confidence in genre_hints:
                genre_scores[genre] += confidence
            
            best_genre = max(genre_scores.items(), key=lambda x: x[1])
            final_genre = best_genre[0]
            genre_confidence = min(best_genre[1] / len(genre_hints), 1.0)
        else:
            final_genre = 'Electronic'  # Default fallback
            genre_confidence = 0.1
        
        # Extract artist information (prefer metadata > filename)
        artist = (metadata_analysis.get('artist') or 
                 filename_analysis.get('artist') or 
                 'Unknown Artist')
        
        # Extract track information
        track = (metadata_analysis.get('track') or 
                filename_analysis.get('track') or 
                Path(file_path).stem)
        
        # File information
        stat = os.stat(file_path)
        
        classification = {
            # File information
            'file_path': file_path,
            'file_hash': file_hash,
            'filename': Path(file_path).name,
            'folder_path': str(Path(file_path).parent),
            'file_size': stat.st_size,
            'file_modified': datetime.fromtimestamp(stat.st_mtime),
            
            # Extracted information
            'artist': artist,
            'track_name': track,
            'remix_info': filename_analysis.get('remix_type'),
            'label': metadata_analysis.get('label'),
            'bpm': metadata_analysis.get('bpm'),
            
            # Classification results
            'genre': final_genre,
            'genre_confidence': genre_confidence,
            'classification_sources': genre_hints,
            
            # Raw data
            'metadata': metadata,
            'filename_analysis': filename_analysis,
            'folder_analysis': folder_analysis,
            'metadata_analysis': metadata_analysis,
            
            # Processing metadata
            'processed_at': datetime.now(),
            'processing_version': 'v3.2'
        }
        
        return classification
    
    def _analyze_duplicates(self):
        """Analyze file hashes for duplicate detection"""
        print("🔍 Analyzing duplicates...")
        
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                self.duplicate_groups.append({
                    'hash': file_hash,
                    'files': file_paths,
                    'count': len(file_paths)
                })
                self.stats['duplicates_found'] += len(file_paths) - 1
        
        print(f"📊 Found {len(self.duplicate_groups)} duplicate groups")
        print(f"📁 {self.stats['duplicates_found']} duplicate files identified")
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive scan report"""
        elapsed_time = time.time() - self.stats['start_time']
        files_per_second = self.stats['files_processed'] / elapsed_time if elapsed_time > 0 else 0
        
        # Genre distribution
        genre_counts = defaultdict(int)
        for classification in self.classifications:
            genre_counts[classification['genre']] += 1
        
        # Artist counts  
        artist_counts = defaultdict(int)
        for classification in self.classifications:
            artist_counts[classification['artist']] += 1
        
        # Label counts
        label_counts = defaultdict(int)
        for classification in self.classifications:
            if classification['label']:
                label_counts[classification['label']] += 1
        
        report = {
            'scan_info': {
                'run_id': self.stats['run_id'],
                'scan_completed': datetime.now().isoformat(),
                'processing_time_seconds': elapsed_time,
                'files_per_second': files_per_second
            },
            'statistics': self.stats,
            'duplicate_analysis': {
                'duplicate_groups': len(self.duplicate_groups),
                'duplicate_files': self.stats['duplicates_found'],
                'unique_files': self.stats['files_processed'] - self.stats['duplicates_found'],
                'duplication_rate': self.stats['duplicates_found'] / self.stats['files_processed'] if self.stats['files_processed'] > 0 else 0
            },
            'genre_distribution': dict(genre_counts),
            'artist_distribution': dict(sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            'label_distribution': dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            'classifications': self.classifications,
            'duplicate_groups': self.duplicate_groups
        }
        
        return report

def main():
    """Main execution function"""
    print("🎵 CULTURAL INTELLIGENCE SYSTEM v3.2")
    print("=====================================")
    print("Electronic Music Taxonomy Scanner")
    print()
    
    # Load configuration
    config = TaxonomyConfig()
    
    # Get scan target
    scan_path = config.get('paths.current_target')
    print(f"🎯 Target: {scan_path}")
    
    if not os.path.exists(scan_path):
        print(f"❌ Path not found: {scan_path}")
        return
    
    # Initialize scanner
    scanner = TaxonomyScanner(config)
    
    # Run scan
    report = scanner.scan_directory(scan_path)
    
    # Save report
    report_file = f"taxonomy_scan_{report['scan_info']['run_id'][:8]}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ SCAN COMPLETE!")
    print(f"📊 Files processed: {report['statistics']['files_processed']}")
    print(f"📁 Duplicates found: {report['duplicate_analysis']['duplicate_files']}")
    print(f"🎵 Genres identified: {len(report['genre_distribution'])}")
    print(f"🎤 Artists found: {len(report['artist_distribution'])}")
    print(f"📀 Labels identified: {len(report['label_distribution'])}")
    print(f"⚡ Performance: {report['scan_info']['files_per_second']:.1f} files/sec")
    print(f"💾 Report saved: {report_file}")

if __name__ == "__main__":
    main()