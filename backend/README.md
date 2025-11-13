# Contract Management System - Backend API

FastAPI backend for the Contract Management System with JWT authentication and role-based access control.

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn app.main:app --reload
```

Visit http://localhost:8000/api/docs for interactive API documentation.

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Features

- ✅ JWT authentication
- ✅ Role-based access control (procurement, legal, finance, admin)
- ✅ User management
- ✅ Contract CRUD operations
- ✅ Template management
- ✅ PostgreSQL database with SQLAlchemy
- ✅ Comprehensive test suite
- ✅ OpenAPI/Swagger documentation

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/` - List users (admin)
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user (admin)

### Templates
- `POST /api/v1/templates/` - Create template (legal/admin)
- `GET /api/v1/templates/` - List templates
- `GET /api/v1/templates/{id}` - Get template
- `PUT /api/v1/templates/{id}` - Update template (legal/admin)
- `DELETE /api/v1/templates/{id}` - Delete template (legal/admin)

### Contracts
- `POST /api/v1/contracts/` - Create contract
- `GET /api/v1/contracts/` - List contracts
- `GET /api/v1/contracts/{id}` - Get contract
- `PUT /api/v1/contracts/{id}` - Update contract
- `DELETE /api/v1/contracts/{id}` - Delete contract

## Documentation

See `/docs` directory for:
- `API.md` - Complete API documentation
- `SETUP.md` - Detailed setup instructions
- `AGENT_LOG.md` - Development log

## Tech Stack

- **Framework**: FastAPI 0.109.2
- **Database**: PostgreSQL with SQLAlchemy 2.0.27
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Testing**: Pytest 8.0.0
- **Validation**: Pydantic 2.6.1

## Project Structure

```
app/
├── main.py              # FastAPI app
├── core/               # Configuration, database, security
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── routes/             # API endpoints
└── tests/              # Test suite
```

## License

Internal use only.
