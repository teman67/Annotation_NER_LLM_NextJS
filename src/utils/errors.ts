// Error types
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: Record<string, unknown>;
}

// Custom error classes
export class ApiException extends Error {
  status: number;
  code?: string;
  details?: Record<string, unknown>;

  constructor(
    message: string,
    status: number = 500,
    code?: string,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiException";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class ValidationError extends Error {
  fields: Record<string, string>;

  constructor(message: string, fields: Record<string, string> = {}) {
    super(message);
    this.name = "ValidationError";
    this.fields = fields;
  }
}

// Error handling utilities
export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof ApiException) {
    return {
      message: error.message,
      status: error.status,
      code: error.code,
      details: error.details,
    };
  }

  // Handle axios errors
  if (typeof error === "object" && error !== null && "response" in error) {
    const axiosError = error as {
      response?: { status: number; data?: Record<string, unknown> };
    };
    if (axiosError.response) {
      const status = axiosError.response.status;
      const data = axiosError.response.data as
        | Record<string, unknown>
        | undefined;

      return {
        message:
          (data?.message as string) ||
          (data?.detail as string) ||
          "Server error occurred",
        status,
        code: data?.code as string,
        details: data,
      };
    }
  }

  // Handle network errors
  if (typeof error === "object" && error !== null && "request" in error) {
    return {
      message: "Network error. Please check your connection.",
      status: 0,
      code: "NETWORK_ERROR",
    };
  }

  // Handle Error instances
  if (error instanceof Error) {
    return {
      message: error.message,
      status: 500,
      code: "UNKNOWN_ERROR",
    };
  }

  // General error
  return {
    message: "An unexpected error occurred",
    status: 500,
    code: "UNKNOWN_ERROR",
  };
};

// Error message helpers
export const getErrorMessage = (error: unknown): string => {
  const apiError = handleApiError(error);
  return apiError.message;
};

export const isNetworkError = (error: unknown): boolean => {
  const apiError = handleApiError(error);
  return apiError.code === "NETWORK_ERROR" || apiError.status === 0;
};

export const isAuthError = (error: unknown): boolean => {
  const apiError = handleApiError(error);
  return apiError.status === 401 || apiError.status === 403;
};

// Validation helpers
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): boolean => {
  return password.length >= 8;
};

export const validateRequired = (value: string): boolean => {
  return value.trim().length > 0;
};
