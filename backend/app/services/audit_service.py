"""
Audit logging service for tracking all system actions.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    """Service for creating and managing audit logs."""

    @staticmethod
    async def log_action(
        db: Session,
        action: str,
        resource_type: str,
        description: str,
        user: Optional[User] = None,
        resource_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            db: Database session
            action: Action performed (CREATE, UPDATE, DELETE, LOGIN, etc.)
            resource_type: Type of resource (contract, user, template, etc.)
            description: Human-readable description of the action
            user: User who performed the action
            resource_id: ID of the affected resource
            changes: Dictionary of changes (before/after values)
            request: FastAPI request object for IP and user agent

        Returns:
            Created AuditLog instance
        """
        # Extract IP address and user agent from request
        ip_address = None
        user_agent = None
        if request:
            # Get real IP from X-Forwarded-For header if behind proxy
            ip_address = request.headers.get("X-Forwarded-For")
            if ip_address:
                # Take first IP if multiple proxies
                ip_address = ip_address.split(",")[0].strip()
            else:
                ip_address = request.client.host if request.client else None

            user_agent = request.headers.get("User-Agent")
            if user_agent and len(user_agent) > 255:
                user_agent = user_agent[:255]

        # Create audit log entry
        audit_log = AuditLog(
            user_id=user.id if user else None,
            action=action.upper(),
            resource_type=resource_type.lower(),
            resource_id=resource_id,
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_audit_logs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
    ) -> list[AuditLog]:
        """
        Retrieve audit logs with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID

        Returns:
            List of AuditLog instances
        """
        query = db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action.upper())
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type.lower())
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)

        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_change_diff(
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        exclude_fields: Optional[set[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create a dictionary of changes between old and new data.

        Args:
            old_data: Previous state
            new_data: New state
            exclude_fields: Fields to exclude from diff (e.g., 'updated_at')

        Returns:
            Dictionary with format: {field: {"old": old_value, "new": new_value}}
        """
        if exclude_fields is None:
            exclude_fields = {"updated_at", "hashed_password"}

        changes = {}

        # Check for modified and new fields
        for key, new_value in new_data.items():
            if key in exclude_fields:
                continue

            old_value = old_data.get(key)

            # Skip if values are the same
            if old_value == new_value:
                continue

            # Convert datetime objects to ISO strings for JSON serialization
            if isinstance(old_value, datetime):
                old_value = old_value.isoformat()
            if isinstance(new_value, datetime):
                new_value = new_value.isoformat()

            changes[key] = {
                "old": old_value,
                "new": new_value,
            }

        # Check for deleted fields
        for key in old_data:
            if key in exclude_fields:
                continue
            if key not in new_data:
                old_value = old_data[key]
                if isinstance(old_value, datetime):
                    old_value = old_value.isoformat()
                changes[key] = {
                    "old": old_value,
                    "new": None,
                }

        return changes


# Convenience functions for common audit actions
async def log_login(db: Session, user: User, request: Request, success: bool = True) -> AuditLog:
    """Log a login attempt."""
    action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    description = f"User {user.email} logged in" if success else f"Failed login attempt for {user.email}"
    return await AuditService.log_action(
        db=db,
        action=action,
        resource_type="user",
        resource_id=user.id if success else None,
        description=description,
        user=user if success else None,
        request=request,
    )


async def log_logout(db: Session, user: User, request: Request) -> AuditLog:
    """Log a logout action."""
    return await AuditService.log_action(
        db=db,
        action="LOGOUT",
        resource_type="user",
        resource_id=user.id,
        description=f"User {user.email} logged out",
        user=user,
        request=request,
    )


async def log_create(
    db: Session,
    user: User,
    resource_type: str,
    resource_id: int,
    description: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource creation."""
    return await AuditService.log_action(
        db=db,
        action="CREATE",
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        user=user,
        request=request,
    )


async def log_update(
    db: Session,
    user: User,
    resource_type: str,
    resource_id: int,
    description: str,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource update."""
    return await AuditService.log_action(
        db=db,
        action="UPDATE",
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        changes=changes,
        user=user,
        request=request,
    )


async def log_delete(
    db: Session,
    user: User,
    resource_type: str,
    resource_id: int,
    description: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource deletion."""
    return await AuditService.log_action(
        db=db,
        action="DELETE",
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        user=user,
        request=request,
    )
