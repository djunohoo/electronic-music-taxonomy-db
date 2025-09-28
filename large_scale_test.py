#!/usr/bin/env python3
"""
Large-Scale Audio Fingerprinting Test
Optimized for testing on collections of 10,000+ tracks

This version includes:
- Progress tracking and resumption
- Batch processing for memory efficiency  
- Parallel processing options
- Statistical sampling for quick validation
- Performance monitoring and optimization
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from collections import defaultdict

# Import our fingerprinting classes
from fingerprinting_poc import AudioFingerprinter, FingerprintResult, TestScenario

@dataclass
class LargeScaleTestConfig:
    """Configuration for large-scale testing"""
    max_files: Optional[int] = None  # None = process all files
    sample_size: Optional[int] = 1000  # For quick validation runs
    batch_size: int = 100  # Process files in batches
    parallel_workers: int = 4  # Number of parallel processing threads
    save_interval: int = 50  # Save progress every N files
    algorithms: List[str] = None  # Default: ["spectral_custom", "file_hash"]
    resume_from_checkpoint: bool = True
    
    def __post_init__(self):
        if self.algorithms is None:
            self.algorithms = ["spectral_custom", "file_hash"]
        
        # Auto-detect optimal worker count
        if self.parallel_workers == "auto":
            self.parallel_workers = min(multiprocessing.cpu_count(), 8)

class LargeScaleTester:
    """Enhanced tester for large music collections"""
    
    def __init__(self, test_directory: str, config: LargeScaleTestConfig = None):
        self.test_directory = Path(test_directory)
        self.config = config or LargeScaleTestConfig()
        self.fingerprinter = AudioFingerprinter()
        
        # Results storage
        self.results: Dict[str, List[Dict]] = defaultdict(list)
        self.checkpoint_file = "large_scale_checkpoint.json"
        self.final_report_file = "large_scale_report.json"
        
        # Performance tracking
        self.start_time = None
        self.processed_count = 0
        self.error_count = 0
        self.duplicate_pairs = []
        
        print(f"🎵 Large-Scale Fingerprinting Test Initialized")
        print(f"📁 Directory: {self.test_directory}")
        print(f"⚙️  Config: {self.config.max_files or 'ALL'} files, "
              f"{self.config.parallel_workers} workers, "
              f"algorithms: {', '.join(self.config.algorithms)}")
    
    def scan_audio_files(self) -> List[str]:
        """Scan directory for all audio files with progress tracking"""
        print("\n🔍 Scanning for audio files...")
        
        supported_formats = {'.mp3', '.wav', '.flac', '.m4a', '.aiff', '.ogg', '.wma'}
        audio_files = []
        
        # Use rglob for recursive scanning with progress
        total_checked = 0
        
        for file_path in self.test_directory.rglob('*'):
            total_checked += 1
            if total_checked % 1000 == 0:
                print(f"  Scanned {total_checked} files, found {len(audio_files)} audio files...")
            
            if file_path.suffix.lower() in supported_formats:
                audio_files.append(str(file_path))
        
        print(f"✅ Scan complete: {len(audio_files)} audio files found in {total_checked} total files")
        
        # Apply limits and sampling
        if self.config.sample_size and len(audio_files) > self.config.sample_size:
            if input(f"\nFound {len(audio_files)} files. Run quick sample of {self.config.sample_size} files? (y/n): ").lower() == 'y':
                audio_files = random.sample(audio_files, self.config.sample_size)
                print(f"📊 Using random sample of {len(audio_files)} files for quick validation")
        
        if self.config.max_files and len(audio_files) > self.config.max_files:
            audio_files = audio_files[:self.config.max_files]
            print(f"📊 Limited to first {len(audio_files)} files")
        
        return sorted(audio_files)
    
    def load_checkpoint(self) -> Dict:
        """Load previous progress if available"""
        if not self.config.resume_from_checkpoint or not os.path.exists(self.checkpoint_file):
            return {"completed_files": [], "results": defaultdict(list)}
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            self.results = defaultdict(list, checkpoint.get("results", {}))
            completed_files = set(checkpoint.get("completed_files", []))
            
            print(f"📄 Resuming from checkpoint: {len(completed_files)} files already processed")
            return checkpoint
            
        except Exception as e:
            print(f"⚠️  Could not load checkpoint: {e}")
            return {"completed_files": [], "results": defaultdict(list)}
    
    def save_checkpoint(self, completed_files: List[str]) -> None:
        """Save current progress"""
        checkpoint = {
            "completed_files": completed_files,
            "results": dict(self.results),
            "config": asdict(self.config),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processed_count": self.processed_count,
            "error_count": self.error_count
        }
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save checkpoint: {e}")
    
    def process_file_batch(self, file_batch: List[str], batch_id: int) -> List[Tuple[str, str, FingerprintResult]]:
        """Process a batch of files with one algorithm"""
        batch_results = []
        
        for file_path in file_batch:
            for algorithm in self.config.algorithms:
                try:
                    if algorithm == "spectral_custom":
                        result = self.fingerprinter.spectral_fingerprint(file_path)
                    elif algorithm == "file_hash":
                        result = self.fingerprinter.simple_hash_fingerprint(file_path)
                    elif algorithm == "chromaprint":
                        result = self.fingerprinter.chromaprint_fingerprint(file_path)
                    else:
                        continue
                    
                    batch_results.append((file_path, algorithm, result))
                    
                except Exception as e:
                    # Create error result
                    error_result = FingerprintResult(
                        file_path=file_path,
                        algorithm=algorithm,
                        fingerprint="",
                        duration=0,
                        processing_time=0,
                        error=str(e)
                    )
                    batch_results.append((file_path, algorithm, error_result))
        
        return batch_results
    
    def parallel_fingerprint_generation(self, audio_files: List[str]) -> None:
        """Generate fingerprints using parallel processing"""
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        completed_files = set(checkpoint["completed_files"])
        
        # Filter out already processed files
        remaining_files = [f for f in audio_files if f not in completed_files]
        
        if not remaining_files:
            print("✅ All files already processed!")
            return
        
        print(f"\n🚀 Starting parallel processing of {len(remaining_files)} files...")
        print(f"⚙️  Using {self.config.parallel_workers} workers, batch size {self.config.batch_size}")
        
        self.start_time = time.time()
        processed_files_list = list(completed_files)
        
        # Create batches
        batches = [remaining_files[i:i + self.config.batch_size] 
                  for i in range(0, len(remaining_files), self.config.batch_size)]
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.config.parallel_workers) as executor:
            
            # Submit all batches
            future_to_batch = {
                executor.submit(self.process_file_batch, batch, i): (i, batch)
                for i, batch in enumerate(batches)
            }
            
            completed_batches = 0
            
            for future in as_completed(future_to_batch):
                batch_id, batch_files = future_to_batch[future]
                
                try:
                    batch_results = future.result()
                    
                    # Process results
                    for file_path, algorithm, result in batch_results:
                        
                        # Convert result to dict for JSON serialization
                        result_dict = {
                            "file_path": result.file_path,
                            "algorithm": result.algorithm,
                            "fingerprint": result.fingerprint,
                            "duration": result.duration,
                            "processing_time": result.processing_time,
                            "error": result.error
                        }
                        
                        self.results[algorithm].append(result_dict)
                        
                        if result.error:
                            self.error_count += 1
                    
                    # Update progress
                    self.processed_count += len(batch_files)
                    processed_files_list.extend(batch_files)
                    completed_batches += 1
                    
                    # Progress update
                    elapsed = time.time() - self.start_time
                    rate = self.processed_count / elapsed if elapsed > 0 else 0
                    eta = (len(remaining_files) - self.processed_count) / rate if rate > 0 else 0
                    
                    print(f"📊 Batch {completed_batches}/{len(batches)} complete | "
                          f"{self.processed_count}/{len(remaining_files)} files | "
                          f"{rate:.1f} files/sec | "
                          f"ETA: {eta/60:.1f}min | "
                          f"Errors: {self.error_count}")
                    
                    # Save checkpoint periodically
                    if completed_batches % (self.config.save_interval // self.config.batch_size + 1) == 0:
                        self.save_checkpoint(processed_files_list)
                        print(f"💾 Checkpoint saved")
                
                except Exception as e:
                    print(f"❌ Batch {batch_id} failed: {e}")
                    self.error_count += len(batch_files)
        
        # Final checkpoint
        self.save_checkpoint(processed_files_list)
        
        total_time = time.time() - self.start_time
        print(f"\n✅ Processing complete!")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📊 Average rate: {len(remaining_files)/total_time:.1f} files/second")
        print(f"❌ Errors: {self.error_count}/{len(remaining_files)} ({self.error_count/len(remaining_files)*100:.1f}%)")
    
    def analyze_large_scale_duplicates(self) -> Dict:
        """Analyze duplicate detection across large dataset"""
        print(f"\n🔍 Analyzing duplicates across {sum(len(results) for results in self.results.values())} fingerprints...")
        
        duplicate_analysis = {}
        
        for algorithm in self.results.keys():
            fingerprint_groups = defaultdict(list)
            
            # Group by fingerprint
            for result_dict in self.results[algorithm]:
                if result_dict["error"] is None and result_dict["fingerprint"]:
                    fingerprint_groups[result_dict["fingerprint"]].append(result_dict["file_path"])
            
            # Find duplicates (groups with >1 file)
            duplicates = {fp: files for fp, files in fingerprint_groups.items() if len(files) > 1}
            
            # Calculate statistics
            total_files = len([r for r in self.results[algorithm] if not r["error"]])
            duplicate_files = sum(len(files) for files in duplicates.values())
            duplicate_groups = len(duplicates)
            
            duplicate_analysis[algorithm] = {
                "total_files": total_files,
                "duplicate_groups": duplicate_groups,
                "duplicate_files": duplicate_files,
                "unique_files": total_files - duplicate_files,
                "duplication_rate": duplicate_files / total_files if total_files > 0 else 0,
                "average_group_size": duplicate_files / duplicate_groups if duplicate_groups > 0 else 0,
                "largest_group": max(len(files) for files in duplicates.values()) if duplicates else 0,
                "sample_duplicates": dict(list(duplicates.items())[:5])  # Sample for inspection
            }
            
            print(f"  {algorithm.upper()}:")
            print(f"    🔍 {duplicate_groups} duplicate groups found")
            print(f"    📁 {duplicate_files} duplicate files ({duplicate_analysis[algorithm]['duplication_rate']:.1%})")
            print(f"    📊 Average group size: {duplicate_analysis[algorithm]['average_group_size']:.1f}")
            print(f"    📈 Largest group: {duplicate_analysis[algorithm]['largest_group']} files")
        
        return duplicate_analysis
    
    def generate_large_scale_report(self) -> Dict:
        """Generate comprehensive report for large-scale test"""
        print(f"\n📊 Generating large-scale analysis report...")
        
        # Performance analysis
        performance_stats = {}
        for algorithm in self.results.keys():
            results = self.results[algorithm]
            successful = [r for r in results if r["error"] is None]
            failed = [r for r in results if r["error"] is not None]
            
            if successful:
                processing_times = [r["processing_time"] for r in successful]
                durations = [r["duration"] for r in successful if r["duration"] > 0]
                
                performance_stats[algorithm] = {
                    "total_processed": len(results),
                    "successful": len(successful),
                    "failed": len(failed),
                    "success_rate": len(successful) / len(results) if results else 0,
                    "avg_processing_time": sum(processing_times) / len(processing_times),
                    "total_processing_time": sum(processing_times),
                    "min_processing_time": min(processing_times),
                    "max_processing_time": max(processing_times),
                    "avg_audio_duration": sum(durations) / len(durations) if durations else 0
                }
        
        # Duplicate analysis
        duplicate_analysis = self.analyze_large_scale_duplicates()
        
        # Overall statistics
        total_files = self.processed_count + len(set().union(*[
            {r["file_path"] for r in results} for results in self.results.values()
        ]))
        
        overall_stats = {
            "test_scale": "LARGE_SCALE",
            "total_files_scanned": total_files,
            "total_files_processed": self.processed_count,
            "total_errors": self.error_count,
            "algorithms_tested": list(self.results.keys()),
            "test_duration_minutes": (time.time() - self.start_time) / 60 if self.start_time else 0,
            "config": asdict(self.config),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Compile final report
        report = {
            "overall_statistics": overall_stats,
            "performance_analysis": performance_stats,
            "duplicate_analysis": duplicate_analysis,
            "error_analysis": self.analyze_errors(),
            "recommendations": self.generate_recommendations(duplicate_analysis, performance_stats)
        }
        
        return report
    
    def analyze_errors(self) -> Dict:
        """Analyze error patterns"""
        error_analysis = defaultdict(lambda: defaultdict(int))
        
        for algorithm in self.results.keys():
            for result in self.results[algorithm]:
                if result["error"]:
                    # Categorize error
                    error_msg = result["error"].lower()
                    if "format" in error_msg or "codec" in error_msg:
                        category = "format_unsupported"
                    elif "permission" in error_msg or "access" in error_msg:
                        category = "file_access"
                    elif "corrupt" in error_msg or "invalid" in error_msg:
                        category = "file_corruption"
                    elif "memory" in error_msg:
                        category = "memory_error"
                    else:
                        category = "other"
                    
                    error_analysis[algorithm][category] += 1
        
        return dict(error_analysis)
    
    def generate_recommendations(self, duplicate_analysis: Dict, performance_stats: Dict) -> List[str]:
        """Generate recommendations based on large-scale test results"""
        recommendations = []
        
        # Performance recommendations
        best_algorithm = min(performance_stats.items(), 
                           key=lambda x: x[1]["avg_processing_time"])
        recommendations.append(f"🚀 PERFORMANCE: {best_algorithm[0].upper()} is fastest at {best_algorithm[1]['avg_processing_time']:.3f}s/file")
        
        # Accuracy recommendations  
        best_duplicate_detector = max(duplicate_analysis.items(),
                                    key=lambda x: x[1]["duplicate_groups"])
        recommendations.append(f"🎯 DUPLICATE DETECTION: {best_duplicate_detector[0].upper()} found most duplicates ({best_duplicate_detector[1]['duplicate_groups']} groups)")
        
        # Scale recommendations
        if self.processed_count >= 10000:
            recommendations.append("📈 SCALE VALIDATION: Successfully processed 10,000+ files - ready for production")
        elif self.processed_count >= 1000:
            recommendations.append("📊 SCALE TESTING: Good validation on 1,000+ files - consider larger test")
        
        # Error rate recommendations
        overall_error_rate = self.error_count / self.processed_count if self.processed_count > 0 else 1
        if overall_error_rate < 0.05:
            recommendations.append("✅ ERROR RATE: Excellent (<5% errors) - production ready")
        elif overall_error_rate < 0.15:
            recommendations.append("⚠️  ERROR RATE: Acceptable (5-15% errors) - monitor in production")
        else:
            recommendations.append("❌ ERROR RATE: High (>15% errors) - investigate before production")
        
        return recommendations
    
    def print_large_scale_summary(self, report: Dict) -> None:
        """Print executive summary of large-scale test"""
        
        print("\n" + "="*80)
        print("🎵 LARGE-SCALE FINGERPRINTING TEST RESULTS")
        print("="*80)
        
        stats = report["overall_statistics"]
        print(f"\n📊 TEST SCALE:")
        print(f"  Files processed: {stats['total_files_processed']:,}")
        print(f"  Test duration: {stats['test_duration_minutes']:.1f} minutes")
        print(f"  Algorithms tested: {len(stats['algorithms_tested'])}")
        print(f"  Error rate: {(stats['total_errors']/stats['total_files_processed']*100):.1f}%")
        
        print(f"\n⚡ PERFORMANCE LEADERS:")
        perf = report["performance_analysis"]
        for alg, metrics in perf.items():
            rate = 1 / metrics["avg_processing_time"] if metrics["avg_processing_time"] > 0 else 0
            print(f"  {alg.upper()}: {rate:.1f} files/sec ({metrics['success_rate']:.1%} success)")
        
        print(f"\n🔍 DUPLICATE DETECTION:")
        dup = report["duplicate_analysis"]
        for alg, analysis in dup.items():
            print(f"  {alg.upper()}: {analysis['duplicate_groups']} groups, {analysis['duplication_rate']:.1%} duplication rate")
        
        print(f"\n💡 KEY RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        print(f"\n📄 Detailed report saved to: {self.final_report_file}")
        print("="*80)

def main():
    """Main execution for large-scale testing"""
    
    if len(sys.argv) < 2:
        print("Usage: python large_scale_test.py <audio_directory> [options]")
        print("\nOptions:")
        print("  --sample N        Test on random sample of N files")
        print("  --max N           Limit to first N files")  
        print("  --workers N       Use N parallel workers (default: 4)")
        print("  --no-resume       Don't resume from checkpoint")
        print("\nExample: python large_scale_test.py 'C:/Music' --sample 1000 --workers 8")
        sys.exit(1)
    
    test_directory = sys.argv[1]
    
    # Parse options
    config = LargeScaleTestConfig()
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--sample" and i + 1 < len(sys.argv):
            config.sample_size = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--max" and i + 1 < len(sys.argv):
            config.max_files = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--workers" and i + 1 < len(sys.argv):
            config.parallel_workers = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--no-resume":
            config.resume_from_checkpoint = False
            i += 1
        else:
            i += 1
    
    print("🎵 Large-Scale Electronic Music Fingerprinting Test")
    print("="*60)
    
    # Initialize tester
    tester = LargeScaleTester(test_directory, config)
    
    # Scan files
    audio_files = tester.scan_audio_files()
    
    if not audio_files:
        print("❌ No audio files found")
        sys.exit(1)
    
    print(f"\n🎯 Ready to process {len(audio_files):,} files")
    
    # Confirm large-scale test
    if len(audio_files) > 5000:
        response = input(f"\n⚠️  This will process {len(audio_files):,} files. Continue? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled")
            sys.exit(0)
    
    # Run large-scale fingerprinting
    tester.parallel_fingerprint_generation(audio_files)
    
    # Generate final report
    report = tester.generate_large_scale_report()
    
    # Save detailed report
    with open(tester.final_report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    tester.print_large_scale_summary(report)

if __name__ == "__main__":
    main()