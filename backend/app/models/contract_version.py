"""
Contract Version History model for tracking changes
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class ContractVersion(Base):
    """Contract version history for tracking all changes"""

    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)

    # Store snapshot of contract data
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    contract_value = Column(String)
    currency = Column(String)
    counterparty_name = Column(String, nullable=False)
    counterparty_contact = Column(String)

    # Change metadata
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_summary = Column(Text)  # Summary of what changed
    changes_json = Column(JSON)  # Detailed changes in JSON format

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    contract = relationship("Contract", backref="versions")
    changed_by = relationship("User")

    def __repr__(self):
        return f"<ContractVersion(contract_id={self.contract_id}, version={self.version_number})>"
