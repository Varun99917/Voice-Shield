"""
SatyVaani Backend
=================
AI-Powered Voice Clone Detection System

Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from core.config import settings
from core.database import init_db, close_db


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Startup and shutdown
    """
    # Startup
    print("=" * 50)
    print(f"🛡️  {settings.APP_NAME} v{settings.APP_VERSION}")
    print("🚀 Starting server...")
    print("=" * 50)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Create default admin user
    await create_default_admin()
    print("✅ Default admin user created")
    
    print("=" * 50)
    print(f"🌐 Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API docs at http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await close_db()


# ==================== CREATE APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== CORS MIDDLEWARE ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== IMPORT ROUTERS ====================

from api.auth import router as auth_router
from api.analysis import router as analysis_router
from api.dashboard import router as dashboard_router
from api.alerts import router as alerts_router
from api.websocket import router as websocket_router


# ==================== REGISTER ROUTERS ====================

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(websocket_router)


# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """
    Root endpoint - API info
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/info")
async def api_info():
    """
    API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth": "/api/auth",
            "analysis": "/api/analysis",
            "dashboard": "/api/dashboard",
            "alerts": "/api/alerts",
            "websocket": "/ws"
        }
    }


# ==================== HELPER FUNCTIONS ====================

async def create_default_admin():
    """Create default admin user if not exists"""
    from core.database import async_session_maker
    from core.security import get_password_hash
    from models.user import User
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == "admin@satyavani.com")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            # Create admin
            admin = User(
                email="admin@satyavani.com",
                full_name="Admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
                is_verified=True
            )
            session.add(admin)
            await session.commit()
            print("✅ Default admin created: admin@satyavani.com / admin123")


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
