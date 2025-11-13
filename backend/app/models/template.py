"""
Template model for contract templates
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Template(Base):
    """Template model for storing contract templates"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Template content/body
    category = Column(String, index=True)  # e.g., "NDA", "MSA", "SOW"
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User", back_populates="templates")
    contracts = relationship("Contract", back_populates="template")

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>"
