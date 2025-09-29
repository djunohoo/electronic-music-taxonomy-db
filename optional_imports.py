"""
Optional Audio Processing Imports
Only import these if needed for advanced audio analysis
"""

# Optional audio processing libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("[INFO] librosa not available - advanced audio analysis disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[INFO] numpy not available - numerical processing limited")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("[INFO] soundfile not available - audio file I/O limited")

try:
    import chromaprint
    import acoustid
    FINGERPRINTING_AVAILABLE = True
except ImportError:
    FINGERPRINTING_AVAILABLE = False
    print("[INFO] audio fingerprinting not available")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[INFO] psutil not available - system monitoring limited")

def get_available_features():
    """Return dict of available optional features"""
    return {
        'librosa': LIBROSA_AVAILABLE,
        'numpy': NUMPY_AVAILABLE,
        'soundfile': SOUNDFILE_AVAILABLE,
        'fingerprinting': FINGERPRINTING_AVAILABLE,
        'system_monitoring': PSUTIL_AVAILABLE
    }
