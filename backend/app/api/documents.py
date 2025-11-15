"""
Document management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contract import Contract
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import document_service
from app.services.audit_service import log_create, log_delete

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload/{contract_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    contract_id: int,
    file: UploadFile = File(...),
    document_type: str = "attachment",
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document for a contract.

    - **contract_id**: Contract ID to associate document with
    - **file**: File to upload
    - **document_type**: Type of document (attachment, signature, amendment)
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check permissions (user must be creator, assigned user, or admin)
    if (
        current_user.role not in ["admin", "legal"]
        and contract.created_by_id != current_user.id
        and contract.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload documents for this contract"
        )

    try:
        # Upload document
        document = await document_service.upload_document(
            db=db,
            upload_file=file,
            contract_id=contract_id,
            user=current_user,
            document_type=document_type,
        )

        # Log the action
        await log_create(
            db=db,
            user=current_user,
            resource_type="document",
            resource_id=document.id,
            description=f"Uploaded document '{file.filename}' for contract #{contract_id}",
            request=request,
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            document_type=document.document_type,
            uploaded_at=document.uploaded_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/contract/{contract_id}", response_model=List[DocumentResponse])
def get_contract_documents(
    contract_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all documents for a contract.

    - **contract_id**: Contract ID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check permissions
    if (
        current_user.role not in ["admin", "legal", "finance"]
        and contract.created_by_id != current_user.id
        and contract.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view documents for this contract"
        )

    documents = document_service.get_contract_documents(
        db=db,
        contract_id=contract_id,
        skip=skip,
        limit=limit,
    )

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get document metadata by ID.

    - **document_id**: Document ID
    """
    document = document_service.get_document_by_id(db=db, document_id=document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Verify contract access
    contract = db.query(Contract).filter(Contract.id == document.contract_id).first()
    if (
        current_user.role not in ["admin", "legal", "finance"]
        and contract.created_by_id != current_user.id
        and contract.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this document"
        )

    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download a document file.

    - **document_id**: Document ID
    """
    document = document_service.get_document_by_id(db=db, document_id=document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Verify contract access
    contract = db.query(Contract).filter(Contract.id == document.contract_id).first()
    if (
        current_user.role not in ["admin", "legal", "finance"]
        and contract.created_by_id != current_user.id
        and contract.assigned_to_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to download this document"
        )

    # Verify file integrity
    if not await document_service.verify_document_integrity(document):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document integrity verification failed"
        )

    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
        media_type=document.mime_type,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document.

    - **document_id**: Document ID
    """
    document = document_service.get_document_by_id(db=db, document_id=document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Verify contract access
    contract = db.query(Contract).filter(Contract.id == document.contract_id).first()
    if (
        current_user.role not in ["admin"]
        and contract.created_by_id != current_user.id
        and document.uploaded_by_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this document"
        )

    # Delete document
    await document_service.delete_document(db=db, document=document)

    # Log the action
    await log_delete(
        db=db,
        user=current_user,
        resource_type="document",
        resource_id=document_id,
        description=f"Deleted document '{document.original_filename}' from contract #{contract.id}",
        request=request,
    )

    return None
