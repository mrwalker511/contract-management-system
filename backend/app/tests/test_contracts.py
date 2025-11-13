"""
Tests for contract management endpoints
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta


@pytest.fixture
def test_contract(db_session, test_user):
    """Create a test contract"""
    from ..models.contract import Contract, ContractStatus

    contract = Contract(
        title="Test Contract",
        description="Test contract description",
        content="This is a test contract...",
        contract_number="CT-TEST001",
        status=ContractStatus.DRAFT,
        counterparty_name="ACME Corp",
        owner_id=test_user.id
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def test_create_contract(client, auth_headers):
    """Test creating a contract"""
    response = client.post(
        "/api/v1/contracts/",
        headers=auth_headers,
        json={
            "title": "Service Agreement",
            "description": "Software development services",
            "content": "Contract content here...",
            "counterparty_name": "Tech Solutions Inc",
            "contract_value": "50000.00",
            "currency": "USD"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Service Agreement"
    assert data["counterparty_name"] == "Tech Solutions Inc"
    assert "contract_number" in data
    assert data["status"] == "draft"


def test_create_contract_with_dates(client, auth_headers):
    """Test creating contract with start and end dates"""
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=365)

    response = client.post(
        "/api/v1/contracts/",
        headers=auth_headers,
        json={
            "title": "Annual Contract",
            "content": "Contract content...",
            "counterparty_name": "Partner Co",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["start_date"] is not None
    assert data["end_date"] is not None


def test_list_contracts(client, auth_headers, test_contract):
    """Test listing contracts"""
    response = client.get("/api/v1/contracts/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_contracts_with_status_filter(client, auth_headers, test_contract):
    """Test listing contracts with status filter"""
    response = client.get("/api/v1/contracts/?status=draft", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(c["status"] == "draft" for c in data)


def test_user_can_only_see_own_contracts(client, auth_headers, legal_auth_headers, test_contract):
    """Test that non-admin users can only see their own contracts"""
    # Legal user should not see the test_user's contract
    response = client.get("/api/v1/contracts/", headers=legal_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    contract_ids = [c["id"] for c in data]
    assert test_contract.id not in contract_ids


def test_admin_can_see_all_contracts(client, admin_auth_headers, test_contract):
    """Test that admin can see all contracts"""
    response = client.get("/api/v1/contracts/", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0


def test_get_contract_by_id(client, auth_headers, test_contract):
    """Test getting contract by ID"""
    response = client.get(f"/api/v1/contracts/{test_contract.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_contract.id
    assert data["title"] == test_contract.title


def test_get_other_users_contract(client, legal_auth_headers, test_contract):
    """Test that user cannot get another user's contract"""
    response = client.get(f"/api/v1/contracts/{test_contract.id}", headers=legal_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_get_any_contract(client, admin_auth_headers, test_contract):
    """Test that admin can get any contract"""
    response = client.get(f"/api/v1/contracts/{test_contract.id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_update_contract(client, auth_headers, test_contract):
    """Test updating a contract"""
    response = client.put(
        f"/api/v1/contracts/{test_contract.id}",
        headers=auth_headers,
        json={
            "title": "Updated Contract Title",
            "status": "pending_review"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Contract Title"
    assert data["status"] == "pending_review"


def test_update_other_users_contract(client, legal_auth_headers, test_contract):
    """Test that user cannot update another user's contract"""
    response = client.put(
        f"/api/v1/contracts/{test_contract.id}",
        headers=legal_auth_headers,
        json={"title": "Hacked Title"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_contract(client, auth_headers, test_contract):
    """Test deleting a contract"""
    response = client.delete(f"/api/v1/contracts/{test_contract.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    response = client.get(f"/api/v1/contracts/{test_contract.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_other_users_contract(client, legal_auth_headers, test_contract):
    """Test that user cannot delete another user's contract"""
    response = client.delete(f"/api/v1/contracts/{test_contract.id}", headers=legal_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_nonexistent_contract(client, auth_headers):
    """Test getting nonexistent contract"""
    response = client.get("/api/v1/contracts/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_contract_number_generation(client, auth_headers):
    """Test that contract numbers are automatically generated"""
    response = client.post(
        "/api/v1/contracts/",
        headers=auth_headers,
        json={
            "title": "Auto Number Contract",
            "content": "Content...",
            "counterparty_name": "Partner"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["contract_number"] is not None
    assert data["contract_number"].startswith("CT-")
