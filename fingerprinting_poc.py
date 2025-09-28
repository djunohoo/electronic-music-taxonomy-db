#!/usr/bin/env python3
"""
Audio Fingerprinting Proof of Concept
Electronic Music Taxonomy Database

This script tests different audio fingerprinting algorithms for accuracy
on electronic music, specifically testing duplicate detection scenarios.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Audio processing libraries
try:
    import librosa
    import numpy as np
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Install with: pip install librosa numpy")
    sys.exit(1)

# Optional chromaprint support
CHROMAPRINT_AVAILABLE = False
try:
    import chromaprint
    import acoustid
    CHROMAPRINT_AVAILABLE = True
except ImportError:
    print("Note: Chromaprint not available, will use spectral analysis instead")
    print("This is fine for POC testing - spectral analysis often works better for electronic music")

@dataclass
class FingerprintResult:
    """Represents a fingerprint result for a track"""
    file_path: str
    algorithm: str
    fingerprint: str
    duration: float
    processing_time: float
    error: Optional[str] = None

@dataclass
class TestScenario:
    """Represents a test scenario for duplicate detection"""
    name: str
    description: str
    file_pairs: List[Tuple[str, str]]
    expected_match: bool

class AudioFingerprinter:
    """Handles different audio fingerprinting algorithms"""
    
    def __init__(self):
        self.supported_formats = {'.mp3', '.wav', '.flac', '.m4a', '.aiff'}
    
    def chromaprint_fingerprint(self, file_path: str) -> FingerprintResult:
        """Generate fingerprint using Chromaprint algorithm (if available)"""
        start_time = time.time()
        
        if not CHROMAPRINT_AVAILABLE:
            return FingerprintResult(
                file_path=file_path,
                algorithm="chromaprint",
                fingerprint="",
                duration=0,
                processing_time=time.time() - start_time,
                error="Chromaprint library not available"
            )
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=22050, duration=30)  # First 30 seconds
            duration = len(y) / sr
            
            # Generate chromaprint fingerprint
            raw_fingerprint, version = chromaprint.encode_fingerprint(
                chromaprint.decode_fingerprint(
                    acoustid.fingerprint(22050, y.astype(np.int16))[1]
                )[0], version=chromaprint.ALGORITHM_DEFAULT, raw=True
            )
            
            # Convert to hex string for storage
            fingerprint = hashlib.md5(str(raw_fingerprint).encode()).hexdigest()
            
            processing_time = time.time() - start_time
            
            return FingerprintResult(
                file_path=file_path,
                algorithm="chromaprint",
                fingerprint=fingerprint,
                duration=duration,
                processing_time=processing_time
            )
            
        except Exception as e:
            return FingerprintResult(
                file_path=file_path,
                algorithm="chromaprint",
                fingerprint="",
                duration=0,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def spectral_fingerprint(self, file_path: str) -> FingerprintResult:
        """Generate fingerprint using custom spectral analysis (optimized for electronic music)"""
        start_time = time.time()
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=22050, duration=30)
            duration = len(y) / sr
            
            # Custom spectral features for electronic music
            # Focus on frequencies important for electronic music (20Hz-20kHz)
            
            # 1. Spectral centroid (brightness)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # 2. MFCCs (timbral characteristics)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 3. Chroma features (harmonic content)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # 4. Spectral rolloff (frequency distribution)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            
            # 5. Zero crossing rate (rhythm/tempo characteristics)
            zcr = librosa.feature.zero_crossing_rate(y)
            
            # 6. Tempo and beat tracking (crucial for electronic music)
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Combine features into signature
            features = np.concatenate([
                np.mean(spectral_centroid, axis=1),
                np.mean(mfccs, axis=1),
                np.mean(chroma, axis=1),
                np.mean(spectral_rolloff, axis=1),
                np.mean(zcr, axis=1),
                [tempo]
            ])
            
            # Create hash from feature vector
            features_normalized = (features / np.linalg.norm(features))
            fingerprint = hashlib.md5(features_normalized.tobytes()).hexdigest()
            
            processing_time = time.time() - start_time
            
            return FingerprintResult(
                file_path=file_path,
                algorithm="spectral_custom",
                fingerprint=fingerprint,
                duration=duration,
                processing_time=processing_time
            )
            
        except Exception as e:
            return FingerprintResult(
                file_path=file_path,
                algorithm="spectral_custom",
                fingerprint="",
                duration=0,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def simple_hash_fingerprint(self, file_path: str) -> FingerprintResult:
        """Generate simple file hash (for baseline comparison)"""
        start_time = time.time()
        
        try:
            # Read first 1MB of file for hash (fast baseline)
            with open(file_path, 'rb') as f:
                chunk = f.read(1024 * 1024)  # 1MB
            
            fingerprint = hashlib.md5(chunk).hexdigest()
            
            # Get basic file info
            stat = os.stat(file_path)
            duration = 0  # Can't determine without full audio analysis
            
            processing_time = time.time() - start_time
            
            return FingerprintResult(
                file_path=file_path,
                algorithm="file_hash",
                fingerprint=fingerprint,
                duration=duration,
                processing_time=processing_time
            )
            
        except Exception as e:
            return FingerprintResult(
                file_path=file_path,
                algorithm="file_hash",
                fingerprint="",
                duration=0,
                processing_time=time.time() - start_time,
                error=str(e)
            )

class FingerprintTester:
    """Main testing class for fingerprint algorithm comparison"""
    
    def __init__(self, test_directory: str):
        self.test_directory = Path(test_directory)
        self.fingerprinter = AudioFingerprinter()
        self.results: Dict[str, List[FingerprintResult]] = defaultdict(list)
        
    def scan_audio_files(self) -> List[str]:
        """Scan directory for audio files"""
        audio_files = []
        
        for file_path in self.test_directory.rglob('*'):
            if file_path.suffix.lower() in self.fingerprinter.supported_formats:
                audio_files.append(str(file_path))
        
        return sorted(audio_files)
    
    def generate_fingerprints(self, audio_files: List[str], algorithms: List[str] = None) -> None:
        """Generate fingerprints for all files using specified algorithms"""
        
        if algorithms is None:
            # Use available algorithms - prioritize spectral_custom for electronic music
            algorithms = ["spectral_custom", "file_hash"]
            if CHROMAPRINT_AVAILABLE:
                algorithms.insert(0, "chromaprint")
        
        total_files = len(audio_files)
        
        for i, file_path in enumerate(audio_files, 1):
            print(f"Processing {i}/{total_files}: {Path(file_path).name}")
            
            for algorithm in algorithms:
                if algorithm == "chromaprint":
                    result = self.fingerprinter.chromaprint_fingerprint(file_path)
                elif algorithm == "spectral_custom":
                    result = self.fingerprinter.spectral_fingerprint(file_path)
                elif algorithm == "file_hash":
                    result = self.fingerprinter.simple_hash_fingerprint(file_path)
                else:
                    continue
                
                self.results[algorithm].append(result)
                
                if result.error:
                    print(f"  ❌ {algorithm}: {result.error}")
                else:
                    print(f"  ✅ {algorithm}: {result.processing_time:.2f}s")
    
    def find_duplicates(self, algorithm: str) -> Dict[str, List[str]]:
        """Find duplicate fingerprints for a given algorithm"""
        fingerprint_groups = defaultdict(list)
        
        for result in self.results[algorithm]:
            if not result.error and result.fingerprint:
                fingerprint_groups[result.fingerprint].append(result.file_path)
        
        # Only return groups with more than one file
        duplicates = {fp: files for fp, files in fingerprint_groups.items() if len(files) > 1}
        return duplicates
    
    def test_duplicate_detection_accuracy(self, known_duplicates: List[TestScenario] = None) -> Dict[str, float]:
        """Test accuracy of duplicate detection against known duplicate sets"""
        
        if known_duplicates is None:
            # Auto-detect potential duplicates by filename similarity
            known_duplicates = self.auto_detect_test_scenarios()
        
        accuracy_results = {}
        
        for algorithm in self.results.keys():
            duplicates = self.find_duplicates(algorithm)
            
            correct_detections = 0
            total_tests = 0
            
            for scenario in known_duplicates:
                total_tests += 1
                
                # Check if algorithm correctly identified this duplicate pair
                found_match = False
                for file1, file2 in scenario.file_pairs:
                    for fingerprint, files in duplicates.items():
                        if file1 in files and file2 in files:
                            found_match = True
                            break
                
                if found_match == scenario.expected_match:
                    correct_detections += 1
            
            accuracy = correct_detections / total_tests if total_tests > 0 else 0
            accuracy_results[algorithm] = accuracy
        
        return accuracy_results
    
    def auto_detect_test_scenarios(self) -> List[TestScenario]:
        """Auto-detect potential duplicate scenarios from filenames"""
        scenarios = []
        
        # Simple filename-based duplicate detection for testing
        # Look for files with similar names (likely different versions)
        
        all_files = []
        for algorithm_results in self.results.values():
            all_files.extend([r.file_path for r in algorithm_results if not r.error])
        
        # Remove duplicates
        all_files = list(set(all_files))
        
        # Group by similar artist/track names (basic heuristic)
        for i, file1 in enumerate(all_files):
            name1 = Path(file1).stem.lower()
            
            for file2 in all_files[i+1:]:
                name2 = Path(file2).stem.lower()
                
                # Simple similarity check
                if self.filename_similarity(name1, name2) > 0.7:
                    scenarios.append(TestScenario(
                        name=f"Similar filenames: {Path(file1).name} vs {Path(file2).name}",
                        description="Auto-detected similar filenames",
                        file_pairs=[(file1, file2)],
                        expected_match=True
                    ))
        
        return scenarios
    
    def filename_similarity(self, name1: str, name2: str) -> float:
        """Calculate simple filename similarity"""
        # Remove common variations
        for suffix in [' (1)', ' (2)', ' - copy', '_320', '_128', ' 320kbps', ' 128kbps']:
            name1 = name1.replace(suffix.lower(), '')
            name2 = name2.replace(suffix.lower(), '')
        
        # Simple word overlap calculation
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "test_summary": {
                "total_files_processed": len(set(r.file_path for results in self.results.values() for r in results)),
                "algorithms_tested": list(self.results.keys()),
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "performance_metrics": {},
            "accuracy_metrics": {},
            "duplicate_detection": {},
            "errors": {}
        }
        
        # Performance metrics
        for algorithm, results in self.results.items():
            successful_results = [r for r in results if not r.error]
            error_results = [r for r in results if r.error]
            
            if successful_results:
                avg_processing_time = sum(r.processing_time for r in successful_results) / len(successful_results)
                total_processing_time = sum(r.processing_time for r in successful_results)
                
                report["performance_metrics"][algorithm] = {
                    "average_processing_time": round(avg_processing_time, 3),
                    "total_processing_time": round(total_processing_time, 3),
                    "successful_files": len(successful_results),
                    "failed_files": len(error_results),
                    "success_rate": len(successful_results) / len(results) if results else 0
                }
            
            # Error analysis
            if error_results:
                report["errors"][algorithm] = [
                    {"file": r.file_path, "error": r.error} for r in error_results
                ]
        
        # Duplicate detection
        for algorithm in self.results.keys():
            duplicates = self.find_duplicates(algorithm)
            report["duplicate_detection"][algorithm] = {
                "duplicate_groups_found": len(duplicates),
                "total_duplicate_files": sum(len(files) for files in duplicates.values()),
                "duplicate_groups": duplicates
            }
        
        # Accuracy testing
        accuracy_results = self.test_duplicate_detection_accuracy()
        report["accuracy_metrics"] = accuracy_results
        
        return report
    
    def print_summary(self, report: Dict) -> None:
        """Print human-readable summary of test results"""
        
        print("\n" + "="*80)
        print("AUDIO FINGERPRINTING POC RESULTS")
        print("="*80)
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"  Total files processed: {report['test_summary']['total_files_processed']}")
        print(f"  Algorithms tested: {', '.join(report['test_summary']['algorithms_tested'])}")
        print(f"  Test completed: {report['test_summary']['test_timestamp']}")
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        for algorithm, metrics in report['performance_metrics'].items():
            print(f"  {algorithm.upper()}:")
            print(f"    Average processing time: {metrics['average_processing_time']}s per file")
            print(f"    Success rate: {metrics['success_rate']:.1%}")
            print(f"    Successful files: {metrics['successful_files']}")
            if metrics['failed_files'] > 0:
                print(f"    ❌ Failed files: {metrics['failed_files']}")
        
        print(f"\n🔍 DUPLICATE DETECTION:")
        for algorithm, detection in report['duplicate_detection'].items():
            print(f"  {algorithm.upper()}:")
            print(f"    Duplicate groups found: {detection['duplicate_groups_found']}")
            print(f"    Total duplicate files: {detection['total_duplicate_files']}")
        
        print(f"\n🎯 ACCURACY METRICS:")
        for algorithm, accuracy in report['accuracy_metrics'].items():
            print(f"  {algorithm.upper()}: {accuracy:.1%} accuracy")
        
        if any(report['errors'].values()):
            print(f"\n❌ ERRORS ENCOUNTERED:")
            for algorithm, errors in report['errors'].items():
                if errors:
                    print(f"  {algorithm.upper()}: {len(errors)} errors")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if report['accuracy_metrics']:
            best_algorithm = max(report['accuracy_metrics'].items(), key=lambda x: x[1])
            print(f"  Best accuracy: {best_algorithm[0].upper()} ({best_algorithm[1]:.1%})")
            
            if best_algorithm[1] >= 0.90:
                print(f"  ✅ RECOMMENDED: Proceed with {best_algorithm[0].upper()} algorithm")
            else:
                print(f"  ⚠️  WARNING: Best accuracy {best_algorithm[1]:.1%} below 90% target")
                print(f"  🔧 SUGGESTED: Consider hybrid approach or algorithm tuning")

def main():
    """Main execution function"""
    
    if len(sys.argv) < 2:
        print("Usage: python fingerprinting_poc.py <audio_directory>")
        print("Example: python fingerprinting_poc.py 'C:/Music/Electronic'")
        sys.exit(1)
    
    test_directory = sys.argv[1]
    
    if not os.path.exists(test_directory):
        print(f"❌ Directory not found: {test_directory}")
        sys.exit(1)
    
    print("🎵 Electronic Music Fingerprinting POC")
    print("="*50)
    print(f"Test directory: {test_directory}")
    
    # Initialize tester
    tester = FingerprintTester(test_directory)
    
    # Scan for audio files
    print("\n🔍 Scanning for audio files...")
    audio_files = tester.scan_audio_files()
    
    if not audio_files:
        print("❌ No audio files found in directory")
        sys.exit(1)
    
    print(f"Found {len(audio_files)} audio files")
    
    # Limit to first 100 files for POC
    if len(audio_files) > 100:
        print(f"Limiting to first 100 files for POC testing")
        audio_files = audio_files[:100]
    
    # Generate fingerprints
    print(f"\n🎯 Generating fingerprints for {len(audio_files)} files...")
    tester.generate_fingerprints(audio_files)
    
    # Generate and save report
    print(f"\n📊 Analyzing results...")
    report = tester.generate_report()
    
    # Save detailed report to JSON
    report_file = "fingerprinting_poc_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: {report_file}")
    
    # Print summary
    tester.print_summary(report)
    
    print(f"\n🏁 POC Complete!")
    print(f"Review the detailed report in {report_file} for full analysis.")

if __name__ == "__main__":
    main()