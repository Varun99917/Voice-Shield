"""
WebSocket API
=============
Real-time communication endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set
import json
import asyncio
import base64
from datetime import datetime

from core.security import decode_token
from services.risk_engine import RiskEngine

router = APIRouter(tags=["WebSocket"])

# Initialize risk engine
risk_engine = RiskEngine()


# ==================== CONNECTION MANAGER ====================

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # user_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.admin_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        """Accept and store connection"""
        await websocket.accept()
        
        if is_admin:
            self.admin_connections.add(websocket)
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        """Remove connection"""
        if is_admin and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
        
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        print(f"User {user_id} disconnected")
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def broadcast_to_admins(self, message: dict):
        """Send message to all admin connections"""
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def broadcast_alert(self, alert: dict):
        """Broadcast alert to admins"""
        await self.broadcast_to_admins({
            "type": "new_alert",
            "data": alert
        })


# Create manager instance
manager = ConnectionManager()


# ==================== WEBSOCKET ENDPOINTS ====================

@router.websocket("/ws/analysis/{token}")
async def websocket_analysis(websocket: WebSocket, token: str):
    """
    WebSocket for real-time audio analysis
    
    Client sends audio chunks, server responds with analysis results
    """
    # Authenticate user
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Accept connection
    await manager.connect(websocket, user_id, is_admin=False)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to SatyVaani analysis engine",
            "user_id": user_id
        })
        
        while True:
            # Receive audio chunk
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "audio_chunk":
                # Process audio chunk
                audio_data = message.get("data")  # Base64 encoded audio
                metadata = message.get("metadata", {})
                
                # Analyze audio
                try:
                    audio_bytes = base64.b64decode(audio_data)
                    result = await risk_engine.analyze_audio(audio_bytes)
                    
                    # Send result back
                    await websocket.send_json({
                        "type": "analysis_result",
                        "data": {
                            "risk_score": result["risk_score"],
                            "risk_level": risk_engine.get_risk_level(result["risk_score"]),
                            "spectral_score": result.get("spectral_score"),
                            "prosody_score": result.get("prosody_score"),
                            "phase_score": result.get("phase_score"),
                            "pattern_score": result.get("pattern_score"),
                            "details": result.get("details"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    })
                    
                    # If high risk, notify admins
                    risk_level = risk_engine.get_risk_level(result["risk_score"])
                    if risk_level in ["high", "critical"]:
                        await manager.broadcast_to_admins({
                            "type": "realtime_threat",
                            "data": {
                                "user_id": user_id,
                                "risk_score": result["risk_score"],
                                "risk_level": risk_level,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        })
                
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Analysis failed: {str(e)}"
                    })
            
            elif message.get("type") == "ping":
                # Keep-alive response
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, is_admin=False)
        print(f"User {user_id} disconnected from analysis WebSocket")


@router.websocket("/ws/admin/{token}")
async def websocket_admin(websocket: WebSocket, token: str):
    """
    WebSocket for admin real-time monitoring
    """
    # Authenticate admin
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Accept connection
    await manager.connect(websocket, user_id, is_admin=True)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to admin monitoring",
            "admin_id": user_id
        })
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, is_admin=True)
        print(f"Admin {user_id} disconnected")


# ==================== HELPER FUNCTIONS ====================

async def send_alert_to_user(user_id: int, alert: dict):
    """Send alert to specific user via WebSocket"""
    await manager.send_to_user(user_id, {
        "type": "alert",
        "data": alert
    })


async def broadcast_threat_detected(user_id: int, risk_score: float, risk_level: str):
    """Broadcast threat detection to admins"""
    await manager.broadcast_to_admins({
        "type": "threat_detected",
        "data": {
            "user_id": user_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat()
        }
    })
