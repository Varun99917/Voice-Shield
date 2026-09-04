"""
Analysis Result Model
=====================
Database model for voice analysis results
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class RiskLevel(str, enum.Enum):
    """Risk levels for voice analysis"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisResult(Base):
    """
    Analysis Results table
    Stores each voice analysis result
    """
    __tablename__ = "analysis_results"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Analysis Results
    risk_score = Column(Float, nullable=False)  # 0-100%
    risk_level = Column(String(20), nullable=False)  # safe/low/medium/high/critical
    
    # Detailed Analysis Breakdown
    spectral_score = Column(Float, nullable=True)   # Spectral analysis score
    prosody_score = Column(Float, nullable=True)     # Prosody analysis score
    phase_score = Column(Float, nullable=True)       # Phase analysis score
    pattern_score = Column(Float, nullable=True)     # Pattern analysis score
    
    # Analysis Details (JSON for flexibility)
    analysis_details = Column(JSON, nullable=True)
    
    # Audio Metadata
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    sample_rate = Column(Integer, nullable=True)
    audio_format = Column(String(10), nullable=True)
    
    # Location (optional)
    location_city = Column(String(100), nullable=True)
    location_country = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Call Context (optional)
    caller_number = Column(String(20), nullable=True)
    call_duration = Column(Float, nullable=True)
    call_platform = Column(String(50), nullable=True)  # voip/mobile/web
    
    # Model Info
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)  # Time taken for analysis
    
    # Status
    is_alert_sent = Column(String(10), default="no", nullable=False)  # no/yes/escalated
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - ONLY user relationship, no alert relationship
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, risk={self.risk_score}%, level={self.risk_level})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "spectral_score": self.spectral_score,
            "prosody_score": self.prosody_score,
            "phase_score": self.phase_score,
            "pattern_score": self.pattern_score,
            "analysis_details": self.analysis_details,
            "audio_duration": self.audio_duration,
            "location_city": self.location_city,
            "caller_number": self.caller_number,
            "processing_time_ms": self.processing_time_ms,
            "is_alert_sent": self.is_alert_sent,
            "created_at": str(self.created_at) if self.created_at else None
        }
    
    @property
    def is_threat(self) -> bool:
        """Check if this analysis indicates a threat"""
        return self.risk_level in ["high", "critical"]
    
    @property 
    def risk_color(self) -> str:
        """Get color for risk level"""
        colors = {
            "safe": "green",
            "low": "green",
            "medium": "yellow",
            "high": "orange",
            "critical": "red"
        }
        return colors.get(self.risk_level, "gray")
