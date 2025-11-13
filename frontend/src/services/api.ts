/**
 * API Client - Axios instance with interceptors for authentication
 */
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import type {
  UserResponse,
  UserCreate,
  UserUpdate,
  Token,
  LoginRequest,
  TemplateResponse,
  TemplateCreate,
  TemplateUpdate,
  ContractResponse,
  ContractCreate,
  ContractUpdate,
  APIError,
} from '../types/api';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Helper function to handle API errors
export const handleAPIError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;
    return axiosError.response?.data?.detail || 'An unexpected error occurred';
  }
  return 'An unexpected error occurred';
};

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  /**
   * Register a new user
   */
  register: async (data: UserCreate): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>('/api/v1/auth/register', data);
    return response.data;
  },

  /**
   * Login user and get access token
   */
  login: async (credentials: LoginRequest): Promise<Token> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<Token>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
};

// ============================================================================
// Users API
// ============================================================================

export const usersAPI = {
  /**
   * Get current user profile
   */
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/api/v1/users/me');
    return response.data;
  },

  /**
   * List all users (admin only)
   */
  listUsers: async (skip = 0, limit = 100): Promise<UserResponse[]> => {
    const response = await apiClient.get<UserResponse[]>('/api/v1/users/', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get user by ID
   */
  getUser: async (userId: number): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>(`/api/v1/users/${userId}`);
    return response.data;
  },

  /**
   * Update user
   */
  updateUser: async (userId: number, data: UserUpdate): Promise<UserResponse> => {
    const response = await apiClient.put<UserResponse>(`/api/v1/users/${userId}`, data);
    return response.data;
  },

  /**
   * Delete user (admin only)
   */
  deleteUser: async (userId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/users/${userId}`);
  },
};

// ============================================================================
// Templates API
// ============================================================================

export const templatesAPI = {
  /**
   * Create a new template (legal/admin only)
   */
  createTemplate: async (data: TemplateCreate): Promise<TemplateResponse> => {
    const response = await apiClient.post<TemplateResponse>('/api/v1/templates/', data);
    return response.data;
  },

  /**
   * List all templates
   */
  listTemplates: async (params?: {
    skip?: number;
    limit?: number;
    category?: string;
    is_active?: boolean;
  }): Promise<TemplateResponse[]> => {
    const response = await apiClient.get<TemplateResponse[]>('/api/v1/templates/', { params });
    return response.data;
  },

  /**
   * Get template by ID
   */
  getTemplate: async (templateId: number): Promise<TemplateResponse> => {
    const response = await apiClient.get<TemplateResponse>(`/api/v1/templates/${templateId}`);
    return response.data;
  },

  /**
   * Update template (legal/admin only)
   */
  updateTemplate: async (templateId: number, data: TemplateUpdate): Promise<TemplateResponse> => {
    const response = await apiClient.put<TemplateResponse>(`/api/v1/templates/${templateId}`, data);
    return response.data;
  },

  /**
   * Delete template (legal/admin only)
   */
  deleteTemplate: async (templateId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/templates/${templateId}`);
  },
};

// ============================================================================
// Contracts API
// ============================================================================

export const contractsAPI = {
  /**
   * Create a new contract
   */
  createContract: async (data: ContractCreate): Promise<ContractResponse> => {
    const response = await apiClient.post<ContractResponse>('/api/v1/contracts/', data);
    return response.data;
  },

  /**
   * List contracts
   */
  listContracts: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    owner_id?: number;
  }): Promise<ContractResponse[]> => {
    const response = await apiClient.get<ContractResponse[]>('/api/v1/contracts/', { params });
    return response.data;
  },

  /**
   * Get contract by ID
   */
  getContract: async (contractId: number): Promise<ContractResponse> => {
    const response = await apiClient.get<ContractResponse>(`/api/v1/contracts/${contractId}`);
    return response.data;
  },

  /**
   * Update contract
   */
  updateContract: async (contractId: number, data: ContractUpdate): Promise<ContractResponse> => {
    const response = await apiClient.put<ContractResponse>(`/api/v1/contracts/${contractId}`, data);
    return response.data;
  },

  /**
   * Delete contract
   */
  deleteContract: async (contractId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/contracts/${contractId}`);
  },
};

export default apiClient;
