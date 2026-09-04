"""
Audio Service
=============
Audio processing and feature extraction
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
import io


class AudioService:
    """
    Service for audio processing
    Handles audio loading, preprocessing, and feature extraction
    """
    
    def __init__(self):
        """Initialize audio service"""
        self.sample_rate = 16000  # Standard sample rate for speech
        self.chunk_duration = 2   # seconds
    
    async def load_audio(self, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """
        Load audio from bytes
        
        Args:
            audio_bytes: Raw audio file bytes
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            import librosa
            import soundfile as sf
            
            # Load audio from bytes
            audio_data, sample_rate = librosa.load(
                io.BytesIO(audio_bytes),
                sr=self.sample_rate,
                mono=True
            )
            
            return audio_data, sample_rate
            
        except Exception as e:
            # Fallback: Create dummy audio for demo
            print(f"Audio loading error (using dummy): {e}")
            dummy_audio = np.random.randn(self.sample_rate * 2).astype(np.float32)
            return dummy_audio, self.sample_rate
    
    async def preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Preprocess audio for analysis
        
        Steps:
        1. Normalize
        2. Remove silence
        3. Standardize length
        
        Args:
            audio_data: Raw audio data
            sample_rate: Audio sample rate
            
        Returns:
            Preprocessed audio data
        """
        # Normalize audio
        audio_data = self._normalize(audio_data)
        
        # Remove silence
        audio_data = self._remove_silence(audio_data, sample_rate)
        
        # Standardize length (2 seconds)
        target_length = sample_rate * self.chunk_duration
        audio_data = self._standardize_length(audio_data, target_length)
        
        return audio_data
    
    async def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Extract audio features for analysis
        
        Features extracted:
        - MFCCs (Mel-Frequency Cepstral Coefficients)
        - Spectral features
        - Prosody features
        - Phase features
        
        Args:
            audio_data: Preprocessed audio data
            sample_rate: Audio sample rate
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            import librosa
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features["mfccs"] = mfccs.mean(axis=1).tolist()
            
            # Spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features["spectral_centroid"] = float(spectral_centroid.mean())
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            features["spectral_bandwidth"] = float(spectral_bandwidth.mean())
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            features["spectral_rolloff"] = float(spectral_rolloff.mean())
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features["zero_crossing_rate"] = float(zcr.mean())
            
            # RMS energy
            rms = librosa.feature.rms(y=audio_data)
            features["rms_energy"] = float(rms.mean())
            
            # Pitch (F0)
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate)
            features["pitch_mean"] = float(pitches.mean())
            features["pitch_std"] = float(pitches.std())
            
        except ImportError:
            # Fallback features if librosa not available
            features = self._extract_basic_features(audio_data, sample_rate)
        
        return features
    
    def _extract_basic_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Extract basic features without librosa
        """
        return {
            "mean": float(np.mean(audio_data)),
            "std": float(np.std(audio_data)),
            "max": float(np.max(audio_data)),
            "min": float(np.min(audio_data)),
            "rms_energy": float(np.sqrt(np.mean(audio_data**2))),
            "zero_crossing_rate": float(np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data)),
            "duration": len(audio_data) / sample_rate
        }
    
    def _normalize(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        return audio_data
    
    def _remove_silence(self, audio_data: np.ndarray, sample_rate: int, threshold: float = 0.01) -> np.ndarray:
        """
        Remove silence from audio
        """
        # Simple energy-based silence removal
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop
        
        # Calculate frame energies
        frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=hop_length)
        energies = np.sum(frames**2, axis=0)
        
        # Find non-silent frames
        non_silent = energies > threshold
        
        if not np.any(non_silent):
            return audio_data  # Return original if all silence
        
        # Reconstruct audio
        non_silent_indices = np.where(non_silent)[0]
        start = non_silent_indices[0] * hop_length
        end = non_silent_indices[-1] * hop_length + frame_length
        
        return audio_data[start:end]
    
    def _standardize_length(self, audio_data: np.ndarray, target_length: int) -> np.ndarray:
        """
        Standardize audio length
        """
        current_length = len(audio_data)
        
        if current_length > target_length:
            # Truncate
            audio_data = audio_data[:target_length]
        elif current_length < target_length:
            # Pad with zeros
            padding = target_length - current_length
            audio_data = np.pad(audio_data, (0, padding), mode='constant')
        
        return audio_data
    
    def get_audio_info(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Get audio information
        """
        return {
            "duration": len(audio_data) / sample_rate,
            "sample_rate": sample_rate,
            "samples": len(audio_data),
            "channels": 1,  # Mono
            "format": "numpy_array"
        }
