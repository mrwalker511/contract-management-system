# Contract Management System API Documentation

## Overview

The Contract Management System API provides a comprehensive backend for managing contracts, templates, and users with role-based access control (RBAC).

**Base URL**: `http://localhost:8000/api/v1`

**API Documentation**: `http://localhost:8000/api/docs` (Swagger UI)

## Authentication

The API uses JWT (JSON Web Token) bearer authentication.

### Register a New User

```http
POST /api/v1/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "procurement",
  "password": "securepassword123"
}
```

**Roles**: `procurement`, `legal`, `finance`, `admin`

**Response**: `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "procurement",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### Login

```http
POST /api/v1/auth/login
```

**Request Body** (form-data):
- `username`: user email
- `password`: user password

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the `Authorization` header for all authenticated requests:

```
Authorization: Bearer <your_token_here>
```

## User Endpoints

### Get Current User Profile

```http
GET /api/v1/users/me
```

**Headers**: `Authorization: Bearer <token>`

**Response**: `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "procurement",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### List All Users (Admin Only)

```http
GET /api/v1/users/?skip=0&limit=100
```

**Headers**: `Authorization: Bearer <admin_token>`

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Response**: `200 OK` - Array of user objects

### Get User by ID

```http
GET /api/v1/users/{user_id}
```

**Authorization**: Users can view their own profile; admins can view any profile

### Update User

```http
PUT /api/v1/users/{user_id}
```

**Request Body** (all fields optional):
```json
{
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "role": "legal",
  "password": "newpassword123",
  "is_active": true
}
```

**Note**: Only admins can change `role` and `is_active` fields.

### Delete User (Admin Only)

```http
DELETE /api/v1/users/{user_id}
```

**Response**: `204 No Content`

## Template Endpoints

### Create Template (Legal/Admin Only)

```http
POST /api/v1/templates/
```

**Request Body**:
```json
{
  "name": "Standard NDA",
  "description": "Non-disclosure agreement template",
  "content": "This Non-Disclosure Agreement...",
  "category": "NDA"
}
```

**Response**: `201 Created`

### List Templates

```http
GET /api/v1/templates/?skip=0&limit=100&category=NDA&is_active=true
```

**Query Parameters**:
- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum records to return
- `category` (optional): Filter by category
- `is_active` (optional): Filter by active status

**Response**: `200 OK` - Array of template objects

### Get Template by ID

```http
GET /api/v1/templates/{template_id}
```

### Update Template (Legal/Admin Only)

```http
PUT /api/v1/templates/{template_id}
```

**Request Body** (all fields optional):
```json
{
  "name": "Updated NDA",
  "description": "Updated description",
  "content": "Updated content...",
  "category": "NDA",
  "is_active": true
}
```

### Delete Template (Legal/Admin Only)

```http
DELETE /api/v1/templates/{template_id}
```

**Response**: `204 No Content`

## Contract Endpoints

### Create Contract

```http
POST /api/v1/contracts/
```

**Request Body**:
```json
{
  "title": "Service Agreement with ACME Corp",
  "description": "Software development services",
  "content": "This agreement is made between...",
  "contract_number": "CT-2024-001",
  "contract_value": "50000.00",
  "currency": "USD",
  "counterparty_name": "ACME Corporation",
  "counterparty_contact": "contact@acme.com",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "template_id": 1
}
```

**Note**: `contract_number` is auto-generated if not provided.

**Response**: `201 Created`

### List Contracts

```http
GET /api/v1/contracts/?skip=0&limit=100&status=draft&owner_id=1
```

**Query Parameters**:
- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum records to return
- `status` (optional): Filter by status
- `owner_id` (optional, admin only): Filter by owner

**Authorization**: Non-admin users see only their own contracts

**Contract Statuses**:
- `draft`
- `pending_review`
- `under_review`
- `approved`
- `pending_signature`
- `signed`
- `active`
- `expired`
- `terminated`
- `rejected`

### Get Contract by ID

```http
GET /api/v1/contracts/{contract_id}
```

**Authorization**: Users can view their own contracts; admins can view any contract

### Update Contract

```http
PUT /api/v1/contracts/{contract_id}
```

**Request Body** (all fields optional):
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "content": "Updated content...",
  "status": "pending_review",
  "contract_value": "60000.00",
  "currency": "USD",
  "counterparty_name": "ACME Corp",
  "counterparty_contact": "newcontact@acme.com",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "signature_date": "2024-01-15T10:00:00Z"
}
```

### Delete Contract

```http
DELETE /api/v1/contracts/{contract_id}
```

**Response**: `204 No Content`

**Authorization**: Users can delete their own contracts; admins can delete any contract

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Role-Based Access Control (RBAC)

### Roles and Permissions

| Role | Users | Templates | Contracts | Description |
|------|-------|-----------|-----------|-------------|
| **procurement** | Own profile | Read | Full access to own contracts | Procurement team members |
| **legal** | Own profile | Full access | Read all, edit own | Legal team members |
| **finance** | Own profile | Read | Read all, edit own | Finance team members |
| **admin** | Full access | Full access | Full access | System administrators |

### Permission Matrix

| Endpoint | Procurement | Legal | Finance | Admin |
|----------|-------------|-------|---------|-------|
| Register user | ✓ | ✓ | ✓ | ✓ |
| View own profile | ✓ | ✓ | ✓ | ✓ |
| View all users | ✗ | ✗ | ✗ | ✓ |
| Update own profile | ✓ | ✓ | ✓ | ✓ |
| Update user role | ✗ | ✗ | ✗ | ✓ |
| Delete user | ✗ | ✗ | ✗ | ✓ |
| Create template | ✗ | ✓ | ✗ | ✓ |
| View templates | ✓ | ✓ | ✓ | ✓ |
| Update template | ✗ | ✓ | ✗ | ✓ |
| Delete template | ✗ | ✓ | ✗ | ✓ |
| Create contract | ✓ | ✓ | ✓ | ✓ |
| View own contracts | ✓ | ✓ | ✓ | ✓ |
| View all contracts | ✗ | ✗ | ✗ | ✓ |
| Update own contract | ✓ | ✓ | ✓ | ✓ |
| Delete own contract | ✓ | ✓ | ✓ | ✓ |

## Rate Limiting

Currently not implemented in Phase 1. Will be added in future phases.

## Pagination

List endpoints support pagination via `skip` and `limit` query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

## OpenAPI Specification

The complete OpenAPI specification is available at:
- JSON format: `/api/openapi.json`
- Interactive docs: `/api/docs` (Swagger UI)
- Alternative docs: `/api/redoc` (ReDoc)
- Shared spec: `/shared/openapi.json`
