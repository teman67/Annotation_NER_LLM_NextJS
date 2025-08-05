import { get, post, put } from "../utils/api";
import type { User, LoginForm, RegisterForm, ApiResponse } from "../types";

// Authentication API endpoints
export const authApi = {
  // Login user
  login: async (
    credentials: LoginForm
  ): Promise<ApiResponse<{ user: User; access_token: string }>> => {
    const response = await post<
      ApiResponse<{ user: User; access_token: string }>
    >("/auth/login", credentials);

    // Store token in localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }

    return response;
  },

  // Register new user
  register: async (
    userData: RegisterForm
  ): Promise<ApiResponse<{ user: User; access_token: string }>> => {
    const response = await post<
      ApiResponse<{ user: User; access_token: string }>
    >("/auth/register", userData);

    // Store token in localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }

    return response;
  },

  // Get current user
  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    return get<ApiResponse<User>>("/auth/me");
  },

  // Logout user
  logout: async (): Promise<ApiResponse<null>> => {
    const response = await post<ApiResponse<null>>("/auth/logout");
    localStorage.removeItem("access_token");
    return response;
  },

  // Refresh access token
  refreshToken: async (): Promise<ApiResponse<{ access_token: string }>> => {
    const response = await post<ApiResponse<{ access_token: string }>>(
      "/auth/refresh"
    );

    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }

    return response;
  },

  // Update user profile
  updateProfile: async (
    userData: Partial<User>
  ): Promise<ApiResponse<User>> => {
    return put<ApiResponse<User>>("/auth/profile", userData);
  },

  // Change password
  changePassword: async (
    currentPassword: string,
    newPassword: string
  ): Promise<ApiResponse<null>> => {
    return put<ApiResponse<null>>("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};
