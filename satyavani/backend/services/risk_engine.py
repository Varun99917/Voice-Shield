"""
Risk Engine
===========
Combines all analysis results into final risk score
"""

import numpy as np
from typing import Dict, Any, Optional
from .ml_service import MLService
from .audio_service import AudioService


class RiskEngine:
    """
    Risk Scoring Engine
    Combines multiple analysis results into final risk assessment
    """
    
    def __init__(self):
        """Initialize risk engine"""
        self.ml_service = MLService()
        self.audio_service = AudioService()
        
        # Risk thresholds
        self.thresholds = {
            "safe": 20,      # 0-20% = Safe
            "low": 40,       # 20-40% = Low risk
            "medium": 60,    # 40-60% = Medium risk
            "high": 80,      # 60-80% = High risk
            "critical": 100  # 80-100% = Critical
        }
        
        # Model weights for ensemble
        self.weights = {
            "spectral": 0.30,
            "prosody": 0.25,
            "phase": 0.25,
            "pattern": 0.20
        }
    
    async def analyze_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Complete audio analysis pipeline
        
        Args:
            audio_bytes: Raw audio file bytes
            
        Returns:
            Complete analysis result with risk score
        """
        # Step 1: Load audio
        audio_data, sample_rate = await self.audio_service.load_audio(audio_bytes)
        
        # Step 2: Preprocess
        audio_data = await self.audio_service.preprocess_audio(audio_data, sample_rate)
        
        # Step 3: Extract features (for logging)
        features = await self.audio_service.extract_features(audio_data, sample_rate)
        
        # Step 4: Run all analyses in parallel
        spectral_result = await self.ml_service.analyze_spectral(audio_data, sample_rate)
        prosody_result = await self.ml_service.analyze_prosody(audio_data, sample_rate)
        phase_result = await self.ml_service.analyze_phase(audio_data, sample_rate)
        pattern_result = await self.ml_service.analyze_pattern(audio_data, sample_rate)
        
        # Step 5: Calculate ensemble risk score
        risk_score = self._calculate_risk_score(
            spectral_result["score"],
            prosody_result["score"],
            phase_result["score"],
            pattern_result["score"]
        )
        
        # Step 6: Compile results
        result = {
            "risk_score": risk_score,
            "spectral_score": spectral_result["score"],
            "prosody_score": prosody_result["score"],
            "phase_score": phase_result["score"],
            "pattern_score": pattern_result["score"],
            "duration": len(audio_data) / sample_rate,
            "sample_rate": sample_rate,
            "details": {
                "spectral": {
                    "status": spectral_result["status"],
                    "confidence": spectral_result["confidence"],
                    "details": spectral_result["details"]
                },
                "prosody": {
                    "status": prosody_result["status"],
                    "confidence": prosody_result["confidence"],
                    "details": prosody_result["details"]
                },
                "phase": {
                    "status": phase_result["status"],
                    "confidence": phase_result["confidence"],
                    "details": phase_result["details"]
                },
                "pattern": {
                    "status": pattern_result["status"],
                    "confidence": pattern_result["confidence"],
                    "details": pattern_result["details"]
                }
            },
            "features": features
        }
        
        return result
    
    def _calculate_risk_score(
        self,
        spectral_score: float,
        prosody_score: float,
        phase_score: float,
        pattern_score: float
    ) -> float:
        """
        Calculate weighted ensemble risk score
        
        Args:
            spectral_score: Spectral analysis score (0-100)
            prosody_score: Prosody analysis score (0-100)
            phase_score: Phase analysis score (0-100)
            pattern_score: Pattern analysis score (0-100)
            
        Returns:
            Final risk score (0-100)
        """
        # Weighted average
        weighted_score = (
            spectral_score * self.weights["spectral"] +
            prosody_score * self.weights["prosody"] +
            phase_score * self.weights["phase"] +
            pattern_score * self.weights["pattern"]
        )
        
        # Apply non-linear scaling to emphasize high scores
        # This makes the system more sensitive to clear threats
        if weighted_score > 60:
            # Boost high scores
            weighted_score = 60 + (weighted_score - 60) * 1.2
        
        # Ensure score is within bounds
        risk_score = max(0, min(100, weighted_score))
        
        return round(risk_score, 2)
    
    def get_risk_level(self, risk_score: float) -> str:
        """
        Convert risk score to risk level
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Risk level string
        """
        if risk_score < self.thresholds["safe"]:
            return "safe"
        elif risk_score < self.thresholds["low"]:
            return "low"
        elif risk_score < self.thresholds["medium"]:
            return "medium"
        elif risk_score < self.thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    def get_risk_color(self, risk_level: str) -> str:
        """
        Get color for risk level
        """
        colors = {
            "safe": "#22c55e",      # Green
            "low": "#22c55e",       # Green
            "medium": "#eab308",    # Yellow
            "high": "#f97316",      # Orange
            "critical": "#ef4444"   # Red
        }
        return colors.get(risk_level, "#6b7280")  # Gray default
    
    def get_risk_emoji(self, risk_level: str) -> str:
        """
        Get emoji for risk level
        """
        emojis = {
            "safe": "🟢",
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        return emojis.get(risk_level, "⚪")
    
    def should_alert(self, risk_level: str) -> bool:
        """
        Determine if alert should be sent
        """
        return risk_level in ["high", "critical"]
    
    def get_recommended_action(self, risk_level: str) -> str:
        """
        Get recommended action based on risk level
        """
        actions = {
            "safe": "No action needed. Voice appears genuine.",
            "low": "Voice appears genuine. No immediate concern.",
            "medium": "Caution advised. Consider additional verification.",
            "high": "WARNING: High probability of voice clone. End call and verify through alternative channel.",
            "critical": "CRITICAL: Voice clone detected with high confidence. End call immediately and report."
        }
        return actions.get(risk_level, "Unknown risk level.")
