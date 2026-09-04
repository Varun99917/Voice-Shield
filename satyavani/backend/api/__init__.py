"""
API Package
===========
FastAPI endpoints for SatyVaani
"""

from .auth import router as auth_router
from .analysis import router as analysis_router
from .dashboard import router as dashboard_router
from .alerts import router as alerts_router
from .websocket import router as websocket_router

__all__ = [
    "auth_router",
    "analysis_router", 
    "dashboard_router",
    "alerts_router",
    "websocket_router"
]
