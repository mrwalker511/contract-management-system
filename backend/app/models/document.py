"""
Document model for file uploads
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Document(Base):
    """Document attachments for contracts"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)

    # File metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Storage path
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64))  # SHA256 hash for integrity

    # Document details
    document_type = Column(String(50))  # attachment, signature, amendment, etc.
    description = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)

    # Upload metadata
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    contract = relationship("Contract", backref="documents")
    uploaded_by = relationship("User")

    def __repr__(self):
        return f"<Document(filename={self.filename}, contract_id={self.contract_id})>"
