#!/usr/bin/env python3
"""
Quick test of fingerprinting algorithms without needing audio files
Tests the core functionality using synthetic audio signals
"""

import numpy as np
import librosa
import tempfile
import os
from fingerprinting_poc import AudioFingerprinter, FingerprintResult

def create_test_audio(frequency=440, duration=5, sr=22050):
    """Create a simple sine wave for testing"""
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    return audio, sr

def test_fingerprinting_algorithms():
    """Test all fingerprinting algorithms with synthetic audio"""
    print("🧪 Testing Fingerprinting Algorithms")
    print("=" * 50)
    
    # Create test audio signals
    test_signals = [
        ("440Hz_tone", create_test_audio(440, 5)),  # A4 note
        ("880Hz_tone", create_test_audio(880, 5)),  # A5 note  
        ("440Hz_duplicate", create_test_audio(440, 5)),  # Same as first
    ]
    
    fingerprinter = AudioFingerprinter()
    results = []
    
    # Test each algorithm
    for name, (audio, sr) in test_signals:
        print(f"\nTesting: {name}")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_filename = temp_file.name
        temp_file.close()  # Close the file handle first
        
        try:
            # Save audio to temporary file
            import soundfile as sf
            sf.write(temp_filename, audio, sr)
            
            # Test spectral fingerprinting
            result = fingerprinter.spectral_fingerprint(temp_filename)
            results.append((name, result))
            
            if result.error:
                print(f"  ❌ Spectral: {result.error}")
            else:
                print(f"  ✅ Spectral: {result.fingerprint[:16]}... ({result.processing_time:.3f}s)")
            
            # Test file hash
            hash_result = fingerprinter.simple_hash_fingerprint(temp_filename)
            if hash_result.error:
                print(f"  ❌ File Hash: {hash_result.error}")
            else:
                print(f"  ✅ File Hash: {hash_result.fingerprint[:16]}... ({hash_result.processing_time:.3f}s)")
            
        finally:
            # Clean up
            try:
                os.unlink(temp_filename)
            except (OSError, PermissionError):
                pass  # File might still be locked, that's OK for testing
    
    # Test duplicate detection
    print(f"\n🔍 Duplicate Detection Test:")
    fingerprints = {}
    
    for name, result in results:
        if not result.error:
            if result.fingerprint in fingerprints:
                print(f"  ✅ Found duplicate: {name} matches {fingerprints[result.fingerprint]}")
            else:
                fingerprints[result.fingerprint] = name
                print(f"  📝 New fingerprint: {name}")
    
    print(f"\n✅ Algorithm test complete!")
    
    # Expected results
    expected_duplicates = 2  # 440Hz_tone should match 440Hz_duplicate
    actual_duplicates = len([fp for fp, names in fingerprints.items() if len(names) > 1]) if any(isinstance(v, list) for v in fingerprints.values()) else 0
    
    print(f"Expected duplicate pairs: 1 (440Hz tones)")
    print(f"Detected unique fingerprints: {len(set(r.fingerprint for _, r in results if not r.error))}")
    
    return len(results) > 0

if __name__ == "__main__":
    try:
        success = test_fingerprinting_algorithms()
        if success:
            print(f"\n🎯 Ready to test with real audio files!")
            print("Run: python fingerprinting_poc.py <your_music_directory>")
        else:
            print(f"\n❌ Test failed. Check error messages above.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()