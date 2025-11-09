import {
  AgentRequest,
  AgentResponse,
  SessionStateResponse,
  StorageResponse,
  HealthResponse,
  Customer,
  CustomerCategory,
} from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Debug logging (remove in production)
if (typeof window !== "undefined") {
  console.log("API Base URL:", API_BASE_URL);
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Debug logging
  if (typeof window !== "undefined") {
    console.log(`[API] Fetching: ${url}`, { method: options?.method || "GET" });
  }
  
  // Only set Content-Type for requests with a body
  const hasBody = options?.body !== undefined && options?.body !== null;
  const headers: Record<string, string> = {};
  
  // Copy existing headers
  if (options?.headers) {
    if (options.headers instanceof Headers) {
      options.headers.forEach((value, key) => {
        headers[key] = value;
      });
    } else if (Array.isArray(options.headers)) {
      options.headers.forEach(([key, value]) => {
        headers[key] = value;
      });
    } else {
      Object.assign(headers, options.headers);
    }
  }
  
  // Set Content-Type only if there's a body and it's not already set
  if (hasBody && !headers["Content-Type"] && !headers["content-type"]) {
    headers["Content-Type"] = "application/json";
  }
  
  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    // Network error (connection refused, DNS failure, etc.)
    throw new Error(
      `Network error: ${error instanceof Error ? error.message : "Failed to connect to server. Make sure the backend is running on ${API_BASE_URL}."}`
    );
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `API Error (${response.status}): ${errorText || response.statusText}`
    );
  }

  try {
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Expected JSON response but got: ${contentType || "unknown"}. Response: ${text.substring(0, 100)}`);
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes("Expected JSON")) {
      throw error;
    }
    throw new Error(
      `Failed to parse response as JSON: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  }
}

export async function chatWithAgent(
  message: string,
  sessionId?: string,
  fileContent?: string,
  userId?: string
): Promise<AgentResponse> {
  const request: AgentRequest = {
    message,
    session_id: sessionId,
    file_content: fileContent,
    user_id: userId,
  };

  return fetchAPI<AgentResponse>("/api/agent/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function chatWithCustomerAgent(
  message: string,
  sessionId?: string,
  fileContent?: string,
  userId?: string
): Promise<AgentResponse> {
  const request: AgentRequest = {
    message,
    session_id: sessionId,
    file_content: fileContent,
    user_id: userId,
  };

  return fetchAPI<AgentResponse>("/api/agent/customer", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function chatWithFinanceAgent(
  message: string,
  sessionId?: string,
  fileContent?: string,
  userId?: string
): Promise<AgentResponse> {
  const request: AgentRequest = {
    message,
    session_id: sessionId,
    file_content: fileContent,
    user_id: userId,
  };

  return fetchAPI<AgentResponse>("/api/agent/finance", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getSessionState(
  sessionId: string,
  userId?: string
): Promise<SessionStateResponse> {
  const params = new URLSearchParams();
  if (userId) {
    params.append("user_id", userId);
  }

  const queryString = params.toString();
  const endpoint = `/api/agent/session/${sessionId}${queryString ? `?${queryString}` : ""}`;

  return fetchAPI<SessionStateResponse>(endpoint, {
    method: "GET",
  });
}

export async function getStorage(): Promise<StorageResponse> {
  return fetchAPI<StorageResponse>("/api/storage", {
    method: "GET",
  });
}

export async function clearStorage(): Promise<StorageResponse> {
  return fetchAPI<StorageResponse>("/api/storage", {
    method: "DELETE",
  });
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchAPI<HealthResponse>("/health", {
    method: "GET",
  });
}

export interface CustomersResponse {
  status: string;
  count: number;
  customers: Customer[];
}

export interface CustomerStatsResponse {
  status: string;
  stats: {
    total: number;
    prospective: number;
    current: number;
    inactive: number;
    uncategorized: number;
  };
}

export async function getCustomers(
  category?: CustomerCategory
): Promise<CustomersResponse> {
  const params = new URLSearchParams();
  if (category) {
    params.append("category", category);
  }

  const queryString = params.toString();
  const endpoint = `/api/customers${queryString ? `?${queryString}` : ""}`;

  return fetchAPI<CustomersResponse>(endpoint, {
    method: "GET",
  });
}

export async function getCustomer(
  customerId: string
): Promise<{ status: string; customer: Customer }> {
  return fetchAPI<{ status: string; customer: Customer }>(
    `/api/customers/${encodeURIComponent(customerId)}`,
    {
      method: "GET",
    }
  );
}

export async function getCustomerStats(): Promise<CustomerStatsResponse> {
  return fetchAPI<CustomerStatsResponse>("/api/customers/stats", {
    method: "GET",
  });
}

export async function updateAllCustomersCategory(
  category: CustomerCategory
): Promise<{ status: string; message: string; updated_count: number; category: string }> {
  if (!category) {
    throw new Error("Category is required");
  }
  
  return fetchAPI<{ status: string; message: string; updated_count: number; category: string }>(
    "/api/customers/update-category",
    {
      method: "POST",
      body: JSON.stringify({ category }),
    }
  );
}

