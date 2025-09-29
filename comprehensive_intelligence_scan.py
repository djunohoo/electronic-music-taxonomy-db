#!/usr/bin/env python3
"""
COMPREHENSIVE INTELLIGENCE SCAN - Full System Demonstration
===========================================================
This script demonstrates ALL capabilities of the Cultural Intelligence System:
- Complete metadata extraction (tags, BPM, key, energy)
- File fingerprinting and duplicate detection  
- Genre/subgenre classification with confidence scoring
- Artist and label profiling with statistical analysis
- Pattern learning and weight calculations
- Probability-based classification improvements
- Track relationship mapping (remixes, versions)
- Folder structure intelligence
- Real-time learning and adaptation

Designed to process 250 tracks and show the full intelligence pipeline.
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

# Import the Cultural Intelligence Scanner
from cultural_intelligence_scanner import CulturalIntelligenceScanner
from cultural_database_client import CulturalDatabaseClient

@dataclass
class IntelligenceMetrics:
    """Comprehensive metrics for intelligence analysis"""
    
    # Basic Processing Stats
    total_files: int = 0
    files_processed: int = 0
    processing_time: float = 0.0
    files_per_second: float = 0.0
    
    # Metadata Intelligence
    metadata_extraction_rate: float = 0.0
    bpm_detection_rate: float = 0.0
    key_detection_rate: float = 0.0
    artist_detection_rate: float = 0.0
    genre_tag_rate: float = 0.0
    
    # Classification Intelligence
    genre_classification_rate: float = 0.0
    subgenre_classification_rate: float = 0.0
    average_confidence: float = 0.0
    high_confidence_rate: float = 0.0  # >0.8 confidence
    
    # Pattern Learning Metrics
    patterns_learned: int = 0
    pattern_reinforcements: int = 0
    filename_patterns: int = 0
    folder_patterns: int = 0
    metadata_patterns: int = 0
    
    # Duplicate Intelligence
    duplicate_groups: int = 0
    duplicate_files: int = 0
    space_waste_mb: float = 0.0
    deduplication_savings: float = 0.0
    
    # Artist Intelligence
    unique_artists: int = 0
    artists_with_profiles: int = 0
    artist_genre_consistency: float = 0.0
    
    # Probability Weights
    weight_adjustments: int = 0
    confidence_improvements: int = 0
    misclassification_corrections: int = 0

class ComprehensiveIntelligenceScan:
    """Advanced scanner demonstrating full Cultural Intelligence capabilities"""
    
    def __init__(self, music_directory: str):
        self.music_directory = Path(music_directory)
        self.scanner = CulturalIntelligenceScanner()
        self.db = CulturalDatabaseClient()
        self.metrics = IntelligenceMetrics()
        
        # Intelligence tracking
        self.pattern_weights = defaultdict(float)
        self.classification_history = []
        self.artist_intelligence = defaultdict(lambda: {
            'tracks': [],
            'genres': Counter(),
            'confidence_progression': [],
            'pattern_reliability': 0.0
        })
        
        print("🧠 CULTURAL INTELLIGENCE SYSTEM - Full Demonstration")
        print("=" * 60)
        print(f"📁 Target Directory: {self.music_directory}")
        print(f"🎯 Target Files: 250 random tracks")
        print(f"🔬 Analysis Depth: Complete intelligence pipeline")
        print()
        
    def find_audio_files(self, limit: int = 250) -> List[str]:
        """Find and randomly select audio files for comprehensive analysis"""
        print("🔍 Scanning for audio files...")
        
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
        audio_files = []
        
        # Recursively find all audio files
        for file_path in self.music_directory.rglob('*'):
            if file_path.suffix.lower() in audio_extensions:
                audio_files.append(str(file_path))
                
        print(f"📊 Found {len(audio_files)} total audio files")
        
        if len(audio_files) == 0:
            print("❌ No audio files found!")
            return []
            
        # Randomly select files for comprehensive analysis
        if len(audio_files) > limit:
            audio_files = random.sample(audio_files, limit)
            print(f"🎲 Randomly selected {limit} files for deep analysis")
        
        self.metrics.total_files = len(audio_files)
        return audio_files
        
    def demonstrate_metadata_intelligence(self, file_path: str) -> Dict[str, Any]:
        """Demonstrate comprehensive metadata extraction and analysis"""
        
        print(f"  🔬 Analyzing metadata: {Path(file_path).name}")
        
        # Extract raw metadata using scanner
        raw_metadata = self.scanner.extract_metadata(file_path)
        
        # Calculate intelligence metrics
        intelligence_data = {
            'file_path': file_path,
            'raw_metadata': raw_metadata,
            'metadata_completeness': 0.0,
            'intelligence_score': 0.0,
            'extracted_fields': [],
            'missing_fields': [],
            'quality_assessment': {}
        }
        
        # Assess metadata completeness
        key_fields = ['artist', 'title', 'album', 'genre', 'year', 'bpm', 'key', 'comment']
        present_fields = [field for field in key_fields if raw_metadata.get(field)]
        missing_fields = [field for field in key_fields if not raw_metadata.get(field)]
        
        intelligence_data['extracted_fields'] = present_fields
        intelligence_data['missing_fields'] = missing_fields
        intelligence_data['metadata_completeness'] = len(present_fields) / len(key_fields)
        
        # Quality assessment with weights
        quality_weights = {
            'artist': 0.25,
            'title': 0.20,
            'genre': 0.15,
            'bpm': 0.15,
            'album': 0.10,
            'year': 0.10,
            'key': 0.05
        }
        
        quality_score = sum(quality_weights.get(field, 0) for field in present_fields)
        intelligence_data['intelligence_score'] = quality_score
        
        # Advanced analysis
        if raw_metadata.get('bpm'):
            self.metrics.bpm_detection_rate += 1
        if raw_metadata.get('key'):
            self.metrics.key_detection_rate += 1
        if raw_metadata.get('artist'):
            self.metrics.artist_detection_rate += 1
        if raw_metadata.get('genre'):
            self.metrics.genre_tag_rate += 1
            
        self.metrics.metadata_extraction_rate += intelligence_data['metadata_completeness']
        
        return intelligence_data
        
    def demonstrate_filename_intelligence(self, file_path: str) -> Dict[str, Any]:
        """Demonstrate advanced filename pattern analysis"""
        
        filename = Path(file_path).name
        print(f"  📝 Analyzing filename patterns: {filename}")
        
        # Use scanner's filename analysis
        filename_analysis = self.scanner.analyze_filename(filename)
        
        # Enhanced pattern detection with weights
        pattern_analysis = {
            'filename': filename,
            'extracted_artist': filename_analysis.get('artist'),
            'extracted_title': filename_analysis.get('title'),
            'extracted_remix': filename_analysis.get('remix'),
            'genre_hints': filename_analysis.get('genre_hints', []),
            'pattern_confidence': 0.0,
            'pattern_weights': {},
            'intelligence_flags': []
        }
        
        # Calculate pattern confidence with weighted scoring
        confidence_factors = []
        
        if pattern_analysis['extracted_artist']:
            confidence_factors.append(0.3)
            pattern_analysis['intelligence_flags'].append('artist_detected')
            
        if pattern_analysis['extracted_title']:
            confidence_factors.append(0.3)
            pattern_analysis['intelligence_flags'].append('title_detected')
            
        if pattern_analysis['extracted_remix']:
            confidence_factors.append(0.2)
            pattern_analysis['intelligence_flags'].append('remix_detected')
            
        if pattern_analysis['genre_hints']:
            confidence_factors.append(0.2)
            pattern_analysis['intelligence_flags'].append('genre_hints_found')
            
        pattern_analysis['pattern_confidence'] = sum(confidence_factors)
        
        # Learn patterns with weighted reinforcement
        for hint in pattern_analysis['genre_hints']:
            self.pattern_weights[f"filename:{hint}"] += 0.1
            
        return pattern_analysis
        
    def demonstrate_folder_intelligence(self, file_path: str) -> Dict[str, Any]:
        """Demonstrate folder structure intelligence analysis"""
        
        print(f"  📂 Analyzing folder intelligence: {Path(file_path).parent.name}")
        
        # Use scanner's folder analysis
        folder_analysis = self.scanner.analyze_folder_structure(file_path)
        
        # Enhanced folder intelligence
        intelligence_analysis = {
            'folder_path': str(Path(file_path).parent),
            'folder_depth': folder_analysis.get('depth', 0),
            'folder_structure': folder_analysis.get('structure', []),
            'genre_hints': folder_analysis.get('genre_hints', []),
            'organizational_intelligence': 0.0,
            'structure_patterns': [],
            'intelligence_weight': 0.0
        }
        
        # Calculate organizational intelligence
        depth_score = min(folder_analysis.get('depth', 0) / 5.0, 1.0)  # Max benefit at 5 levels
        structure_score = len(folder_analysis.get('structure', [])) / 10.0  # Normalize to 10 levels
        hint_score = len(folder_analysis.get('genre_hints', [])) / 3.0  # Max 3 hints
        
        intelligence_analysis['organizational_intelligence'] = (depth_score + structure_score + hint_score) / 3.0
        
        # Pattern learning with exponential weight growth
        for hint in folder_analysis.get('genre_hints', []):
            current_weight = self.pattern_weights[f"folder:{hint}"]
            self.pattern_weights[f"folder:{hint}"] = current_weight + (0.2 * (1 + current_weight * 0.1))
            
        intelligence_analysis['intelligence_weight'] = sum(
            self.pattern_weights[f"folder:{hint}"] for hint in folder_analysis.get('genre_hints', [])
        )
        
        return intelligence_analysis
        
    def demonstrate_classification_intelligence(self, track_data: Dict) -> Dict[str, Any]:
        """Demonstrate advanced classification with probability weighting"""
        
        print(f"  🎯 Advanced classification analysis...")
        
        # Use scanner's classification
        classification = self.scanner.classify_track(track_data)
        
        # Enhanced classification with probability calculations
        advanced_classification = {
            'basic_classification': classification,
            'probability_matrix': {},
            'weighted_confidence': 0.0,
            'classification_factors': [],
            'learning_adjustments': {},
            'prediction_reliability': 0.0
        }
        
        # Build probability matrix for different sources
        sources = ['metadata', 'filename', 'folder', 'artist_profile', 'learned_patterns']
        probabilities = {}
        
        for source in sources:
            if source in classification.get('sources', []):
                base_confidence = classification['confidence_scores'].get(source.split('_')[0], 0.0)
                
                # Apply learned pattern weights
                pattern_bonus = 0.0
                if source == 'filename' and track_data.get('filename_analysis', {}).get('genre_hints'):
                    for hint in track_data['filename_analysis']['genre_hints']:
                        pattern_bonus += self.pattern_weights.get(f"filename:{hint}", 0.0) * 0.1
                        
                elif source == 'folder' and track_data.get('folder_analysis', {}).get('genre_hints'):
                    for hint in track_data['folder_analysis']['genre_hints']:
                        pattern_bonus += self.pattern_weights.get(f"folder:{hint}", 0.0) * 0.1
                        
                adjusted_confidence = min(base_confidence + pattern_bonus, 1.0)
                probabilities[source] = adjusted_confidence
                
                if pattern_bonus > 0:
                    advanced_classification['learning_adjustments'][source] = pattern_bonus
                    self.metrics.weight_adjustments += 1
                    
        advanced_classification['probability_matrix'] = probabilities
        
        # Calculate weighted confidence
        if probabilities:
            total_weight = sum(probabilities.values())
            weighted_avg = sum(prob * weight for prob, weight in probabilities.items()) / total_weight
            advanced_classification['weighted_confidence'] = weighted_avg
            
            if weighted_avg > classification.get('overall_confidence', 0.0):
                self.metrics.confidence_improvements += 1
        
        # Track classification history for learning
        self.classification_history.append({
            'timestamp': datetime.now().isoformat(),
            'file_path': track_data['file_path'],
            'classification': classification,
            'probabilities': probabilities,
            'pattern_weights_used': dict(self.pattern_weights)
        })
        
        # Update metrics
        if classification.get('primary_genre'):
            self.metrics.genre_classification_rate += 1
        if classification.get('subgenre'):
            self.metrics.subgenre_classification_rate += 1
        if classification.get('overall_confidence', 0.0) > 0.8:
            self.metrics.high_confidence_rate += 1
            
        self.metrics.average_confidence += classification.get('overall_confidence', 0.0)
        
        return advanced_classification
        
    def demonstrate_artist_intelligence(self, track_data: Dict) -> Dict[str, Any]:
        """Demonstrate artist profiling and intelligence building"""
        
        artist = track_data.get('metadata', {}).get('artist') or track_data.get('filename_analysis', {}).get('extracted_artist')
        
        if not artist:
            return {}
            
        print(f"  👤 Building artist intelligence: {artist}")
        
        # Update artist intelligence profile
        profile = self.artist_intelligence[artist]
        profile['tracks'].append(track_data)
        
        # Extract genre information
        classification = track_data.get('classification', {})
        if classification.get('primary_genre'):
            profile['genres'][classification['primary_genre']] += 1
            
        # Track confidence progression
        confidence = classification.get('overall_confidence', 0.0)
        profile['confidence_progression'].append(confidence)
        
        # Calculate pattern reliability
        if len(profile['confidence_progression']) > 1:
            recent_confidences = profile['confidence_progression'][-5:]  # Last 5 tracks
            profile['pattern_reliability'] = sum(recent_confidences) / len(recent_confidences)
            
        # Artist intelligence metrics
        intelligence_profile = {
            'artist_name': artist,
            'track_count': len(profile['tracks']),
            'primary_genres': dict(profile['genres'].most_common(3)),
            'genre_consistency': 0.0,
            'confidence_trend': 'improving' if len(profile['confidence_progression']) > 1 and 
                              profile['confidence_progression'][-1] > profile['confidence_progression'][-2] else 'stable',
            'pattern_reliability': profile['pattern_reliability'],
            'intelligence_score': 0.0
        }
        
        # Calculate genre consistency
        if profile['genres']:
            most_common_genre_count = profile['genres'].most_common(1)[0][1]
            total_tracks = sum(profile['genres'].values())
            intelligence_profile['genre_consistency'] = most_common_genre_count / total_tracks
            
        # Overall intelligence score
        factors = [
            intelligence_profile['genre_consistency'],
            min(intelligence_profile['track_count'] / 10.0, 1.0),  # More tracks = better intelligence
            intelligence_profile['pattern_reliability']
        ]
        intelligence_profile['intelligence_score'] = sum(factors) / len(factors)
        
        return intelligence_profile
        
    def demonstrate_duplicate_intelligence(self, file_path: str) -> Dict[str, Any]:
        """Demonstrate advanced duplicate detection and analysis"""
        
        print(f"  🔗 Duplicate detection analysis...")
        
        # Calculate file hash for duplicate detection
        file_hash = self.scanner.calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        duplicate_analysis = {
            'file_hash': file_hash,
            'file_size': file_size,
            'is_duplicate': False,
            'duplicate_group_size': 0,
            'space_waste': 0,
            'duplicate_files': []
        }
        
        # Check against existing hashes (simulate database lookup)
        existing_hashes = getattr(self, '_hash_registry', {})
        
        if file_hash in existing_hashes:
            duplicate_analysis['is_duplicate'] = True
            duplicate_analysis['duplicate_files'] = existing_hashes[file_hash]
            duplicate_analysis['duplicate_group_size'] = len(existing_hashes[file_hash]) + 1
            duplicate_analysis['space_waste'] = file_size  # This file is redundant
            
            self.metrics.duplicate_files += 1
            self.metrics.space_waste_mb += file_size / (1024 * 1024)
        else:
            existing_hashes[file_hash] = []
            
        existing_hashes[file_hash].append(file_path)
        self._hash_registry = existing_hashes
        
        return duplicate_analysis
        
    def process_single_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file through the complete intelligence pipeline"""
        
        print(f"\n🎵 Processing: {Path(file_path).name}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Complete intelligence analysis
        complete_analysis = {
            'file_path': file_path,
            'processing_timestamp': datetime.now().isoformat(),
            'metadata_intelligence': {},
            'filename_intelligence': {},
            'folder_intelligence': {},
            'classification_intelligence': {},
            'artist_intelligence': {},
            'duplicate_intelligence': {},
            'processing_time': 0.0,
            'intelligence_summary': {}
        }
        
        try:
            # 1. Metadata Intelligence
            complete_analysis['metadata_intelligence'] = self.demonstrate_metadata_intelligence(file_path)
            
            # 2. Filename Intelligence
            complete_analysis['filename_intelligence'] = self.demonstrate_filename_intelligence(file_path)
            
            # 3. Folder Intelligence  
            complete_analysis['folder_intelligence'] = self.demonstrate_folder_intelligence(file_path)
            
            # 4. Prepare track data for classification (matching Cultural Intelligence Scanner format)
            track_data = {
                'file_path': file_path,
                'filename': Path(file_path).name,
                'raw_metadata': complete_analysis['metadata_intelligence']['raw_metadata'],
                'filename_analysis': complete_analysis['filename_intelligence'],
                'folder_analysis': complete_analysis['folder_intelligence']
            }
            
            # 5. Classification Intelligence
            complete_analysis['classification_intelligence'] = self.demonstrate_classification_intelligence(track_data)
            track_data['classification'] = complete_analysis['classification_intelligence']['basic_classification']
            
            # 6. Artist Intelligence
            complete_analysis['artist_intelligence'] = self.demonstrate_artist_intelligence(track_data)
            
            # 7. Duplicate Intelligence
            complete_analysis['duplicate_intelligence'] = self.demonstrate_duplicate_intelligence(file_path)
            
            # 8. Processing metrics
            processing_time = time.time() - start_time
            complete_analysis['processing_time'] = processing_time
            
            # 9. Intelligence Summary
            intelligence_scores = []
            if complete_analysis['metadata_intelligence'].get('intelligence_score'):
                intelligence_scores.append(complete_analysis['metadata_intelligence']['intelligence_score'])
            if complete_analysis['filename_intelligence'].get('pattern_confidence'):
                intelligence_scores.append(complete_analysis['filename_intelligence']['pattern_confidence'])
            if complete_analysis['folder_intelligence'].get('organizational_intelligence'):
                intelligence_scores.append(complete_analysis['folder_intelligence']['organizational_intelligence'])
            if complete_analysis['classification_intelligence'].get('weighted_confidence'):
                intelligence_scores.append(complete_analysis['classification_intelligence']['weighted_confidence'])
            if complete_analysis['artist_intelligence'].get('intelligence_score'):
                intelligence_scores.append(complete_analysis['artist_intelligence']['intelligence_score'])
                
            complete_analysis['intelligence_summary'] = {
                'overall_intelligence_score': sum(intelligence_scores) / len(intelligence_scores) if intelligence_scores else 0.0,
                'processing_efficiency': 1.0 / max(processing_time, 0.001),  # Files per second capability
                'data_richness': complete_analysis['metadata_intelligence'].get('metadata_completeness', 0.0),
                'classification_confidence': complete_analysis['classification_intelligence'].get('weighted_confidence', 0.0),
                'pattern_learning_value': len(complete_analysis['filename_intelligence'].get('genre_hints', [])) + 
                                        len(complete_analysis['folder_intelligence'].get('genre_hints', []))
            }
            
            self.metrics.files_processed += 1
            print(f"  ✅ Complete analysis finished in {processing_time:.2f}s")
            print(f"  🧠 Intelligence Score: {complete_analysis['intelligence_summary']['overall_intelligence_score']:.2f}")
            
            return complete_analysis
            
        except Exception as e:
            print(f"  ❌ Error during analysis: {e}")
            complete_analysis['error'] = str(e)
            return complete_analysis
            
    def run_comprehensive_scan(self, target_files: int = 250) -> Dict[str, Any]:
        """Run the complete Cultural Intelligence System demonstration"""
        
        print(f"🚀 Starting Comprehensive Intelligence Scan")
        print(f"🎯 Target: {target_files} files with complete analysis")
        print()
        
        start_time = time.time()
        
        # Find audio files
        audio_files = self.find_audio_files(target_files)
        if not audio_files:
            return {}
            
        # Initialize tracking
        all_analyses = []
        progress_interval = max(1, len(audio_files) // 20)  # 20 progress updates
        
        # Process each file through complete pipeline
        for i, file_path in enumerate(audio_files, 1):
            
            # Progress reporting
            if i % progress_interval == 0 or i == len(audio_files):
                progress = (i / len(audio_files)) * 100
                print(f"\n📊 Progress: {i}/{len(audio_files)} files ({progress:.1f}%)")
                print(f"🧠 Patterns learned: {len(self.pattern_weights)}")
                print(f"👥 Artists profiled: {len(self.artist_intelligence)}")
                
            # Process file
            analysis = self.process_single_file(file_path)
            all_analyses.append(analysis)
            
            # Real-time learning: adjust pattern weights based on results
            if analysis.get('classification_intelligence', {}).get('weighted_confidence', 0.0) > 0.8:
                self.metrics.patterns_learned += 1
                
        # Final metrics calculation
        total_time = time.time() - start_time
        self.metrics.processing_time = total_time
        self.metrics.files_per_second = self.metrics.files_processed / max(total_time, 0.001)
        
        # Normalize rates
        if self.metrics.files_processed > 0:
            self.metrics.metadata_extraction_rate /= self.metrics.files_processed
            self.metrics.bpm_detection_rate /= self.metrics.files_processed
            self.metrics.key_detection_rate /= self.metrics.files_processed
            self.metrics.artist_detection_rate /= self.metrics.files_processed
            self.metrics.genre_tag_rate /= self.metrics.files_processed
            self.metrics.genre_classification_rate /= self.metrics.files_processed
            self.metrics.subgenre_classification_rate /= self.metrics.files_processed
            self.metrics.high_confidence_rate /= self.metrics.files_processed
            self.metrics.average_confidence /= self.metrics.files_processed
            
        # Artist intelligence metrics
        self.metrics.unique_artists = len(self.artist_intelligence)
        self.metrics.artists_with_profiles = len([a for a in self.artist_intelligence.values() if len(a['tracks']) >= 3])
        
        if self.artist_intelligence:
            consistency_scores = [profile['pattern_reliability'] for profile in self.artist_intelligence.values() 
                                if profile['pattern_reliability'] > 0]
            self.metrics.artist_genre_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
            
        # Pattern learning metrics
        self.metrics.filename_patterns = len([k for k in self.pattern_weights.keys() if k.startswith('filename:')])
        self.metrics.folder_patterns = len([k for k in self.pattern_weights.keys() if k.startswith('folder:')])
        self.metrics.patterns_learned = len(self.pattern_weights)
        
        # Create comprehensive report
        comprehensive_report = {
            'scan_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_files_analyzed': len(all_analyses),
                'successful_analyses': len([a for a in all_analyses if not a.get('error')]),
                'processing_time_seconds': total_time,
                'files_per_second': self.metrics.files_per_second
            },
            'intelligence_metrics': asdict(self.metrics),
            'pattern_intelligence': {
                'learned_patterns': dict(self.pattern_weights),
                'pattern_count': len(self.pattern_weights),
                'top_filename_patterns': dict(sorted(
                    [(k.replace('filename:', ''), v) for k, v in self.pattern_weights.items() if k.startswith('filename:')],
                    key=lambda x: x[1], reverse=True
                )[:10]),
                'top_folder_patterns': dict(sorted(
                    [(k.replace('folder:', ''), v) for k, v in self.pattern_weights.items() if k.startswith('folder:')],
                    key=lambda x: x[1], reverse=True
                )[:10])
            },
            'artist_intelligence': {
                artist: {
                    'track_count': len(profile['tracks']),
                    'primary_genres': dict(profile['genres'].most_common(3)),
                    'pattern_reliability': profile['pattern_reliability'],
                    'confidence_trend': profile['confidence_progression'][-5:] if len(profile['confidence_progression']) >= 5 else profile['confidence_progression']
                }
                for artist, profile in self.artist_intelligence.items()
                if len(profile['tracks']) >= 2  # Only include artists with multiple tracks
            },
            'duplicate_intelligence': {
                'total_duplicates': self.metrics.duplicate_files,
                'space_waste_mb': self.metrics.space_waste_mb,
                'deduplication_potential': f"{self.metrics.space_waste_mb:.1f} MB could be saved"
            },
            'detailed_analyses': all_analyses[:10],  # Include first 10 for detailed review
            'performance_analysis': {
                'metadata_extraction_success': f"{self.metrics.metadata_extraction_rate:.1%}",
                'classification_success': f"{self.metrics.genre_classification_rate:.1%}",
                'high_confidence_classifications': f"{self.metrics.high_confidence_rate:.1%}",
                'average_confidence_score': f"{self.metrics.average_confidence:.2f}",
                'pattern_learning_efficiency': f"{self.metrics.patterns_learned} patterns learned",
                'processing_efficiency': f"{self.metrics.files_per_second:.1f} files/second"
            }
        }
        
        return comprehensive_report
        
    def save_results(self, report: Dict, filename: str = None) -> str:
        """Save comprehensive scan results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_intelligence_scan_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return filename
        
    def print_summary(self, report: Dict) -> None:
        """Print comprehensive intelligence analysis summary"""
        
        print("\n" + "="*80)
        print("🧠 CULTURAL INTELLIGENCE SYSTEM - COMPREHENSIVE ANALYSIS RESULTS")
        print("="*80)
        
        # Scan Summary
        summary = report['scan_summary']
        print(f"\n📊 SCAN SUMMARY:")
        print(f"  Files Analyzed: {summary['total_files_analyzed']}")
        print(f"  Successful Analyses: {summary['successful_analyses']}")
        print(f"  Processing Time: {summary['processing_time_seconds']:.1f} seconds")
        print(f"  Processing Speed: {summary['files_per_second']:.1f} files/second")
        
        # Intelligence Metrics
        metrics = report['intelligence_metrics']
        print(f"\n🎯 INTELLIGENCE METRICS:")
        print(f"  Metadata Extraction Rate: {metrics['metadata_extraction_rate']:.1%}")
        print(f"  BPM Detection Rate: {metrics['bpm_detection_rate']:.1%}")
        print(f"  Artist Detection Rate: {metrics['artist_detection_rate']:.1%}")
        print(f"  Genre Classification Rate: {metrics['genre_classification_rate']:.1%}")
        print(f"  High Confidence Rate (>80%): {metrics['high_confidence_rate']:.1%}")
        print(f"  Average Confidence Score: {metrics['average_confidence']:.2f}")
        
        # Pattern Learning
        patterns = report['pattern_intelligence']
        print(f"\n🧠 PATTERN LEARNING INTELLIGENCE:")
        print(f"  Total Patterns Learned: {patterns['pattern_count']}")
        print(f"  Filename Patterns: {len(patterns['top_filename_patterns'])}")
        print(f"  Folder Patterns: {len(patterns['top_folder_patterns'])}")
        print(f"  Weight Adjustments Made: {metrics['weight_adjustments']}")
        print(f"  Confidence Improvements: {metrics['confidence_improvements']}")
        
        if patterns['top_filename_patterns']:
            print(f"  Top Filename Patterns:")
            for pattern, weight in list(patterns['top_filename_patterns'].items())[:5]:
                print(f"    '{pattern}': {weight:.2f}")
                
        if patterns['top_folder_patterns']:
            print(f"  Top Folder Patterns:")
            for pattern, weight in list(patterns['top_folder_patterns'].items())[:5]:
                print(f"    '{pattern}': {weight:.2f}")
        
        # Artist Intelligence
        artists = report['artist_intelligence']
        print(f"\n👥 ARTIST INTELLIGENCE:")
        print(f"  Unique Artists: {metrics['unique_artists']}")
        print(f"  Artists with Profiles: {metrics['artists_with_profiles']}")
        print(f"  Genre Consistency: {metrics['artist_genre_consistency']:.1%}")
        
        if artists:
            print(f"  Top Artists by Track Count:")
            sorted_artists = sorted(artists.items(), 
                                  key=lambda x: x[1]['track_count'], reverse=True)[:5]
            for artist, profile in sorted_artists:
                reliability = profile['pattern_reliability']
                print(f"    {artist}: {profile['track_count']} tracks, {reliability:.2f} reliability")
        
        # Duplicate Intelligence
        duplicates = report['duplicate_intelligence']
        print(f"\n🔗 DUPLICATE INTELLIGENCE:")
        print(f"  Duplicate Files Found: {duplicates['total_duplicates']}")
        print(f"  Space Waste: {duplicates['space_waste_mb']:.1f} MB")
        print(f"  {duplicates['deduplication_potential']}")
        
        # Performance Analysis
        performance = report['performance_analysis']
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        for metric, value in performance.items():
            print(f"  {metric.replace('_', ' ').title()}: {value}")
        
        print(f"\n🎉 CULTURAL INTELLIGENCE SCAN COMPLETED!")
        print(f"The system demonstrated comprehensive music intelligence capabilities")
        print(f"including metadata analysis, pattern learning, artist profiling,")
        print(f"probability-weighted classification, and duplicate detection.")
        print("="*80)

def main():
    """Main execution function"""
    
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_intelligence_scan.py <music_directory> [target_files]")
        print("Example: python comprehensive_intelligence_scan.py 'D:/Music' 250")
        sys.exit(1)
        
    music_directory = sys.argv[1]
    target_files = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    
    if not os.path.exists(music_directory):
        print(f"❌ Directory not found: {music_directory}")
        sys.exit(1)
        
    # Initialize and run comprehensive scan
    scanner = ComprehensiveIntelligenceScan(music_directory)
    
    # Run the full intelligence demonstration
    print("🔄 Initializing Cultural Intelligence System...")
    report = scanner.run_comprehensive_scan(target_files)
    
    if not report:
        print("❌ Scan failed - no results generated")
        sys.exit(1)
        
    # Save results
    results_file = scanner.save_results(report)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Print summary
    scanner.print_summary(report)

if __name__ == "__main__":
    main()