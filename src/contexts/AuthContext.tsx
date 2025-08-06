import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import type { User, LoginForm, RegisterForm } from "../types";
import { getErrorMessage } from "../utils/errors";
import { API_CONFIG, API_ENDPOINTS } from "../constants/api";
import { AuthContext, type AuthContextType } from "./AuthContextType";

// Convert backend user response to our User type
const convertUser = (user: Record<string, unknown>): User => ({
  id: user.id as string,
  email: (user.email as string) || "",
  full_name: (user.full_name as string) || "",
  avatar_url: (user.avatar_url as string) || "",
  created_at: user.created_at as string,
  updated_at: (user.updated_at as string) || (user.created_at as string),
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session from backend
    const getSession = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem("access_token");
        const headers: Record<string, string> = {};

        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch(
          `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.SESSION}`,
          {
            credentials: "include",
            headers,
          }
        );

        if (res.ok) {
          const data = await res.json();
          setUser(data.user ? convertUser(data.user) : null);
        } else if (res.status === 401) {
          // Token is invalid, clear it
          localStorage.removeItem("access_token");
          setUser(null);
        } else {
          setUser(null);
        }
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    getSession();
  }, []);

  const signIn = async (credentials: LoginForm): Promise<void> => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(credentials),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const errorMessage =
          errorData.message ||
          errorData.detail ||
          (res.status === 401 ? "Invalid credentials" : "Server error");
        throw new Error(errorMessage);
      }

      const data = await res.json();

      // Store the access token if provided
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
      }

      setUser(data.user ? convertUser(data.user) : null);
      toast.success("Successfully signed in!");
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (userData: RegisterForm): Promise<void> => {
    setLoading(true);
    try {
      if (userData.password !== userData.confirmPassword) {
        throw new Error("Passwords do not match");
      }

      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.REGISTER}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            email: userData.email,
            password: userData.password,
            full_name: userData.fullName || "",
          }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const errorMessage =
          errorData.message || errorData.detail || "Failed to sign up";
        throw new Error(errorMessage);
      }

      const data = await res.json();
      if (data.verification_required) {
        toast.success(
          "Registration successful! Please check your email to verify your account."
        );
      } else {
        setUser(data.user ? convertUser(data.user) : null);
        toast.success("Registration successful!");
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async (): Promise<void> => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.LOGOUT}`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const errorMessage =
          errorData.message || errorData.detail || "Failed to sign out";
        throw new Error(errorMessage);
      }

      // Clear the access token
      localStorage.removeItem("access_token");
      setUser(null);
      toast.success("Successfully signed out!");
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (userData: Partial<User>): Promise<void> => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.USERS.UPDATE_PROFILE}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(userData),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const errorMessage =
          errorData.message || errorData.detail || "Failed to update profile";
        throw new Error(errorMessage);
      }

      const data = await res.json();
      setUser(data.user ? convertUser(data.user) : null);
      toast.success("Profile updated successfully!");
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const verifyEmail = async (token: string): Promise<void> => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.VERIFY_EMAIL}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ token }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));

        // Handle rate limiting specifically
        if (res.status === 429) {
          const errorMessage =
            errorData.message ||
            "Too many verification attempts. Please wait before trying again.";
          toast.error(errorMessage, { duration: 5000 });
          throw new Error(errorMessage);
        }

        const errorMessage =
          errorData.message || errorData.detail || "Failed to verify email";
        throw new Error(errorMessage);
      }

      const data = await res.json();

      // Handle successful verification or already verified case
      if (data.user) {
        setUser(convertUser(data.user));

        // Store access token if provided
        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token);
        }

        // Show appropriate success message
        if (data.message?.includes("already verified")) {
          toast.success("Email is already verified! You are logged in.");
        } else {
          toast.success("Email verified successfully! You are now logged in.");
        }
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      // Don't show toast again for rate limiting as we already showed it above
      if (!errorMessage.includes("Too many")) {
        toast.error(errorMessage);
      }
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const resendVerification = async (email: string): Promise<void> => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.RESEND_VERIFICATION}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const errorMessage =
          errorData.message ||
          errorData.detail ||
          "Failed to resend verification";
        throw new Error(errorMessage);
      }

      toast.success("Verification email sent! Please check your inbox.");
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    updateProfile,
    verifyEmail,
    resendVerification,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
