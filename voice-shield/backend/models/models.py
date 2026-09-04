"""
Voice Shield Models
=================
Database models for User, Analysis, and Alert
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    organization = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "role": self.role.value if self.role else "user",
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "organization": self.organization,
            "department": self.department,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class Analysis(Base):
    """Analysis result model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    audio_filename = Column(String(255), nullable=True)
    
    # Overall risk assessment
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    
    # Individual scores
    spectral_score = Column(Float, nullable=True)
    prosody_score = Column(Float, nullable=True)
    phase_score = Column(Float, nullable=True)
    pattern_score = Column(Float, nullable=True)
    
    # Analysis details
    is_cloned = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    analysis_details = Column(Text, nullable=True)
    
    # ML source
    ml_source = Column(String(50), default="simulated")  # "colab", "simulated"
    ml_endpoint = Column(String(255), nullable=True)
    
    # Metadata
    audio_duration = Column(Float, nullable=True)  # seconds
    sample_rate = Column(Integer, nullable=True)
    is_alert_sent = Column(String(10), default="false")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "audio_filename": self.audio_filename,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value if self.risk_level else "safe",
            "spectral_score": self.spectral_score,
            "prosody_score": self.prosody_score,
            "phase_score": self.phase_score,
            "pattern_score": self.pattern_score,
            "is_cloned": self.is_cloned,
            "confidence": self.confidence,
            "analysis_details": self.analysis_details,
            "ml_source": self.ml_source,
            "audio_duration": self.audio_duration,
            "is_alert_sent": self.is_alert_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    analysis_id = Column(Integer, nullable=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # "cloned_voice", "high_risk", "suspicious"
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    status = Column(String(20), default="unread")  # "unread", "read", "resolved"
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "alert_type": self.alert_type,
            "severity": self.severity.value if self.severity else "low",
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
