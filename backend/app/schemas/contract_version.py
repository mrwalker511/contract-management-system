"""
Pydantic schemas for contract version operations.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ContractVersionBase(BaseModel):
    """Base contract version schema."""
    contract_id: int
    version_number: int
    title: str
    description: Optional[str] = None
    content: str
    status: str
    contract_value: Optional[Decimal] = None
    currency: Optional[str] = "USD"
    counterparty_name: str
    counterparty_contact: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ContractVersionCreate(BaseModel):
    """Schema for creating a contract version."""
    change_summary: Optional[str] = None
    changes_json: Optional[Dict[str, Any]] = None


class ContractVersionResponse(ContractVersionBase):
    """Schema for contract version responses."""
    id: int
    changed_by_id: int
    change_summary: Optional[str] = None
    changes_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VersionComparisonResponse(BaseModel):
    """Schema for version comparison responses."""
    contract_id: int
    version_1: int
    version_2: int
    differences: Dict[str, Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
