"""
Pydantic schemas for Contract model
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..models.contract import ContractStatus


class ContractBase(BaseModel):
    """Base contract schema with common fields"""
    title: str
    description: Optional[str] = None
    content: str
    contract_number: Optional[str] = None
    contract_value: Optional[Decimal] = None
    currency: str = "USD"
    counterparty_name: str
    counterparty_contact: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ContractCreate(ContractBase):
    """Schema for creating a new contract"""
    template_id: Optional[int] = None


class ContractUpdate(BaseModel):
    """Schema for updating contract (all fields optional)"""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ContractStatus] = None
    contract_value: Optional[Decimal] = None
    currency: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_contact: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    signature_date: Optional[datetime] = None


class ContractResponse(ContractBase):
    """Schema for contract response"""
    id: int
    status: ContractStatus
    signature_date: Optional[datetime] = None
    docusign_envelope_id: Optional[str] = None
    docusign_status: Optional[str] = None
    owner_id: int
    template_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
