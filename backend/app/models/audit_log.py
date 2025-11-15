"""
Audit Log model for tracking all system actions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class AuditLog(Base):
    """Audit log for tracking all system actions"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # contract, user, template, etc.
    resource_id = Column(Integer, nullable=True, index=True)

    # Details
    description = Column(Text, nullable=False)
    changes = Column(JSON)  # Before/after data
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(action={self.action}, resource={self.resource_type}, user_id={self.user_id})>"
