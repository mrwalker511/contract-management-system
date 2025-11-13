"""
Contract model for managing contracts
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class ContractStatus(str, enum.Enum):
    """Contract lifecycle statuses"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    REJECTED = "rejected"


class Contract(Base):
    """Contract model for storing contract details"""

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Contract content/body

    # Contract details
    contract_number = Column(String, unique=True, index=True)
    status = Column(SQLEnum(ContractStatus), nullable=False, default=ContractStatus.DRAFT, index=True)
    contract_value = Column(Numeric(precision=15, scale=2))  # Monetary value
    currency = Column(String(3), default="USD")  # ISO currency code

    # Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    signature_date = Column(DateTime(timezone=True))

    # Parties
    counterparty_name = Column(String, nullable=False)  # Other party in contract
    counterparty_contact = Column(String)

    # DocuSign integration
    docusign_envelope_id = Column(String, unique=True, index=True)
    docusign_status = Column(String)

    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="contracts")
    template = relationship("Template", back_populates="contracts")

    def __repr__(self):
        return f"<Contract(id={self.id}, title={self.title}, status={self.status})>"
