"""
Tests for user management endpoints
"""
import pytest
from fastapi import status


def test_get_current_user(client, auth_headers, test_user):
    """Test getting current user profile"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_users_as_admin(client, admin_auth_headers, test_user):
    """Test listing users as admin"""
    response = client.get("/api/v1/users/", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_users_as_non_admin(client, auth_headers):
    """Test listing users as non-admin (should fail)"""
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_by_id(client, auth_headers, test_user):
    """Test getting user by ID (own profile)"""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id


def test_get_other_user_as_non_admin(client, auth_headers, test_legal_user):
    """Test getting other user's profile as non-admin (should fail)"""
    response = client.get(f"/api/v1/users/{test_legal_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_other_user_as_admin(client, admin_auth_headers, test_user):
    """Test getting other user's profile as admin"""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_update_own_profile(client, auth_headers, test_user):
    """Test updating own profile"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={"full_name": "Updated Name"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_update_own_role_as_non_admin(client, auth_headers, test_user):
    """Test that non-admin cannot change their own role"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={"role": "admin"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Role should not have changed
    assert data["role"] == "procurement"


def test_update_user_role_as_admin(client, admin_auth_headers, test_user):
    """Test admin can change user role"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=admin_auth_headers,
        json={"role": "legal"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["role"] == "legal"


def test_delete_user_as_admin(client, admin_auth_headers, test_user):
    """Test deleting user as admin"""
    response = client.delete(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_as_non_admin(client, auth_headers, test_legal_user):
    """Test deleting user as non-admin (should fail)"""
    response = client.delete(f"/api/v1/users/{test_legal_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_nonexistent_user(client, admin_auth_headers):
    """Test getting nonexistent user"""
    response = client.get("/api/v1/users/99999", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
