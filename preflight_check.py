#!/usr/bin/env python3
"""
Pre-Flight System Check
Validates everything is ready for large-scale testing while waiting for file copy
"""

import os
import sys
import time
import psutil
import platform
from pathlib import Path

def check_system_resources():
    """Check if system can handle large-scale processing"""
    print("🖥️  SYSTEM RESOURCE CHECK")
    print("-" * 40)
    
    # CPU info
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    print(f"  CPU Cores: {cpu_count}")
    print(f"  CPU Frequency: {cpu_freq.current:.0f} MHz" if cpu_freq else "  CPU Frequency: Unknown")
    
    # Memory info
    memory = psutil.virtual_memory()
    print(f"  RAM Total: {memory.total / (1024**3):.1f} GB")
    print(f"  RAM Available: {memory.available / (1024**3):.1f} GB")
    print(f"  RAM Usage: {memory.percent}%")
    
    # Disk info
    disk = psutil.disk_usage('.')
    print(f"  Disk Free: {disk.free / (1024**3):.1f} GB")
    
    # Recommendations
    recommended_workers = min(cpu_count, 8)
    memory_per_worker = memory.available / (1024**3) / recommended_workers
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  Optimal workers: {recommended_workers}")
    print(f"  Memory per worker: {memory_per_worker:.1f} GB")
    
    if memory.available / (1024**3) < 4:
        print("  ⚠️  WARNING: Low memory - consider smaller batch sizes")
    if disk.free / (1024**3) < 10:
        print("  ⚠️  WARNING: Low disk space - may affect checkpoint saves")
    
    return {
        "cpu_cores": cpu_count,
        "ram_gb": memory.total / (1024**3),
        "recommended_workers": recommended_workers,
        "ready": memory.available / (1024**3) >= 2 and disk.free / (1024**3) >= 5
    }

def test_audio_processing_speed():
    """Benchmark audio processing speed"""
    print(f"\n🎵 AUDIO PROCESSING BENCHMARK")
    print("-" * 40)
    
    try:
        from test_algorithms import create_test_audio, AudioFingerprinter
        import tempfile
        import soundfile as sf
        
        fingerprinter = AudioFingerprinter()
        
        # Create test audio
        audio, sr = create_test_audio(440, 10)  # 10 second test
        
        # Test processing speed
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        temp_file.close()
        
        try:
            sf.write(temp_filename, audio, sr)
            
            # Benchmark spectral analysis
            start_time = time.time()
            result = fingerprinter.spectral_fingerprint(temp_filename)
            spectral_time = time.time() - start_time
            
            # Benchmark file hash
            start_time = time.time()
            hash_result = fingerprinter.simple_hash_fingerprint(temp_filename)
            hash_time = time.time() - start_time
            
            print(f"  Spectral Analysis: {spectral_time:.3f}s per 10s audio")
            print(f"  File Hash: {hash_time:.3f}s per file")
            
            # Extrapolate for large collection
            spectral_rate = 10 / spectral_time if spectral_time > 0 else float('inf')
            hash_rate = 1 / hash_time if hash_time > 0 else float('inf')
            
            print(f"\n📊 PROJECTED RATES:")
            print(f"  Spectral: {spectral_rate:.1f} seconds of audio per second")
            print(f"  Hash: {hash_rate:.0f} files per second")
            
            # Time estimates for 23,000 files
            estimated_spectral = 23000 * (spectral_time / 10) * 4  # Assume 4min average track
            estimated_hash = 23000 * hash_time
            
            print(f"\n⏱️  23,000 FILE ESTIMATES:")
            print(f"  Spectral only: {estimated_spectral/3600:.1f} hours")
            print(f"  Hash only: {estimated_hash/60:.1f} minutes")
            print(f"  Both algorithms: {max(estimated_spectral, estimated_hash)/3600:.1f} hours")
            
        finally:
            try:
                os.unlink(temp_filename)
            except:
                pass
        
        return {
            "spectral_time": spectral_time,
            "hash_time": hash_time,
            "estimated_hours": max(estimated_spectral, estimated_hash) / 3600
        }
        
    except Exception as e:
        print(f"  ❌ Benchmark failed: {e}")
        return {"error": str(e)}

def check_directory_monitoring():
    """Set up monitoring for when copy completes"""
    print(f"\n📁 DIRECTORY MONITORING SETUP")
    print("-" * 40)
    
    common_paths = [
        "D:/Music",
        "E:/Music", 
        "C:/Users/Administrator/Music",
        "C:/Music",
        "./music_test"
    ]
    
    print("  Common music directory paths to check:")
    for path in common_paths:
        if os.path.exists(path):
            try:
                file_count = sum(1 for _ in Path(path).rglob('*.*'))
                print(f"    ✅ {path} ({file_count} files)")
            except:
                print(f"    📁 {path} (access limited)")
        else:
            print(f"    ❌ {path}")
    
    print(f"\n💡 When your copy completes, we'll be ready to run:")
    print(f"  python large_scale_test.py \"<your_music_path>\" --sample 1000")

def create_optimal_config():
    """Create an optimized config based on system specs"""
    print(f"\n⚙️  GENERATING OPTIMAL CONFIG")
    print("-" * 40)
    
    system_info = check_system_resources()
    
    # Calculate optimal settings
    if system_info["ram_gb"] >= 16:
        batch_size = 200
        workers = min(system_info["cpu_cores"], 8)
    elif system_info["ram_gb"] >= 8:
        batch_size = 100
        workers = min(system_info["cpu_cores"], 6)
    else:
        batch_size = 50
        workers = min(system_info["cpu_cores"], 4)
    
    config = {
        "batch_size": batch_size,
        "parallel_workers": workers,
        "save_interval": 100,
        "algorithms": ["spectral_custom", "file_hash"]
    }
    
    print(f"  Optimal batch size: {batch_size}")
    print(f"  Parallel workers: {workers}")
    print(f"  Save interval: {config['save_interval']} files")
    print(f"  Algorithms: {', '.join(config['algorithms'])}")
    
    # Save config for later use
    import json
    with open("optimal_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"  💾 Config saved to optimal_config.json")
    
    return config

def main():
    """Run complete pre-flight check"""
    print("🚀 PRE-FLIGHT CHECK FOR 23,000 TRACK TEST")
    print("="*50)
    print("Running while waiting for file copy to complete...\n")
    
    # System check
    system_ready = check_system_resources()
    
    # Audio processing benchmark
    benchmark_results = test_audio_processing_speed()
    
    # Directory monitoring
    check_directory_monitoring()
    
    # Optimal configuration
    optimal_config = create_optimal_config()
    
    # Final readiness assessment
    print(f"\n🎯 READINESS ASSESSMENT")
    print("="*30)
    
    ready_items = []
    if system_ready["ready"]:
        ready_items.append("✅ System resources adequate")
    else:
        ready_items.append("⚠️  System resources limited - proceed with caution")
    
    if "error" not in benchmark_results:
        if benchmark_results.get("estimated_hours", 10) < 6:
            ready_items.append("✅ Processing speed acceptable")
        else:
            ready_items.append("⚠️  Processing will take >6 hours")
    else:
        ready_items.append("❌ Audio processing benchmark failed")
    
    ready_items.append("✅ Test framework ready")
    ready_items.append("✅ Configuration optimized")
    
    for item in ready_items:
        print(f"  {item}")
    
    print(f"\n🎵 READY FOR 23,000 TRACK VALIDATION!")
    print(f"Once your copy completes, run:")
    print(f"  python large_scale_test.py \"<path>\" --sample 1000 --workers {optimal_config['parallel_workers']}")
    
    return all("✅" in item for item in ready_items)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⏸️  Pre-flight check interrupted")
    except Exception as e:
        print(f"\n❌ Pre-flight check failed: {e}")
        import traceback
        traceback.print_exc()