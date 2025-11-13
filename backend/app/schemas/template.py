"""
Pydantic schemas for Template model
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TemplateBase(BaseModel):
    """Base template schema with common fields"""
    name: str
    description: Optional[str] = None
    content: str
    category: Optional[str] = None


class TemplateCreate(TemplateBase):
    """Schema for creating a new template"""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating template (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response"""
    id: int
    is_active: bool
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
