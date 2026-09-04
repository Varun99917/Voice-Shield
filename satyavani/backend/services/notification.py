"""
Notification Service
====================
Handle alerts and notifications
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.alert import Alert, AlertType, AlertPriority, AlertStatus
from models.analysis import AnalysisResult


class NotificationService:
    """
    Service for creating and sending notifications
    """
    
    def __init__(self):
        """Initialize notification service"""
        pass
    
    async def create_threat_alert(
        self,
        db: AsyncSession,
        user,
        analysis: AnalysisResult
    ) -> Alert:
        """
        Create alert when threat is detected
        
        Args:
            db: Database session
            user: User who triggered the alert
            analysis: Analysis result
            
        Returns:
            Created alert
        """
        # Determine alert type and priority
        risk_level = analysis.risk_level
        risk_score = analysis.risk_score
        
        # Alert type based on analysis details
        alert_type = AlertType.VOICE_CLONE
        if analysis.analysis_details:
            if analysis.analysis_details.get("pattern", {}).get("status") == "tts":
                alert_type = AlertType.TTS_DETECTED
            elif analysis.analysis_details.get("prosody", {}).get("status") == "robotic":
                alert_type = AlertType.VOICE_CLONE
        
        # Priority based on risk score
        if risk_score >= 80:
            priority = AlertPriority.CRITICAL
        elif risk_score >= 60:
            priority = AlertPriority.HIGH
        elif risk_score >= 40:
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW
        
        # Create title and message
        title = self._get_alert_title(alert_type, risk_level)
        message = self._get_alert_message(user.full_name, risk_score, alert_type)
        details = self._get_alert_details(analysis)
        
        # Create alert
        alert = Alert(
            user_id=user.id,
            alert_type=alert_type,
            priority=priority,
            status=AlertStatus.PENDING,
            title=title,
            message=message,
            details=details,
            analysis_id=analysis.id,
            risk_score=int(risk_score)
        )
        
        db.add(alert)
        await db.flush()  # Get alert ID
        
        # Link alert to analysis
        analysis.alert_id = alert.id
        analysis.is_alert_sent = "yes"
        
        # Send notifications
        await self._send_notifications(user, alert)
        
        return alert
    
    async def _send_notifications(self, user, alert: Alert):
        """
        Send notifications through various channels
        """
        # TODO: Implement actual notification sending
        
        # Email notification
        if user.email:
            await self._send_email(user.email, alert)
            alert.email_sent = True
        
        # SMS notification
        if user.phone_number:
            await self._send_sms(user.phone_number, alert)
            alert.sms_sent = True
        
        # Push notification (would use Firebase)
        await self._send_push_notification(user.id, alert)
        alert.push_sent = True
    
    async def _send_email(self, email: str, alert: Alert):
        """
        Send email notification
        """
        # TODO: Implement with SMTP or SendGrid
        print(f"📧 Email notification sent to {email}")
        print(f"   Subject: {alert.title}")
        print(f"   Priority: {alert.priority}")
    
    async def _send_sms(self, phone: str, alert: Alert):
        """
        Send SMS notification
        """
        # TODO: Implement with Twilio or MSG91
        print(f"📱 SMS notification sent to {phone}")
        print(f"   Message: {alert.message[:100]}...")
    
    async def _send_push_notification(self, user_id: int, alert: Alert):
        """
        Send push notification
        """
        # TODO: Implement with Firebase Cloud Messaging
        print(f"🔔 Push notification sent to user {user_id}")
    
    def _get_alert_title(self, alert_type: AlertType, risk_level: str) -> str:
        """
        Generate alert title
        """
        titles = {
            AlertType.VOICE_CLONE: "🚨 Voice Clone Detected!",
            AlertType.TTS_DETECTED: "🚨 AI-Generated Voice Detected!",
            AlertType.AUDIO_REPLAY: "⚠️ Possible Audio Replay!",
            AlertType.SUSPICIOUS: "⚠️ Suspicious Activity",
            AlertType.OTHER: "⚠️ Alert"
        }
        return titles.get(alert_type, "⚠️ Alert")
    
    def _get_alert_message(self, user_name: str, risk_score: float, alert_type: AlertType) -> str:
        """
        Generate alert message
        """
        return (
            f"High-risk voice activity detected for {user_name}. "
            f"Risk score: {risk_score:.1f}%. "
            f"Type: {alert_type.value}. "
            f"Please verify through alternative channel."
        )
    
    def _get_alert_details(self, analysis: AnalysisResult) -> str:
        """
        Generate detailed alert information
        """
        details = []
        
        if analysis.analysis_details:
            for key, value in analysis.analysis_details.items():
                if isinstance(value, dict):
                    details.append(f"{key}: {value.get('status', 'unknown')}")
        
        return " | ".join(details) if details else "No additional details"
