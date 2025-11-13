/**
 * Authentication Context - Manages user authentication state
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserResponse, LoginRequest, UserCreate } from '../types/api';
import { authAPI, usersAPI } from '../services/api';

interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: localStorage.getItem('access_token'),
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true, error: null });

          // Get token
          const tokenData = await authAPI.login(credentials);
          localStorage.setItem('access_token', tokenData.access_token);

          // Get user profile
          const user = await usersAPI.getCurrentUser();

          set({
            token: tokenData.access_token,
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      register: async (userData: UserCreate) => {
        try {
          set({ isLoading: true, error: null });

          // Register user
          await authAPI.register(userData);

          // Auto-login after registration
          await get().login({
            username: userData.email,
            password: userData.password,
          });

          set({ isLoading: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Registration failed';
          set({
            error: errorMessage,
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      loadUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, isLoading: false });
          return;
        }

        try {
          set({ isLoading: true });
          const user = await usersAPI.getCurrentUser();
          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          localStorage.removeItem('access_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
);
