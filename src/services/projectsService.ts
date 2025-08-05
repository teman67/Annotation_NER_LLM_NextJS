import { get, post, put, del } from "../utils/api";
import type {
  Project,
  ProjectForm,
  ApiResponse,
  PaginatedResponse,
} from "../types";

// Projects API endpoints
export const projectsApi = {
  // Get all projects for current user
  getProjects: async (
    page = 1,
    perPage = 10
  ): Promise<PaginatedResponse<Project>> => {
    return get<PaginatedResponse<Project>>(
      `/projects?page=${page}&per_page=${perPage}`
    );
  },

  // Get single project by ID
  getProject: async (projectId: string): Promise<ApiResponse<Project>> => {
    return get<ApiResponse<Project>>(`/projects/${projectId}`);
  },

  // Create new project
  createProject: async (
    projectData: ProjectForm
  ): Promise<ApiResponse<Project>> => {
    return post<ApiResponse<Project>>("/projects", projectData);
  },

  // Update existing project
  updateProject: async (
    projectId: string,
    projectData: Partial<ProjectForm>
  ): Promise<ApiResponse<Project>> => {
    return put<ApiResponse<Project>>(`/projects/${projectId}`, projectData);
  },

  // Delete project
  deleteProject: async (projectId: string): Promise<ApiResponse<null>> => {
    return del<ApiResponse<null>>(`/projects/${projectId}`);
  },

  // Get project statistics
  getProjectStats: async (
    projectId: string
  ): Promise<
    ApiResponse<{
      total_files: number;
      total_annotations: number;
      total_cost: number;
      last_activity: string;
    }>
  > => {
    return get<
      ApiResponse<{
        total_files: number;
        total_annotations: number;
        total_cost: number;
        last_activity: string;
      }>
    >(`/projects/${projectId}/stats`);
  },

  // Get project members (for collaboration)
  getProjectMembers: async (
    projectId: string
  ): Promise<
    ApiResponse<
      Array<{
        user_id: string;
        email: string;
        full_name: string;
        role: "owner" | "collaborator" | "viewer";
        added_at: string;
      }>
    >
  > => {
    return get<
      ApiResponse<
        Array<{
          user_id: string;
          email: string;
          full_name: string;
          role: "owner" | "collaborator" | "viewer";
          added_at: string;
        }>
      >
    >(`/projects/${projectId}/members`);
  },

  // Add project member
  addProjectMember: async (
    projectId: string,
    email: string,
    role: "collaborator" | "viewer"
  ): Promise<ApiResponse<null>> => {
    return post<ApiResponse<null>>(`/projects/${projectId}/members`, {
      email,
      role,
    });
  },

  // Remove project member
  removeProjectMember: async (
    projectId: string,
    userId: string
  ): Promise<ApiResponse<null>> => {
    return del<ApiResponse<null>>(`/projects/${projectId}/members/${userId}`);
  },

  // Update member role
  updateMemberRole: async (
    projectId: string,
    userId: string,
    role: "collaborator" | "viewer"
  ): Promise<ApiResponse<null>> => {
    return put<ApiResponse<null>>(`/projects/${projectId}/members/${userId}`, {
      role,
    });
  },
};
