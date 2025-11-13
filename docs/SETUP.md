# Setup Guide - Contract Management System Backend

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- virtualenv (recommended)

## Database Setup

### 1. Install PostgreSQL

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Windows**:
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE contract_db;
CREATE USER contract_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE contract_db TO contract_user;
\q
```

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://contract_user:your_password@localhost:5432/contract_db

# Security - Generate a secure random key!
SECRET_KEY=your-very-secure-random-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
DEBUG=True
```

**Generate a secure SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Initialize Database

The database tables will be created automatically when you start the application.

For migrations in the future, we can use Alembic:
```bash
# Initialize Alembic (future use)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Running the Application

### Development Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

### Run All Tests

```bash
# From the backend directory
pytest
```

### Run Specific Test File

```bash
pytest app/tests/test_auth.py
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser to view coverage
```

### Run Specific Test

```bash
pytest app/tests/test_auth.py::test_login_success
```

## Generate OpenAPI Specification

```bash
# From the project root
python scripts/generate_openapi.py
```

This will generate `/shared/openapi.json` for use by the frontend.

## Creating an Admin User

### Using Python Shell

```bash
# From the backend directory with venv activated
python
```

```python
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

admin = User(
    email="admin@example.com",
    full_name="Admin User",
    role=UserRole.ADMIN,
    hashed_password=get_password_hash("admin123"),
    is_active=True
)

db.add(admin)
db.commit()
print(f"Admin user created: {admin.email}")
db.close()
```

### Using API

```bash
# Register as any role first
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "password": "securepass123"
  }'
```

## API Testing with curl

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "procurement",
    "password": "testpass123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@example.com&password=testpass123"
```

Copy the `access_token` from the response.

### 3. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <your_access_token>"
```

### 4. Create a Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Contract",
    "content": "Contract content here",
    "counterparty_name": "ACME Corp",
    "contract_value": "10000.00"
  }'
```

## Troubleshooting

### Database Connection Error

**Error**: `could not connect to server`

**Solution**: Ensure PostgreSQL is running:
```bash
# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql

# macOS
brew services list
brew services start postgresql
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Authentication Errors

**Error**: `Could not validate credentials`

**Solution**:
1. Check that SECRET_KEY in .env matches the one used to create tokens
2. Verify token hasn't expired
3. Check that token is properly formatted in Authorization header

### Database Tables Not Created

**Solution**: Tables are created automatically on first run. If issues persist:
```python
from app.core.database import engine, Base
from app.models import User, Template, Contract
Base.metadata.create_all(bind=engine)
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py      # Database connection
│   │   └── security.py      # Auth & security utilities
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── template.py      # Template model
│   │   └── contract.py      # Contract model
│   ├── schemas/
│   │   ├── user.py          # User Pydantic schemas
│   │   ├── template.py      # Template schemas
│   │   └── contract.py      # Contract schemas
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management endpoints
│   │   ├── templates.py     # Template endpoints
│   │   └── contracts.py     # Contract endpoints
│   └── tests/
│       ├── conftest.py      # Test fixtures
│       ├── test_auth.py     # Auth tests
│       ├── test_users.py    # User tests
│       ├── test_templates.py # Template tests
│       └── test_contracts.py # Contract tests
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
└── .env.example            # Environment variables template
```

## Next Steps

After completing Phase 1 backend setup:

1. ✅ Backend API is running
2. ✅ Tests are passing
3. ✅ OpenAPI spec is generated in `/shared`
4. 🔄 Frontend can now be developed using the OpenAPI spec
5. 🔄 Phase 2: Add email notifications, Teams integration, and version history
