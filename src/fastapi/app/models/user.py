"""
User/Caregiver data models
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    CAREGIVER = "caregiver"
    SUPERVISOR = "supervisor"


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="Full name of the user")
    role: UserRole = Field(default=UserRole.CAREGIVER, description="User role")
    active: bool = Field(default=True, description="Whether user account is active")


class UserCreate(UserBase):
    """Model for creating new users"""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class User(UserBase):
    """Complete user model"""
    user_id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Token(BaseModel):
    """JWT token model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None