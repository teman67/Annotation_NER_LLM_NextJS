// User and Authentication types
export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  settings: ProjectSettings;
}

export interface ProjectSettings {
  llm_provider: "openai" | "anthropic";
  model_name: string;
  max_tokens: number;
  temperature: number;
  cost_limit?: number;
}

// File types
export interface ProjectFile {
  id: string;
  project_id: string;
  filename: string;
  content: string;
  file_size: number;
  uploaded_at: string;
  processed: boolean;
  chunks?: TextChunk[];
}

export interface TextChunk {
  id: string;
  file_id: string;
  content: string;
  start_index: number;
  end_index: number;
  chunk_index: number;
}

// Tag types
export interface Tag {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  color: string;
  created_at: string;
  is_active: boolean;
}

// Annotation types
export interface Annotation {
  id: string;
  file_id: string;
  project_id: string;
  text: string;
  start_index: number;
  end_index: number;
  tag_id: string;
  tag: Tag;
  confidence: number;
  is_ai_generated: boolean;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface AnnotationRequest {
  file_id: string;
  content: string;
  tags: string[];
  llm_provider: "openai" | "anthropic";
  model_name: string;
  max_tokens?: number;
  temperature?: number;
}

export interface AnnotationResponse {
  annotations: Annotation[];
  cost: number;
  tokens_used: number;
  processing_time: number;
}

// Cost tracking types
export interface CostCalculation {
  input_tokens: number;
  output_tokens: number;
  total_cost: number;
  provider: string;
  model: string;
}

export interface UsageStats {
  total_annotations: number;
  total_cost: number;
  tokens_used: number;
  files_processed: number;
  average_confidence: number;
  period_start: string;
  period_end: string;
}

// Export types
export interface ExportOptions {
  format: "json" | "csv" | "conll";
  include_metadata: boolean;
  include_confidence: boolean;
  filter_by_tags?: string[];
  min_confidence?: number;
}

export interface ExportResult {
  download_url: string;
  filename: string;
  file_size: number;
  created_at: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  fullName?: string;
}

export interface ProjectForm {
  name: string;
  description?: string;
  is_public: boolean;
  settings: ProjectSettings;
}

export interface TagForm {
  name: string;
  description?: string;
  color: string;
}

// UI State types
export interface LoadingState {
  [key: string]: boolean;
}

export interface ErrorState {
  [key: string]: string | null;
}

// Dashboard types
export interface DashboardStats {
  total_projects: number;
  total_files: number;
  total_annotations: number;
  total_cost: number;
  recent_activity: Activity[];
}

export interface Activity {
  id: string;
  type:
    | "project_created"
    | "file_uploaded"
    | "annotation_completed"
    | "export_generated";
  description: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

// LLM Configuration types
export interface LLMProvider {
  id: "openai" | "anthropic";
  name: string;
  models: LLMModel[];
  pricing: LLMPricing;
}

export interface LLMModel {
  id: string;
  name: string;
  max_tokens: number;
  description?: string;
}

export interface LLMPricing {
  input_token_price: number;
  output_token_price: number;
  currency: string;
}
