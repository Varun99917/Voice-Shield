"""
Analysis API
============
Voice analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.analysis import AnalysisResult, RiskLevel
from services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

# Initialize risk engine
risk_engine = RiskEngine()


# ==================== SCHEMAS ====================

class AudioAnalysisRequest(BaseModel):
    """Request for analyzing audio"""
    audio_base64: Optional[str] = None  # For real-time WebSocket
    caller_number: Optional[str] = None
    call_platform: Optional[str] = None  # voip/mobile/web
    location_city: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response from audio analysis"""
    id: int
    risk_score: float
    risk_level: str
    spectral_score: Optional[float]
    prosody_score: Optional[float]
    phase_score: Optional[float]
    pattern_score: Optional[float]
    analysis_details: Optional[dict]
    processing_time_ms: float
    created_at: str


class AnalysisHistory(BaseModel):
    """Analysis history response"""
    total: int
    analyses: List[dict]


# ==================== ENDPOINTS ====================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    caller_number: Optional[str] = None,
    call_platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze uploaded audio file for voice cloning detection
    
    - **file**: Audio file (WAV, MP3, FLAC)
    - **caller_number**: Optional caller phone number
    - **call_platform**: Platform (voip/mobile/web)
    """
    import time
    import base64
    import io
    
    start_time = time.time()
    
    # Validate file type
    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/flac", "audio/ogg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Run analysis
    try:
        analysis_result = await risk_engine.analyze_audio(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Determine risk level
    risk_score = analysis_result["risk_score"]
    risk_level = risk_engine.get_risk_level(risk_score)
    
    # Save to database
    db_result = AnalysisResult(
        user_id=current_user.id,
        risk_score=risk_score,
        risk_level=risk_level,
        spectral_score=analysis_result.get("spectral_score"),
        prosody_score=analysis_result.get("prosody_score"),
        phase_score=analysis_result.get("phase_score"),
        pattern_score=analysis_result.get("pattern_score"),
        analysis_details=analysis_result.get("details"),
        audio_duration=analysis_result.get("duration"),
        sample_rate=analysis_result.get("sample_rate"),
        caller_number=caller_number,
        call_platform=call_platform,
        processing_time_ms=processing_time,
        model_version="1.0.0"
    )
    
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)
    
    # Create alert if threat detected
    if risk_level in ["high", "critical"]:
        from services.notification import NotificationService
        notification_service = NotificationService()
        await notification_service.create_threat_alert(
            db=db,
            user=current_user,
            analysis=db_result
        )
    
    return AnalysisResponse(
        id=db_result.id,
        risk_score=risk_score,
        risk_level=risk_level,
        spectral_score=analysis_result.get("spectral_score"),
        prosody_score=analysis_result.get("prosody_score"),
        phase_score=analysis_result.get("phase_score"),
        pattern_score=analysis_result.get("pattern_score"),
        analysis_details=analysis_result.get("details"),
        processing_time_ms=processing_time,
        created_at=str(db_result.created_at)
    )


@router.get("/history", response_model=AnalysisHistory)
async def get_analysis_history(
    limit: int = 20,
    offset: int = 0,
    risk_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's analysis history
    
    - **limit**: Number of results to return (default 20)
    - **offset**: Pagination offset
    - **risk_level**: Filter by risk level (safe/low/medium/high/critical)
    """
    query = select(AnalysisResult).where(AnalysisResult.user_id == current_user.id)
    
    if risk_level:
        query = query.where(AnalysisResult.risk_level == risk_level)
    
    query = query.order_by(AnalysisResult.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    analyses = result.scalars().all()
    
    # Get total count
    count_query = select(sql_func.count(AnalysisResult.id)).where(
        AnalysisResult.user_id == current_user.id
    )
    total = await db.scalar(count_query)
    
    return AnalysisHistory(
        total=total,
        analyses=[a.to_dict() for a in analyses]
    )


@router.get("/recent")
async def get_recent_analyses(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent analyses for home screen
    """
    result = await db.execute(
        select(AnalysisResult)
        .where(AnalysisResult.user_id == current_user.id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
    )
    analyses = result.scalars().all()
    
    return [a.to_dict() for a in analyses]


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's analysis statistics
    """
    # Total analyses
    total = await db.scalar(
        select(sql_func.count(AnalysisResult.id))
        .where(AnalysisResult.user_id == current_user.id)
    )
    
    # Today's analyses
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await db.scalar(
        select(sql_func.count(AnalysisResult.id))
        .where(
            AnalysisResult.user_id == current_user.id,
            AnalysisResult.created_at >= today_start
        )
    )
    
    # Threats detected
    threats = await db.scalar(
        select(sql_func.count(AnalysisResult.id))
        .where(
            AnalysisResult.user_id == current_user.id,
            AnalysisResult.risk_level.in_(["high", "critical"])
        )
    )
    
    # Average risk score
    avg_risk = await db.scalar(
        select(sql_func.avg(AnalysisResult.risk_score))
        .where(AnalysisResult.user_id == current_user.id)
    )
    
    return {
        "total_analyses": total or 0,
        "today_analyses": today_count or 0,
        "threats_detected": threats or 0,
        "average_risk_score": round(avg_risk or 0, 2)
    }


@router.get("/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analysis result by ID
    """
    result = await db.execute(
        select(AnalysisResult).where(
            AnalysisResult.id == analysis_id,
            AnalysisResult.user_id == current_user.id
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis.to_dict()
