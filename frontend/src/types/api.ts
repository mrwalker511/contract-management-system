/**
 * API Types - Generated from OpenAPI Specification
 * Contract Management System API v1.0.0
 */

// Enums
export enum UserRole {
  PROCUREMENT = 'procurement',
  LEGAL = 'legal',
  FINANCE = 'finance',
  ADMIN = 'admin',
}

export enum ContractStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  PENDING_SIGNATURE = 'pending_signature',
  SIGNED = 'signed',
  ACTIVE = 'active',
  EXPIRED = 'expired',
  TERMINATED = 'terminated',
  REJECTED = 'rejected',
}

// User Types
export interface UserCreate {
  email: string;
  full_name: string;
  role: UserRole;
  password: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  role?: UserRole;
  password?: string;
  is_active?: boolean;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}

// Authentication Types
export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;  // email
  password: string;
}

// Template Types
export interface TemplateCreate {
  name: string;
  description?: string | null;
  content: string;
  category?: string | null;
}

export interface TemplateUpdate {
  name?: string;
  description?: string | null;
  content?: string;
  category?: string | null;
  is_active?: boolean;
}

export interface TemplateResponse {
  id: number;
  name: string;
  description?: string | null;
  content: string;
  category?: string | null;
  is_active: boolean;
  created_by_id: number;
  created_at: string;
  updated_at?: string | null;
}

// Contract Types
export interface ContractCreate {
  title: string;
  description?: string | null;
  content: string;
  contract_number?: string | null;
  contract_value?: number | null;
  currency?: string;
  counterparty_name: string;
  counterparty_contact?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  template_id?: number | null;
}

export interface ContractUpdate {
  title?: string;
  description?: string | null;
  content?: string;
  status?: ContractStatus;
  contract_value?: number | null;
  currency?: string;
  counterparty_name?: string;
  counterparty_contact?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  signature_date?: string | null;
}

export interface ContractResponse {
  id: number;
  title: string;
  description?: string | null;
  content: string;
  contract_number?: string | null;
  status: ContractStatus;
  contract_value?: number | null;
  currency: string;
  counterparty_name: string;
  counterparty_contact?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  signature_date?: string | null;
  docusign_envelope_id?: string | null;
  docusign_status?: string | null;
  owner_id: number;
  template_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// Error Types
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface APIError {
  detail: string;
}

// List Response Types (for pagination support)
export type UserList = UserResponse[];
export type TemplateList = TemplateResponse[];
export type ContractList = ContractResponse[];
