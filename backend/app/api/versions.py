"""
Contract version history endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contract import Contract
from app.schemas.contract_version import (
    ContractVersionResponse,
    VersionComparisonResponse
)
from app.services.version_service import VersionService
from app.services.audit_service import log_update

router = APIRouter(prefix="/versions", tags=["versions"])


@router.get("/contract/{contract_id}", response_model=List[ContractVersionResponse])
def get_contract_versions(
    contract_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all versions of a contract.

    - **contract_id**: Contract ID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Verify contract exists
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
            detail="Not enough permissions to view versions for this contract"
        )

    versions = VersionService.get_contract_versions(
        db=db,
        contract_id=contract_id,
        skip=skip,
        limit=limit,
    )

    return versions


@router.get(
    "/contract/{contract_id}/version/{version_number}",
    response_model=ContractVersionResponse
)
def get_version_by_number(
    contract_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific version of a contract.

    - **contract_id**: Contract ID
    - **version_number**: Version number to retrieve
    """
    # Verify contract exists
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
            detail="Not enough permissions to view this version"
        )

    version = VersionService.get_version_by_number(
        db=db,
        contract_id=contract_id,
        version_number=version_number,
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found"
        )

    return version


@router.get(
    "/contract/{contract_id}/compare/{version_1}/{version_2}",
    response_model=VersionComparisonResponse
)
def compare_versions(
    contract_id: int,
    version_1: int,
    version_2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compare two versions of a contract.

    - **contract_id**: Contract ID
    - **version_1**: First version number
    - **version_2**: Second version number
    """
    # Verify contract exists
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
            detail="Not enough permissions to compare versions"
        )

    differences = VersionService.compare_versions(
        db=db,
        contract_id=contract_id,
        version_1=version_1,
        version_2=version_2,
    )

    return VersionComparisonResponse(
        contract_id=contract_id,
        version_1=version_1,
        version_2=version_2,
        differences=differences,
    )


@router.post(
    "/contract/{contract_id}/restore/{version_number}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def restore_version(
    contract_id: int,
    version_number: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Restore a contract to a previous version.

    - **contract_id**: Contract ID
    - **version_number**: Version number to restore to
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check permissions (only admin, legal, or creator can restore)
    if (
        current_user.role not in ["admin", "legal"]
        and contract.created_by_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to restore this contract"
        )

    # Restore version
    restored_contract = VersionService.restore_version(
        db=db,
        contract=contract,
        version_number=version_number,
        user=current_user,
    )

    if not restored_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found"
        )

    # Log the action
    await log_update(
        db=db,
        user=current_user,
        resource_type="contract",
        resource_id=contract_id,
        description=f"Restored contract to version {version_number}",
        request=request,
    )

    return {
        "message": f"Contract successfully restored to version {version_number}",
        "contract_id": contract_id,
        "version_number": version_number,
    }
