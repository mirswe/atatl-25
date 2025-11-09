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

// customer types
export type CustomerCategory = "Prospective" | "Current" | "Inactive" | null;

export interface Order {
  order_id?: string;
  order_number?: string;
  date?: string;
  amount?: number;
  description?: string;
}

export interface Customer {
  name: string | null;
  email: string | null;
  phone: string | null;
  rewardPoints: number | null;
  prevOrders: Order[] | null;
  birthday: string | null;
  interests: string[] | null;
  address: string | null;
  company: string | null;
  category: CustomerCategory;
  notes: string | null;
  paymentMethod: string | null;
  paymentLast4: string | null;
  timestamp?: string;
}

// financial data types
export type FinancialCategory =
  | "Transaction Records"
  | "Expenses"
  | "Banking"
  | "Finance Reports"
  | "Tax Documents"
  | null;

export interface FinancialTransaction {
  type: "income" | "expense" | "transfer" | "payment";
  amount: number;
  currency: string;
  date: string;
  description: string;
  notes?: string | null;
}

export interface FinancialExpense {
  type: string; // e.g., "taxes", "bills", "utilities", "rent", "supplies"
  amount: number;
  currency: string;
  date: string;
  description: string;
  notes?: string | null;
}

export interface BankStatement {
  type: "bank_statement" | "credit_card_statement";
  amount: number;
  currency: string;
  date: string;
  description: string;
  notes?: string | null;
}

export interface FinanceReport {
  type: "profit_and_loss" | "balance_sheet" | "cash_flow_statement";
  amount?: number | null;
  currency?: string | null;
  date?: string | null;
  description: string;
  notes?: string | null;
}

export interface TaxDocument {
  type: "tax_return" | "tax_form";
  amount?: number | null;
  currency?: string | null;
  date?: string | null;
  description: string;
  notes?: string | null;
}

export interface FinancialData {
  name: string | null;
  category: FinancialCategory;
  transactions: FinancialTransaction[] | null;
  expenses: FinancialExpense[] | null;
  bankStatements: BankStatement[] | null;
  financeReports: FinanceReport[] | null;
  taxDocuments: TaxDocument[] | null;
  timestamp?: string;
}


