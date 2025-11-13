/**
 * Main App Component - Routing and Layout
 */
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { useAuthStore } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/DashboardLayout';
import { LoginPage } from './pages/Login';
import { RegisterPage } from './pages/Register';
import { ContractsPage } from './pages/Contracts';

function App() {
  const { loadUser, isAuthenticated } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, []);

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/dashboard/contracts" replace /> : <LoginPage />
            }
          />
          <Route
            path="/register"
            element={
              isAuthenticated ? <Navigate to="/dashboard/contracts" replace /> : <RegisterPage />
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard/contracts" replace />} />
            <Route path="contracts" element={<ContractsPage />} />
            <Route
              path="templates"
              element={
                <div style={{ textAlign: 'center', padding: '50px' }}>
                  <h2>Templates (Coming in Phase 2)</h2>
                  <p>Template management features will be available in the next phase.</p>
                </div>
              }
            />
            <Route
              path="users"
              element={
                <div style={{ textAlign: 'center', padding: '50px' }}>
                  <h2>User Management (Coming in Phase 2)</h2>
                  <p>User management features will be available in the next phase.</p>
                </div>
              }
            />
            <Route
              path="profile"
              element={
                <div style={{ textAlign: 'center', padding: '50px' }}>
                  <h2>Profile Settings (Coming in Phase 2)</h2>
                  <p>Profile management will be available in the next phase.</p>
                </div>
              }
            />
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="*"
            element={
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/dashboard">Go to Dashboard</a>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
