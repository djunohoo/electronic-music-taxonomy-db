"""
Audio analysis and feature extraction for genre identification.
"""
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

class AudioFeatureExtractor:
    """Extract audio features for genre identification."""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.n_fft = 2048
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file."""
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise ValueError(f"Error loading audio file {file_path}: {e}")
    
    def extract_tempo_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract tempo-related features."""
        # Beat tracking
        tempo, beats = librosa.beat.beat_track(y=y, sr=self.sample_rate)
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(y=y, sr=self.sample_rate)
        onset_times = librosa.onset.frames_to_time(onset_frames, sr=self.sample_rate)
        
        return {
            'tempo': float(tempo),
            'beat_count': len(beats),
            'onset_count': len(onset_times),
            'onset_density': len(onset_times) / (len(y) / self.sample_rate)
        }
    
    def extract_spectral_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract spectral features."""
        # Compute spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=self.sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sample_rate)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=self.sample_rate)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        return {
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'spectral_centroid_std': np.std(spectral_centroids),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'spectral_rolloff_std': np.std(spectral_rolloff),
            'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
            'spectral_bandwidth_std': np.std(spectral_bandwidth),
            'zero_crossing_rate_mean': np.mean(zero_crossing_rate),
            'zero_crossing_rate_std': np.std(zero_crossing_rate)
        }
    
    def extract_harmonic_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract harmonic and percussive features."""
        # Separate harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Harmonic features
        harmonic_energy = np.sum(y_harmonic ** 2)
        percussive_energy = np.sum(y_percussive ** 2)
        
        # Harmonic-percussive ratio
        hp_ratio = harmonic_energy / (percussive_energy + 1e-8)
        
        return {
            'harmonic_energy': float(harmonic_energy),
            'percussive_energy': float(percussive_energy),
            'harmonic_percussive_ratio': float(hp_ratio)
        }
    
    def extract_mfcc_features(self, y: np.ndarray, n_mfcc: int = 13) -> Dict[str, float]:
        """Extract MFCC features."""
        mfccs = librosa.feature.mfcc(y=y, sr=self.sample_rate, n_mfcc=n_mfcc)
        
        features = {}
        for i in range(n_mfcc):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])
        
        return features
    
    def extract_chroma_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract chroma features for harmonic analysis."""
        chroma = librosa.feature.chroma_stft(y=y, sr=self.sample_rate)
        
        return {
            'chroma_mean': np.mean(chroma),
            'chroma_std': np.std(chroma),
            'chroma_max': np.max(chroma),
            'dominant_chroma': int(np.argmax(np.mean(chroma, axis=1)))
        }
    
    def extract_all_features(self, file_path: str) -> Dict[str, float]:
        """Extract all audio features from a file."""
        y, sr = self.load_audio(file_path)
        
        features = {}
        features.update(self.extract_tempo_features(y))
        features.update(self.extract_spectral_features(y))
        features.update(self.extract_harmonic_features(y))
        features.update(self.extract_mfcc_features(y))
        features.update(self.extract_chroma_features(y))
        
        return features

class GenreClassifier:
    """Machine learning classifier for genre identification."""
    
    def __init__(self):
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.genre_labels = []
    
    def prepare_training_data(self, feature_data: List[Dict], labels: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare feature data for training."""
        # Get feature names from first sample
        if feature_data:
            self.feature_names = list(feature_data[0].keys())
        
        # Convert to numpy array
        X = np.array([[sample[feature] for feature in self.feature_names] for sample in feature_data])
        y = np.array(labels)
        
        # Store unique labels
        self.genre_labels = list(set(labels))
        
        return X, y
    
    def train(self, feature_data: List[Dict], labels: List[str]) -> Dict[str, float]:
        """Train the classifier."""
        X, y = self.prepare_training_data(feature_data, labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train classifier
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.classifier.score(X_train_scaled, y_train)
        test_score = self.classifier.score(X_test_scaled, y_test)
        
        # Get detailed metrics
        y_pred = self.classifier.predict(X_test_scaled)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'classification_report': report
        }
    
    def predict_genre(self, features: Dict[str, float]) -> Tuple[str, float]:
        """Predict genre from audio features."""
        # Convert features to array
        feature_array = np.array([[features[feature] for feature in self.feature_names]])
        
        # Scale features
        feature_array_scaled = self.scaler.transform(feature_array)
        
        # Predict
        prediction = self.classifier.predict(feature_array_scaled)[0]
        probability = np.max(self.classifier.predict_proba(feature_array_scaled))
        
        return prediction, probability
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        importances = self.classifier.feature_importances_
        return dict(zip(self.feature_names, importances))
    
    def save_model(self, model_path: str):
        """Save trained model."""
        model_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'genre_labels': self.genre_labels
        }
        joblib.dump(model_data, model_path)
    
    def load_model(self, model_path: str):
        """Load trained model."""
        model_data = joblib.load(model_path)
        self.classifier = model_data['classifier']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.genre_labels = model_data['genre_labels']

class GenreAnalyzer:
    """High-level interface for genre analysis."""
    
    def __init__(self):
        self.feature_extractor = AudioFeatureExtractor()
        self.classifier = GenreClassifier()
    
    def analyze_audio_file(self, file_path: str) -> Dict:
        """Analyze an audio file and predict its genre."""
        # Extract features
        features = self.feature_extractor.extract_all_features(file_path)
        
        # Predict genre (if model is trained)
        try:
            genre, confidence = self.classifier.predict_genre(features)
            return {
                'predicted_genre': genre,
                'confidence': confidence,
                'features': features
            }
        except:
            return {
                'predicted_genre': None,
                'confidence': None,
                'features': features
            }
    
    def visualize_features(self, features: Dict[str, float], save_path: Optional[str] = None):
        """Visualize extracted features."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Tempo features
        tempo_features = {k: v for k, v in features.items() if 'tempo' in k or 'beat' in k or 'onset' in k}
        if tempo_features:
            axes[0, 0].bar(tempo_features.keys(), tempo_features.values())
            axes[0, 0].set_title('Tempo Features')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Spectral features
        spectral_features = {k: v for k, v in features.items() if 'spectral' in k}
        if spectral_features:
            axes[0, 1].bar(spectral_features.keys(), spectral_features.values())
            axes[0, 1].set_title('Spectral Features')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # MFCC features (means only)
        mfcc_means = {k: v for k, v in features.items() if 'mfcc' in k and 'mean' in k}
        if mfcc_means:
            axes[1, 0].bar(range(len(mfcc_means)), list(mfcc_means.values()))
            axes[1, 0].set_title('MFCC Features (Means)')
            axes[1, 0].set_xlabel('MFCC Coefficient')
        
        # Harmonic features
        harmonic_features = {k: v for k, v in features.items() if any(x in k for x in ['harmonic', 'chroma'])}
        if harmonic_features:
            axes[1, 1].bar(harmonic_features.keys(), harmonic_features.values())
            axes[1, 1].set_title('Harmonic Features')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

if __name__ == "__main__":
    # Example usage
    analyzer = GenreAnalyzer()
    
    # Example: analyze a file (would need actual audio file)
    # result = analyzer.analyze_audio_file("path/to/audio.wav")
    # print(f"Predicted genre: {result['predicted_genre']}")
    # print(f"Confidence: {result['confidence']}")
    
    print("Audio analysis module ready!")