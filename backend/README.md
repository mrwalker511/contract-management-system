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

### Phase 1 (Completed)
- ✅ JWT authentication
- ✅ Role-based access control (procurement, legal, finance, admin)
- ✅ User management
- ✅ Contract CRUD operations
- ✅ Template management
- ✅ PostgreSQL database with SQLAlchemy
- ✅ Comprehensive test suite
- ✅ OpenAPI/Swagger documentation

### Phase 2 (Completed)
- ✅ Contract version history tracking
- ✅ Audit logging for all system actions
- ✅ Email notifications (SMTP)
- ✅ Microsoft Teams integration
- ✅ Document upload and management
- ✅ File integrity verification (SHA256 hashing)
- ✅ Contract change tracking and comparison
- ✅ Version restore functionality

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

### Documents (Phase 2)
- `POST /api/v1/documents/upload/{contract_id}` - Upload document
- `GET /api/v1/documents/contract/{contract_id}` - List contract documents
- `GET /api/v1/documents/{id}` - Get document metadata
- `GET /api/v1/documents/{id}/download` - Download document
- `DELETE /api/v1/documents/{id}` - Delete document

### Versions (Phase 2)
- `GET /api/v1/versions/contract/{contract_id}` - Get contract version history
- `GET /api/v1/versions/contract/{contract_id}/version/{version_number}` - Get specific version
- `GET /api/v1/versions/contract/{contract_id}/compare/{v1}/{v2}` - Compare versions
- `POST /api/v1/versions/contract/{contract_id}/restore/{version_number}` - Restore version

### Audit Logs (Phase 2)
- `GET /api/v1/audit/logs` - Get audit logs (admin/legal)
- `GET /api/v1/audit/logs/user/{user_id}` - Get user audit logs
- `GET /api/v1/audit/logs/contract/{contract_id}` - Get contract audit logs

## Documentation

See `/docs` directory for:
- `API.md` - Complete API documentation
- `SETUP.md` - Detailed setup instructions
- `AGENT_LOG.md` - Development log

## Tech Stack

- **Framework**: FastAPI 0.109.2
- **Database**: PostgreSQL with SQLAlchemy 2.0.27, Alembic 1.13.1
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Testing**: Pytest 8.0.0
- **Validation**: Pydantic 2.6.1
- **Email**: aiosmtplib 3.0.1 + Jinja2 3.1.3
- **Teams Integration**: msgraph-sdk 1.1.0
- **File Handling**: aiofiles 23.2.1, python-magic 0.4.27

## Project Structure

```
app/
├── main.py              # FastAPI app
├── core/               # Configuration, database, security
├── models/             # SQLAlchemy models (User, Contract, Template, etc.)
├── schemas/            # Pydantic schemas (validation)
├── routes/             # Phase 1 API endpoints
├── api/                # Phase 2 API endpoints
├── services/           # Business logic (audit, version, email, teams, documents)
├── templates/          # Email templates (Jinja2)
└── tests/              # Test suite
alembic/                # Database migrations
└── versions/           # Migration scripts
```

## Phase 2 Configuration

### Email Notifications

Configure SMTP settings in `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@contractmanagement.com
SMTP_FROM_NAME=Contract Management System
SMTP_USE_TLS=true
```

### Microsoft Teams Integration

Configure Azure AD app and Teams webhook:

```env
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
TEAMS_TEAM_ID=your-team-id
TEAMS_CHANNEL_ID=your-channel-id
```

### File Uploads

```env
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800  # 50MB
```

Allowed file types:
- PDF, Word (.doc, .docx)
- Excel (.xls, .xlsx)
- Text files (.txt)
- Images (.png, .jpg, .gif)

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## License

Internal use only.
