"""
Pydantic schemas for User model
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from ..models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user (all fields optional)"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
