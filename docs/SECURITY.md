# Security Guidelines - Contract Management System

## Overview

This document outlines the security measures implemented in the Contract Management System backend and provides guidelines for secure deployment and operation.

## Authentication & Authorization

### JWT Token Security

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Token Expiration**: 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Storage**: Tokens include user ID and role in payload
- **Validation**: All protected endpoints verify token signature, expiration, and user status

**Critical Configuration**:
```env
SECRET_KEY=<generate-strong-random-key-minimum-32-characters>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

⚠️ **IMPORTANT**: Generate a cryptographically secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Password Security

**Password Requirements** (enforced via Pydantic validation):
- Minimum length: 8 characters
- Maximum length: 72 characters (bcrypt limitation)
- Must contain at least one letter
- Must contain at least one digit

**Password Hashing**:
- Algorithm: bcrypt (via passlib)
- Automatically salted
- Computationally expensive to prevent brute-force attacks
- Compatible bcrypt version: 4.1.2

**Implementation**:
```python
# Password validation in schemas/user.py
@field_validator('password')
def validate_password(cls, v: str) -> str:
    if len(v) < 8 or len(v) > 72:
        raise ValueError('Password length requirements not met')
    # Additional checks...
```

### Role-Based Access Control (RBAC)

**Roles**:
- `procurement`: Can manage own contracts, view templates
- `legal`: Can manage templates, view all contracts, manage own contracts
- `finance`: Can view all contracts, manage own contracts
- `admin`: Full access to all resources

**Authorization Checks**:
- Implemented via `check_user_role()` dependency
- Users can only access their own resources (except admins)
- Role comparison uses enum values for type safety

## Input Validation

### Email Normalization

- All emails automatically converted to lowercase
- Leading/trailing whitespace removed
- Case-insensitive lookups for authentication
- Prevents duplicate accounts with different casing

### Data Validation

- **Pydantic** schemas enforce type safety and validation
- **SQLAlchemy ORM** prevents SQL injection via parameterized queries
- **Email validation** via pydantic `EmailStr` type
- **Enum validation** for user roles and contract statuses

## Database Security

### Connection Security

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

**Best Practices**:
1. Use strong database passwords (minimum 16 characters)
2. Restrict database user permissions to only required operations
3. Use SSL/TLS for database connections in production:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```
4. Never commit `.env` file with credentials to version control

### SQL Injection Prevention

- All database queries use SQLAlchemy ORM
- Parameterized queries prevent SQL injection
- No raw SQL strings with user input

### Data at Rest

- Passwords: bcrypt hashed (never stored in plain text)
- Sensitive fields: Consider encrypting in production
- Database backups: Encrypt and store securely

## API Security

### CORS Configuration

```python
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

**Production Configuration**:
- Restrict to specific frontend domains
- Never use `["*"]` in production
- Include protocol (http/https) in origins

### Rate Limiting

**Phase 1 Status**: Not implemented

**Recommended for Phase 2**:
```python
# Using slowapi or fastapi-limiter
@limiter.limit("5/minute")
@router.post("/auth/login")
```

**Endpoints to prioritize**:
- `/auth/login` - 5 requests/minute
- `/auth/register` - 3 requests/hour
- All API endpoints - 100 requests/minute per user

### Input Size Limits

- FastAPI default: 16 MB request body
- Configure via `app = FastAPI(max_request_size=...)`
- Validate file uploads separately if implementing Phase 2

## Common Vulnerabilities (OWASP Top 10)

### ✅ Implemented Protections

1. **Broken Access Control**
   - RBAC implemented with role checks
   - Users can only access own resources
   - Admin privileges properly gated

2. **Cryptographic Failures**
   - Bcrypt for password hashing
   - JWT tokens with HMAC signature
   - Timezone-aware datetime handling

3. **Injection**
   - ORM prevents SQL injection
   - Pydantic validation prevents injection attacks
   - No user input in raw queries

4. **Insecure Design**
   - Password requirements enforced
   - Email normalization prevents bypass
   - Token expiration implemented

5. **Security Misconfiguration**
   - Environment-based configuration
   - Debug mode disabled by default
   - Security headers (add in Phase 2)

### ⚠️ Additional Recommendations for Production

1. **HTTPS Only**
   ```python
   # Add security headers middleware
   app.add_middleware(
       TrustedHostMiddleware,
       allowed_hosts=["yourdomain.com"]
   )
   ```

2. **Security Headers**
   ```python
   @app.middleware("http")
   async def add_security_headers(request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       response.headers["Strict-Transport-Security"] = "max-age=31536000"
       return response
   ```

3. **Audit Logging**
   - Log all authentication attempts
   - Log permission denials
   - Log data modifications
   - Include user ID, IP, timestamp

4. **Session Management**
   - Implement token refresh mechanism
   - Blacklist revoked tokens (Redis)
   - Force re-authentication for sensitive operations

5. **Monitoring & Alerting**
   - Failed login attempts (potential brute force)
   - Permission violations
   - Unusual API usage patterns
   - Database connection failures

## Environment Configuration

### Development (.env)

```env
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/contract_db_dev
SECRET_KEY=dev-only-key-change-for-production
```

### Production (.env.production)

```env
DEBUG=False
DATABASE_URL=postgresql://prod_user:STRONG_PASSWORD@prod-host:5432/contract_db?sslmode=require
SECRET_KEY=<64-character-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480  # 8 hours for production
BACKEND_CORS_ORIGINS=["https://contracts.yourdomain.com"]
```

## Deployment Checklist

### Pre-Deployment

- [ ] Generate strong SECRET_KEY
- [ ] Configure production DATABASE_URL with SSL
- [ ] Set DEBUG=False
- [ ] Configure specific CORS origins
- [ ] Review and restrict database user permissions
- [ ] Enable database SSL connections
- [ ] Set up database backups
- [ ] Configure reverse proxy (nginx/caddy)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up logging and monitoring

### Post-Deployment

- [ ] Test authentication flow
- [ ] Verify RBAC permissions
- [ ] Check CORS configuration
- [ ] Test rate limiting (Phase 2)
- [ ] Monitor logs for errors
- [ ] Set up alerting
- [ ] Perform security scan
- [ ] Document incident response procedures

## Security Updates

### Dependency Management

```bash
# Check for security vulnerabilities
pip install safety
safety check --file requirements.txt

# Update dependencies (test thoroughly)
pip list --outdated
```

**Critical Dependencies to Monitor**:
- `fastapi` - Security fixes
- `sqlalchemy` - SQL injection fixes
- `passlib` / `bcrypt` - Cryptography updates
- `python-jose` - JWT vulnerabilities
- `pydantic` - Validation bypasses

## Incident Response

### Security Breach Response

1. **Immediate Actions**:
   - Rotate SECRET_KEY immediately
   - Invalidate all active tokens
   - Review audit logs for suspicious activity
   - Identify breach vector
   - Patch vulnerability

2. **Investigation**:
   - Identify affected users/data
   - Determine extent of breach
   - Preserve evidence/logs
   - Document timeline

3. **Recovery**:
   - Force password resets for affected users
   - Apply security patches
   - Enhance monitoring
   - Communicate with stakeholders

4. **Post-Mortem**:
   - Root cause analysis
   - Implement additional controls
   - Update security procedures
   - Training and awareness

## Contact & Reporting

For security vulnerabilities, please report to: [security contact email]

**Do not** disclose security issues publicly before they are patched.

## Compliance Considerations

### Data Protection

- **GDPR**: Implement right to erasure (delete user endpoint)
- **Data Minimization**: Only collect necessary data
- **Consent**: Document data usage in privacy policy
- **Data Retention**: Implement retention policies

### Audit Requirements

- Log all data access/modifications
- Maintain immutable audit trail
- Regular security assessments
- Access control reviews

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0 (Phase 1)
