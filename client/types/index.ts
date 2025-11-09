// some user types
export interface User {
  id: string;
  email?: string;
  name?: string;
  created_at?: string;
}

// example data types
export interface ExampleData {
  id: string;
  title: string;
  description?: string;
  created_at: string;
}

// api response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// backend api types
export interface HealthResponse {
  status: string;
  message: string;
}

export interface AIRequest {
  prompt: string;
  max_tokens?: number;
}

export interface AIResponse {
  response: string;
  tokens_used?: number;
}

export interface AgentRequest {
  message: string;
  user_id?: string;
  session_id?: string;
  file_content?: string;
}

export interface AgentResponse {
  response: string;
  session_id?: string;
}

export interface SessionStateResponse {
  session_id: string;
  customer_info?: any[];
  financial_data?: any[];
  uploaded_files?: any[];
  full_state?: Record<string, any>;
}

export interface StorageResponse {
  status: string;
  customer_info_count?: number;
  financial_data_count?: number;
  uploaded_files_count?: number;
  customer_info?: any[];
  financial_data?: any[];
  uploaded_files?: any[];
  message?: string;
}


