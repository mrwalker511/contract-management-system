"""
Services package for Phase 2 features.
"""
from .audit_service import AuditService, log_create, log_update, log_delete, log_login, log_logout
from .version_service import VersionService
from .email_service import EmailService, email_service
from .teams_service import TeamsService, teams_service
from .document_service import DocumentService, document_service

__all__ = [
    "AuditService",
    "log_create",
    "log_update",
    "log_delete",
    "log_login",
    "log_logout",
    "VersionService",
    "EmailService",
    "email_service",
    "TeamsService",
    "teams_service",
    "DocumentService",
    "document_service",
]
