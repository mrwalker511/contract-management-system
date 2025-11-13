"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user, check_user_role, get_password_hash
from ..models.user import User, UserRole
from ..schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_user_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Users can only view their own profile unless they're admin
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user by ID

    Args:
        user_id: User ID
        user_data: Updated user data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user data

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Users can only update their own profile unless they're admin
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields
    update_data = user_data.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    # Only admin can change role and is_active
    if current_user.role != UserRole.ADMIN:
        update_data.pop("role", None)
        update_data.pop("is_active", None)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(check_user_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Delete user by ID (admin only)

    Args:
        user_id: User ID
        current_user: Current authenticated admin user
        db: Database session

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return None
