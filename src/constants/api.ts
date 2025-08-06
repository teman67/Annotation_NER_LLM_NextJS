// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  API_BASE_URL:
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  TIMEOUT: 30000,
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    LOGOUT: "/auth/logout",
    SESSION: "/auth/session",
    VERIFY_EMAIL: "/auth/verify-email",
    RESEND_VERIFICATION: "/auth/resend-verification",
    FORGOT_PASSWORD: "/auth/forgot-password",
    RESET_PASSWORD: "/auth/reset-password",
  },
  USERS: {
    PROFILE: "/users/profile",
    UPDATE_PROFILE: "/users/profile",
    API_KEYS: "/users/api-keys",
    UPDATE_API_KEYS: "/users/api-keys",
    DECRYPTED_API_KEYS: "/users/api-keys/decrypted",
  },
  PROJECTS: {
    LIST: "/projects",
    CREATE: "/projects",
    GET: (id: string) => `/projects/${id}`,
    UPDATE: (id: string) => `/projects/${id}`,
    DELETE: (id: string) => `/projects/${id}`,
  },
  FILES: {
    LIST: "/files",
    UPLOAD: "/files/upload",
    GET: (id: string) => `/files/${id}`,
    DELETE: (id: string) => `/files/${id}`,
  },
  ANNOTATIONS: {
    LIST: "/annotations",
    CREATE: "/annotations",
    GET: (id: string) => `/annotations/${id}`,
    UPDATE: (id: string) => `/annotations/${id}`,
    DELETE: (id: string) => `/annotations/${id}`,
    GENERATE: "/annotations/annotate",
    ESTIMATE_COST: "/annotations/estimate-cost",
    AVAILABLE_MODELS: "/annotations/available-models",
  },
  TAGS: {
    LIST: "/tags",
    CREATE: "/tags",
    GET: (id: string) => `/tags/${id}`,
    UPDATE: (id: string) => `/tags/${id}`,
    DELETE: (id: string) => `/tags/${id}`,
  },
  DASHBOARD: {
    STATS: "/dashboard/stats",
    RECENT_ACTIVITY: "/dashboard/recent-activity",
  },
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
} as const;
