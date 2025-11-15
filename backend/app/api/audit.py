"""
Audit log endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, role_checker
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[int] = Query(None, description="Filter by resource ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get audit logs with optional filtering.
    Only accessible by admin and legal users.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **user_id**: Filter by user ID
    - **action**: Filter by action type (CREATE, UPDATE, DELETE, etc.)
    - **resource_type**: Filter by resource type (contract, user, template, etc.)
    - **resource_id**: Filter by specific resource ID
    """
    # Only admin and legal users can view audit logs
    if current_user.role not in ["admin", "legal"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view audit logs"
        )

    logs = AuditService.get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    return logs


@router.get("/logs/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get audit logs for a specific user.
    Users can view their own logs, admin and legal can view all.

    - **user_id**: User ID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Check permissions
    if current_user.role not in ["admin", "legal"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view these audit logs"
        )

    logs = AuditService.get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
    )

    return logs


@router.get("/logs/contract/{contract_id}", response_model=List[AuditLogResponse])
def get_contract_audit_logs(
    contract_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get audit logs for a specific contract.

    - **contract_id**: Contract ID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Verify user has access to the contract
    from app.models.contract import Contract
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check permissions
    if (
        current_user.role not in ["admin", "legal", "finance"]
        and contract.created_by_id != current_user.id
        and contract.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view audit logs for this contract"
        )

    logs = AuditService.get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        resource_type="contract",
        resource_id=contract_id,
    )

    return logs
