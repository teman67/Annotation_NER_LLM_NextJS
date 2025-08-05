import axios from "axios";
import type { AxiosResponse, AxiosProgressEvent } from "axios";
import type { ApiResponse, ApiError } from "../types";
import { API_CONFIG } from "../constants/api";

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_CONFIG.API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Important for cookie-based auth
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Generic API call wrapper
export const apiCall = async <T>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  url: string,
  data?: unknown,
  config?: object
): Promise<T> => {
  try {
    const response = await apiClient({
      method,
      url,
      data,
      ...config,
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || error.message,
        code: error.response?.data?.code || error.code,
      };
      throw apiError;
    }
    throw error;
  }
};

// Utility functions for common HTTP methods
export const get = <T>(url: string, config?: object): Promise<T> =>
  apiCall<T>("GET", url, undefined, config);

export const post = <T>(
  url: string,
  data?: unknown,
  config?: object
): Promise<T> => apiCall<T>("POST", url, data, config);

export const put = <T>(
  url: string,
  data?: unknown,
  config?: object
): Promise<T> => apiCall<T>("PUT", url, data, config);

export const del = <T>(url: string, config?: object): Promise<T> =>
  apiCall<T>("DELETE", url, undefined, config);

// File upload utility
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<ApiResponse<unknown>> => {
  const formData = new FormData();
  formData.append("file", file);

  return apiCall("POST", url, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = (progressEvent.loaded / progressEvent.total) * 100;
        onProgress(progress);
      }
    },
  });
};

export default apiClient;
