"""
Voice Shield Auth API
====================
Authentication and User Management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from core.database import async_session_maker
from core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user
)
from models.models import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ==================== REQUEST/RESPONSE MODELS ====================

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone_number: str = None
    organization: str = None
    department: str = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    organization: str = None
    department: str = None


# ==================== AUTH ENDPOINTS ====================

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    async with async_session_maker() as session:
        # Check if email already exists
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            email=request.email,
            full_name=request.full_name,
            phone_number=request.phone_number,
            hashed_password=get_password_hash(request.password),
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            organization=request.organization,
            department=request.department
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=user.to_dict()
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user and return JWT token"""
    async with async_session_maker() as session:
        # Find user by email
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        await session.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=user.to_dict()
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == current_user["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user.to_dict()


@router.put("/me", response_model=UserResponse)
async def update_me(
    full_name: str = None,
    phone_number: str = None,
    organization: str = None,
    department: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == current_user["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone_number = phone_number
        if organization:
            user.organization = organization
        if department:
            user.department = department
        
        await session.commit()
        await session.refresh(user)
        
        return user.to_dict()


@router.get("/users", response_model=list)
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [user.to_dict() for user in users]
