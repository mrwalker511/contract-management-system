"""
Pydantic schemas for document operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""
    contract_id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    document_type: Optional[str] = "attachment"


class DocumentResponse(DocumentBase):
    """Schema for document responses."""
    id: int
    file_hash: Optional[str] = None
    uploaded_by_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    """Schema for document upload responses."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    document_type: str
    uploaded_at: datetime
    message: str = "Document uploaded successfully"

    model_config = ConfigDict(from_attributes=True)
