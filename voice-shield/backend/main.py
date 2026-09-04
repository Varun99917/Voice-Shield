"""
Voice Shield Backend
====================
AI-Powered Voice Clone Detection System

Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from core.config import settings
from core.database import init_db, close_db

# Import routers
from api.auth import router as auth_router
from api.analysis import router as analysis_router


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    print("=" * 60)
    print("🛡️  VOICE SHIELD - AI Voice Clone Detection")
    print("=" * 60)
    print(f"📦 Version: {settings.APP_VERSION}")
    print("🚀 Starting server...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Create default admin
    await create_default_admin()
    
    print("=" * 60)
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    
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
    docs_url="/docs"
)


# ==================== CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== REGISTER ROUTERS ====================

app.include_router(auth_router)
app.include_router(analysis_router)


# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ==================== HELPER FUNCTIONS ====================

async def create_default_admin():
    """Create default admin user if not exists"""
    from core.database import async_session_maker
    from core.security import get_password_hash
    from models.models import User, UserRole
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@voiceshield.com")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email="admin@voiceshield.com",
                full_name="Admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            session.add(admin)
            await session.commit()
            print("✅ Admin created: admin@voiceshield.com / admin123")


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
