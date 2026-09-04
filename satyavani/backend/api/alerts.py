"""
Alerts API
==========
Alert management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func, and_, update
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from core.security import get_current_user, get_admin_user
from models.user import User
from models.alert import Alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


# ==================== SCHEMAS ====================

class AlertUpdate(BaseModel):
    """Update alert status"""
    status: str
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class AlertResponse(BaseModel):
    """Alert response"""
    id: int
    alert_type: str
    priority: str
    status: str
    title: str
    message: str
    risk_score: Optional[int]
    created_at: str


# ==================== ENDPOINTS ====================

@router.get("/")
async def get_my_alerts(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's alerts
    """
    result = await db.execute(
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    alerts = result.scalars().all()
    
    return [alert.to_dict() for alert in alerts]


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of unread alerts
    """
    count = await db.scalar(
        select(sql_func.count(Alert.id)).where(
            and_(
                Alert.user_id == current_user.id,
                Alert.status == "pending"
            )
        )
    )
    
    return {"unread_count": count or 0}


@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Acknowledge an alert
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Alert acknowledged", "alert": alert.to_dict()}


@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve an alert
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    if notes:
        alert.notes = notes
    await db.commit()
    
    return {"message": "Alert resolved", "alert": alert.to_dict()}


# ==================== ADMIN ENDPOINTS ====================

@router.get("/all")
async def get_all_alerts(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all alerts (admin only)
    """
    query = select(Alert)
    
    if priority:
        query = query.where(Alert.priority == priority)
    
    if status_filter:
        query = query.where(Alert.status == status_filter)
    
    query = query.order_by(Alert.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    # Get total count
    count_query = select(sql_func.count(Alert.id))
    if priority:
        count_query = count_query.where(Alert.priority == priority)
    if status_filter:
        count_query = count_query.where(Alert.status == status_filter)
    
    total = await db.scalar(count_query)
    
    return {
        "total": total,
        "alerts": [alert.to_dict() for alert in alerts]
    }


@router.put("/{alert_id}/update")
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update alert (admin only)
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = alert_data.status
    if alert_data.notes:
        alert.notes = alert_data.notes
    if alert_data.assigned_to:
        alert.assigned_to = alert_data.assigned_to
    
    if alert_data.status == "resolved":
        alert.resolved_at = datetime.utcnow()
    elif alert_data.status == "acknowledged":
        alert.acknowledged_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert)
    
    return alert.to_dict()


@router.get("/stats")
async def get_alert_stats(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert statistics
    """
    total = await db.scalar(select(sql_func.count(Alert.id))) or 0
    
    pending = await db.scalar(
        select(sql_func.count(Alert.id)).where(Alert.status == "pending")
    ) or 0
    
    acknowledged = await db.scalar(
        select(sql_func.count(Alert.id)).where(Alert.status == "acknowledged")
    ) or 0
    
    resolved = await db.scalar(
        select(sql_func.count(Alert.id)).where(Alert.status == "resolved")
    ) or 0
    
    critical = await db.scalar(
        select(sql_func.count(Alert.id)).where(Alert.priority == "critical")
    ) or 0
    
    high = await db.scalar(
        select(sql_func.count(Alert.id)).where(Alert.priority == "high")
    ) or 0
    
    return {
        "total": total,
        "pending": pending,
        "acknowledged": acknowledged,
        "resolved": resolved,
        "critical": critical,
        "high": high
    }
