"""
Template management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user, check_user_role
from ..models.user import User
from ..models.template import Template
from ..schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(check_user_role(["legal", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Create a new template (legal or admin role required)

    Args:
        template_data: Template creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created template data
    """
    db_template = Template(
        **template_data.model_dump(),
        created_by_id=current_user.id
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all templates with optional filters

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Optional category filter
        is_active: Optional active status filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of templates
    """
    query = db.query(Template)

    # Apply filters
    if category:
        query = query.filter(Template.category == category)
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)

    templates = query.offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get template by ID

    Args:
        template_id: Template ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Template data

    Raises:
        HTTPException: If template not found
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: User = Depends(check_user_role(["legal", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Update template by ID (legal or admin role required)

    Args:
        template_id: Template ID
        template_data: Updated template data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated template data

    Raises:
        HTTPException: If template not found
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Update template fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(check_user_role(["legal", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Delete template by ID (legal or admin role required)

    Args:
        template_id: Template ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If template not found
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    db.delete(template)
    db.commit()

    return None
