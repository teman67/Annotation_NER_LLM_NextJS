import { createContext } from "react";
import type { User, LoginForm, RegisterForm } from "../types";

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (credentials: LoginForm) => Promise<void>;
  signUp: (userData: RegisterForm) => Promise<void>;
  signOut: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);
