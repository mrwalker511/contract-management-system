# Contract Management System - Frontend

Modern React + TypeScript frontend for the Contract Management System with Ant Design UI.

## Features

- ✅ React 18 with TypeScript
- ✅ Vite for fast development
- ✅ Ant Design UI components
- ✅ JWT authentication with auto-refresh
- ✅ Role-based access control (RBAC)
- ✅ Protected routes
- ✅ Zustand for state management
- ✅ Axios for API calls with interceptors
- ✅ Responsive dashboard layout
- ✅ Contract CRUD operations
- ✅ TypeScript types from OpenAPI spec

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## Quick Start

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

## Environment Configuration

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── DashboardLayout.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/               # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── Contracts.tsx
│   ├── contexts/            # React contexts & state
│   │   └── AuthContext.tsx
│   ├── services/            # API client and services
│   │   └── api.ts
│   ├── types/               # TypeScript type definitions
│   │   └── api.ts
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
└── vite.config.ts          # Vite configuration
```

## User Roles & Permissions

### Procurement
- Create and manage own contracts
- View templates

### Legal
- Create and manage templates
- View all contracts
- Manage own contracts

### Finance
- View all contracts
- Manage own contracts

### Admin
- Full access to all features
- User management
- Template management
- All contract operations

## Usage Guide

### 1. Registration

1. Navigate to http://localhost:3000/register
2. Fill in:
   - Full Name
   - Email
   - Role (procurement, legal, or finance)
   - Password (min. 8 chars, must contain letters and numbers)
3. Click "Register"
4. You'll be automatically logged in

### 2. Login

1. Navigate to http://localhost:3000/login
2. Enter email and password
3. Click "Sign In"

### 3. Managing Contracts

**Create Contract**:
1. Click "New Contract" button
2. Fill in contract details:
   - Title (required)
   - Description
   - Counterparty name (required)
   - Counterparty contact
   - Contract value and currency
   - Content (required)
3. Click "Create"

**View/Edit Contract**:
1. Click "View" button on any contract
2. Modal shows full contract details
3. Edit fields as needed
4. Click "Update"

**Delete Contract**:
1. Click delete icon (trash)
2. Confirm deletion

**Search & Filter**:
- Use search box to find contracts by title
- Use status dropdown to filter by contract status

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

- Authentication: `/api/v1/auth/*`
- Users: `/api/v1/users/*`
- Contracts: `/api/v1/contracts/*`
- Templates: `/api/v1/templates/*`

API client includes:
- Automatic JWT token injection
- Auto-redirect to login on 401 errors
- Error handling and display
- TypeScript type safety

## State Management

Uses Zustand for global state:

```typescript
import { useAuthStore } from './contexts/AuthContext';

// In component
const { user, login, logout, isAuthenticated } = useAuthStore();
```

Auth state persists in localStorage:
- `access_token`: JWT token
- `auth-storage`: User data

## Authentication Flow

1. User logs in → API returns JWT token
2. Token stored in localStorage
3. Axios interceptor adds token to all requests
4. On 401 error → auto-logout and redirect to login
5. Protected routes check authentication status

## Development Notes

### TypeScript Types

All API types are defined in `src/types/api.ts` matching the OpenAPI spec:
- `UserCreate`, `UserResponse`, `UserUpdate`
- `ContractCreate`, `ContractResponse`, `ContractUpdate`
- `TemplateCreate`, `TemplateResponse`, `TemplateUpdate`
- Enums: `UserRole`, `ContractStatus`

### Adding New Features

1. Add types to `src/types/api.ts`
2. Add API methods to `src/services/api.ts`
3. Create page component in `src/pages/`
4. Add route in `src/App.tsx`
5. Add menu item in `DashboardLayout.tsx`

### RBAC Implementation

```typescript
// Protect route by role
<Route
  path="/admin"
  element={
    <ProtectedRoute requiredRoles={[UserRole.ADMIN]}>
      <AdminPage />
    </ProtectedRoute>
  }
/>

// Check role in component
{user?.role === UserRole.LEGAL && (
  <Button>Legal Only Feature</Button>
)}
```

## Troubleshooting

### API Connection Issues

```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration in backend
# Ensure http://localhost:3000 is in BACKEND_CORS_ORIGINS
```

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Authentication Issues

```bash
# Clear browser storage
localStorage.clear()

# Check token in DevTools → Application → Local Storage
```

## Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Serve with nginx or other web server
# Dist files will be in: dist/
```

### Production Configuration

1. Update `.env`:
   ```env
   VITE_API_URL=https://api.yourdomain.com
   ```

2. Configure nginx:
   ```nginx
   server {
     listen 80;
     server_name yourdomain.com;
     root /path/to/dist;

     location / {
       try_files $uri /index.html;
     }

     location /api {
       proxy_pass http://backend:8000;
     }
   }
   ```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Next Steps (Phase 2)

Planned features for Phase 2:
- Template management UI
- User management (admin)
- Profile settings
- Contract version history
- Document upload
- Email notifications integration
- Teams notifications integration
- Advanced search and filtering
- Contract status workflow
- DocuSign integration UI

## Contributing

Follow the guidelines in `/CLAUDE.MD` for collaborative development.

## License

Internal use only.
