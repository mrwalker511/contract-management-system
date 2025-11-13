"""
Tests for template management endpoints
"""
import pytest
from fastapi import status


@pytest.fixture
def test_template(db_session, test_legal_user):
    """Create a test template"""
    from ..models.template import Template

    template = Template(
        name="NDA Template",
        description="Standard NDA template",
        content="This is a non-disclosure agreement...",
        category="NDA",
        created_by_id=test_legal_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


def test_create_template_as_legal(client, legal_auth_headers):
    """Test creating template as legal user"""
    response = client.post(
        "/api/v1/templates/",
        headers=legal_auth_headers,
        json={
            "name": "MSA Template",
            "description": "Master Service Agreement",
            "content": "This is an MSA...",
            "category": "MSA"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "MSA Template"
    assert data["category"] == "MSA"


def test_create_template_as_non_legal(client, auth_headers):
    """Test creating template as non-legal user (should fail)"""
    response = client.post(
        "/api/v1/templates/",
        headers=auth_headers,
        json={
            "name": "Test Template",
            "content": "Test content"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_templates(client, auth_headers, test_template):
    """Test listing templates"""
    response = client.get("/api/v1/templates/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_templates_with_category_filter(client, auth_headers, test_template):
    """Test listing templates with category filter"""
    response = client.get("/api/v1/templates/?category=NDA", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(t["category"] == "NDA" for t in data)


def test_list_templates_with_active_filter(client, auth_headers, test_template):
    """Test listing templates with active filter"""
    response = client.get("/api/v1/templates/?is_active=true", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(t["is_active"] for t in data)


def test_get_template_by_id(client, auth_headers, test_template):
    """Test getting template by ID"""
    response = client.get(f"/api/v1/templates/{test_template.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_template.id
    assert data["name"] == test_template.name


def test_update_template_as_legal(client, legal_auth_headers, test_template):
    """Test updating template as legal user"""
    response = client.put(
        f"/api/v1/templates/{test_template.id}",
        headers=legal_auth_headers,
        json={"name": "Updated NDA Template"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated NDA Template"


def test_update_template_as_non_legal(client, auth_headers, test_template):
    """Test updating template as non-legal user (should fail)"""
    response = client.put(
        f"/api/v1/templates/{test_template.id}",
        headers=auth_headers,
        json={"name": "Hacked Template"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_template_as_legal(client, legal_auth_headers, test_template):
    """Test deleting template as legal user"""
    response = client.delete(f"/api/v1/templates/{test_template.id}", headers=legal_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_template_as_non_legal(client, auth_headers, test_template):
    """Test deleting template as non-legal user (should fail)"""
    response = client.delete(f"/api/v1/templates/{test_template.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_nonexistent_template(client, auth_headers):
    """Test getting nonexistent template"""
    response = client.get("/api/v1/templates/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_template_deactivation(client, legal_auth_headers, test_template):
    """Test deactivating a template"""
    response = client.put(
        f"/api/v1/templates/{test_template.id}",
        headers=legal_auth_headers,
        json={"is_active": False}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False
