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


