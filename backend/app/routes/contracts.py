"""
Contract management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, UserRole
from ..models.contract import Contract, ContractStatus
from ..schemas.contract import ContractCreate, ContractUpdate, ContractResponse

router = APIRouter(prefix="/contracts", tags=["contracts"])


def generate_contract_number() -> str:
    """Generate unique contract number"""
    return f"CT-{uuid.uuid4().hex[:8].upper()}"


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new contract

    Args:
        contract_data: Contract creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created contract data
    """
    # Generate contract number if not provided
    contract_number = contract_data.contract_number or generate_contract_number()

    db_contract = Contract(
        **contract_data.model_dump(exclude={"contract_number"}),
        contract_number=contract_number,
        owner_id=current_user.id
    )

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


@router.get("/", response_model=List[ContractResponse])
async def list_contracts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ContractStatus] = Query(None, description="Filter by status"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List contracts with optional filters

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status filter
        owner_id: Optional owner ID filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of contracts

    Notes:
        - Non-admin users can only see their own contracts
        - Admins can see all contracts
    """
    query = db.query(Contract)

    # Non-admin users can only see their own contracts
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Contract.owner_id == current_user.id)
    elif owner_id:
        # Admin can filter by owner_id
        query = query.filter(Contract.owner_id == owner_id)

    # Apply status filter
    if status:
        query = query.filter(Contract.status == status)

    contracts = query.offset(skip).limit(limit).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get contract by ID

    Args:
        contract_id: Contract ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Contract data

    Raises:
        HTTPException: If contract not found or unauthorized
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check authorization: user must own the contract or be admin
    if contract.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this contract"
        )

    return contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update contract by ID

    Args:
        contract_id: Contract ID
        contract_data: Updated contract data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated contract data

    Raises:
        HTTPException: If contract not found or unauthorized
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check authorization
    if contract.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this contract"
        )

    # Update contract fields
    update_data = contract_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)

    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete contract by ID

    Args:
        contract_id: Contract ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If contract not found or unauthorized
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check authorization
    if contract.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this contract"
        )

    db.delete(contract)
    db.commit()

    return None
