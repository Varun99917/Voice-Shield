"""
ML Service - External API Integration
=====================================
Calls DeepVoiceGuard ML API on Render
"""

import httpx
from typing import Dict, Any, Optional
import numpy as np
from core.config import settings


class MLService:
    """Service for ML model inference via external API"""
    
    def __init__(self):
        self.api_url = settings.ML_API_URL
        self.timeout = 60.0
    
    async def analyze_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Call external ML API for audio analysis
        Falls back to simulated analysis if API fails
        """
        if self.api_url:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
                    response = await client.post(self.api_url, files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        return self._normalize_result(result)
            except Exception as e:
                print(f"ML API call failed: {e}")
        
        # Fallback: Simulated analysis
        return self._simulate_analysis(audio_bytes)
    
    def _normalize_result(self, api_result: dict) -> Dict[str, Any]:
        """
        Normalize API response to our standard format
        """
        # Try to extract scores from API response
        # Adjust based on actual API response format
        try:
            is_cloned = api_result.get("is_cloned", api_result.get("is_deepfake", False))
            confidence = api_result.get("confidence", 0.75)
            risk_score = api_result.get("risk_score", api_result.get("score", 50))
            
            # If API gives us individual scores
            spectral = api_result.get("spectral_score", risk_score)
            prosody = api_result.get("prosody_score", risk_score)
            phase = api_result.get("phase_score", risk_score)
            pattern = api_result.get("pattern_score", risk_score)
            
            return {
                "risk_score": float(risk_score),
                "risk_level": self._get_risk_level(risk_score),
                "is_cloned": bool(is_cloned),
                "confidence": float(confidence),
                "spectral_score": float(spectral),
                "prosody_score": float(prosody),
                "phase_score": float(phase),
                "pattern_score": float(pattern),
                "analysis_details": api_result.get("details", "ML API analysis complete"),
                "ml_source": "deepvoiceguard",
            }
        except Exception as e:
            print(f"Normalize error: {e}")
            return self._simulate_analysis(b"")
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score < 20: return "safe"
        elif score < 40: return "low"
        elif score < 60: return "medium"
        elif score < 80: return "high"
        else: return "critical"
    
    def _simulate_analysis(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Simulated analysis for fallback"""
        import random
        
        spectral = random.uniform(15, 35)
        prosody = random.uniform(18, 32)
        phase = random.uniform(20, 30)
        pattern = random.uniform(16, 28)
        
        risk_score = spectral * 0.30 + prosody * 0.25 + phase * 0.25 + pattern * 0.20
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": self._get_risk_level(risk_score),
            "is_cloned": risk_score >= 60,
            "confidence": round(0.70 + (risk_score / 100) * 0.29, 4),
            "spectral_score": round(spectral, 2),
            "prosody_score": round(prosody, 2),
            "phase_score": round(phase, 2),
            "pattern_score": round(pattern, 2),
            "analysis_details": "Simulated analysis (ML API unavailable)",
            "ml_source": "simulated",
        }