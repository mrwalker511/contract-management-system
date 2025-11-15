"""
Document upload and management service.
"""
import os
import hashlib
import uuid
from pathlib import Path
from typing import Optional, List
import aiofiles
import magic
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User


class DocumentService:
    """Service for managing document uploads and storage."""

    # Allowed MIME types for document uploads
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "image/png",
        "image/jpeg",
        "image/gif",
    }

    # Maximum file size (50 MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self):
        """Initialize document service with storage configuration."""
        self.upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads"))
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for organization
        (self.upload_dir / "contracts").mkdir(exist_ok=True)

    @staticmethod
    async def calculate_file_hash(file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file for integrity verification.

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()

        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    @staticmethod
    def validate_file_type(file_path: Path) -> str:
        """
        Detect and validate MIME type of a file.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string

        Raises:
            ValueError: If file type is not allowed
        """
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(str(file_path))

        if mime_type not in DocumentService.ALLOWED_MIME_TYPES:
            raise ValueError(f"File type {mime_type} is not allowed")

        return mime_type

    async def save_upload_file(
        self,
        upload_file: UploadFile,
        contract_id: int,
    ) -> tuple[Path, int]:
        """
        Save an uploaded file to disk.

        Args:
            upload_file: FastAPI UploadFile object
            contract_id: Contract ID for organizing files

        Returns:
            Tuple of (file_path, file_size)

        Raises:
            ValueError: If file is too large or invalid
        """
        # Generate unique filename
        file_ext = Path(upload_file.filename or "file").suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / "contracts" / str(contract_id)
        file_path.mkdir(parents=True, exist_ok=True)
        file_path = file_path / unique_filename

        # Save file in chunks and track size
        file_size = 0

        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await upload_file.read(8192):
                file_size += len(chunk)

                if file_size > self.MAX_FILE_SIZE:
                    # Delete partial file
                    await aiofiles.os.remove(file_path)
                    raise ValueError(
                        f"File size exceeds maximum allowed size of "
                        f"{self.MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
                    )

                await f.write(chunk)

        return file_path, file_size

    async def upload_document(
        self,
        db: Session,
        upload_file: UploadFile,
        contract_id: int,
        user: User,
        document_type: Optional[str] = "attachment",
    ) -> Document:
        """
        Upload and save a document.

        Args:
            db: Database session
            upload_file: FastAPI UploadFile object
            contract_id: Contract ID to associate document with
            user: User uploading the document
            document_type: Type of document (attachment, signature, amendment, etc.)

        Returns:
            Created Document instance

        Raises:
            ValueError: If file validation fails
        """
        # Save file to disk
        file_path, file_size = await self.save_upload_file(upload_file, contract_id)

        try:
            # Validate file type
            mime_type = self.validate_file_type(file_path)

            # Calculate file hash
            file_hash = await self.calculate_file_hash(file_path)

            # Create database record
            document = Document(
                contract_id=contract_id,
                filename=file_path.name,
                original_filename=upload_file.filename or "unknown",
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                document_type=document_type,
                uploaded_by_id=user.id,
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            return document

        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                await aiofiles.os.remove(file_path)
            raise e

    async def delete_document(
        self,
        db: Session,
        document: Document,
    ) -> bool:
        """
        Delete a document from database and disk.

        Args:
            db: Database session
            document: Document to delete

        Returns:
            True if deleted successfully
        """
        file_path = Path(document.file_path)

        # Delete file from disk
        if file_path.exists():
            try:
                await aiofiles.os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete file {file_path}: {str(e)}")

        # Delete database record
        db.delete(document)
        db.commit()

        return True

    @staticmethod
    def get_contract_documents(
        db: Session,
        contract_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """
        Get all documents for a contract.

        Args:
            db: Database session
            contract_id: Contract ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Document instances
        """
        return (
            db.query(Document)
            .filter(Document.contract_id == contract_id)
            .order_by(Document.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_document_by_id(
        db: Session,
        document_id: int,
    ) -> Optional[Document]:
        """
        Get a document by ID.

        Args:
            db: Database session
            document_id: Document ID

        Returns:
            Document instance or None if not found
        """
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    async def verify_document_integrity(document: Document) -> bool:
        """
        Verify that a document's file matches its stored hash.

        Args:
            document: Document to verify

        Returns:
            True if file integrity is verified, False otherwise
        """
        file_path = Path(document.file_path)

        if not file_path.exists():
            return False

        # Calculate current hash
        current_hash = await DocumentService.calculate_file_hash(file_path)

        # Compare with stored hash
        return current_hash == document.file_hash


# Global document service instance
document_service = DocumentService()
