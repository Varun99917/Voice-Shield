"""
Authentication API
==================
Login, Register, Profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from core.database import get_db
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ==================== SCHEMAS ====================

class UserRegister(BaseModel):
    """User registration schema"""
    email: str
    password: str
    full_name: str
    phone_number: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User's email address
    - **password**: Password (min 6 characters)
    - **full_name**: Full name
    - **phone_number**: Phone number (optional)
    - **organization**: Organization name (optional)
    - **department**: Department name (optional)
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        organization=user_data.organization,
        department=user_data.department,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_verified=False,
        role="user"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=new_user.to_dict()
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password
    
    - **email**: Registered email
    - **password**: Account password
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=user.to_dict()
    )


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile
    Requires authentication
    """
    return current_user.to_dict()


@router.put("/profile")
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile
    """
    # Update fields if provided
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.phone_number is not None:
        current_user.phone_number = user_data.phone_number
    if user_data.organization is not None:
        current_user.organization = user_data.organization
    if user_data.department is not None:
        current_user.department = user_data.department
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user.to_dict()


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password updated successfully"}


# ==================== ADMIN ENDPOINTS ====================

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [user.to_dict() for user in users]
