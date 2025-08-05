import { get, post, put, del } from "../utils/api";
import type {
  Annotation,
  AnnotationRequest,
  AnnotationResponse,
  ApiResponse,
  PaginatedResponse,
  ExportOptions,
  ExportResult,
} from "../types";

// Annotations API endpoints
export const annotationsApi = {
  // Generate AI annotations for text
  generateAnnotations: async (
    request: AnnotationRequest
  ): Promise<AnnotationResponse> => {
    return post<AnnotationResponse>("/annotations/generate", request);
  },

  // Get annotations for a project
  getProjectAnnotations: async (
    projectId: string,
    page = 1,
    perPage = 50,
    filters?: {
      file_id?: string;
      tag_id?: string;
      is_approved?: boolean;
      min_confidence?: number;
    }
  ): Promise<PaginatedResponse<Annotation>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }

    return get<PaginatedResponse<Annotation>>(
      `/annotations/project/${projectId}?${params.toString()}`
    );
  },

  // Get annotations for a specific file
  getFileAnnotations: async (
    fileId: string
  ): Promise<ApiResponse<Annotation[]>> => {
    return get<ApiResponse<Annotation[]>>(`/annotations/file/${fileId}`);
  },

  // Save manual annotation
  createAnnotation: async (
    annotation: Omit<Annotation, "id" | "created_at" | "updated_at">
  ): Promise<ApiResponse<Annotation>> => {
    return post<ApiResponse<Annotation>>("/annotations", annotation);
  },

  // Update annotation
  updateAnnotation: async (
    annotationId: string,
    data: Partial<Annotation>
  ): Promise<ApiResponse<Annotation>> => {
    return put<ApiResponse<Annotation>>(`/annotations/${annotationId}`, data);
  },

  // Delete annotation
  deleteAnnotation: async (
    annotationId: string
  ): Promise<ApiResponse<null>> => {
    return del<ApiResponse<null>>(`/annotations/${annotationId}`);
  },

  // Approve annotation
  approveAnnotation: async (
    annotationId: string
  ): Promise<ApiResponse<Annotation>> => {
    return put<ApiResponse<Annotation>>(
      `/annotations/${annotationId}/approve`,
      {}
    );
  },

  // Reject annotation
  rejectAnnotation: async (
    annotationId: string
  ): Promise<ApiResponse<null>> => {
    return del<ApiResponse<null>>(`/annotations/${annotationId}/reject`);
  },

  // Bulk approve annotations
  bulkApproveAnnotations: async (
    annotationIds: string[]
  ): Promise<
    ApiResponse<{
      approved: number;
      failed: number;
    }>
  > => {
    return post<
      ApiResponse<{
        approved: number;
        failed: number;
      }>
    >("/annotations/bulk-approve", {
      annotation_ids: annotationIds,
    });
  },

  // Bulk delete annotations
  bulkDeleteAnnotations: async (
    annotationIds: string[]
  ): Promise<
    ApiResponse<{
      deleted: number;
      failed: number;
    }>
  > => {
    return post<
      ApiResponse<{
        deleted: number;
        failed: number;
      }>
    >("/annotations/bulk-delete", {
      annotation_ids: annotationIds,
    });
  },

  // Export annotations
  exportAnnotations: async (
    projectId: string,
    options: ExportOptions
  ): Promise<ApiResponse<ExportResult>> => {
    return post<ApiResponse<ExportResult>>(
      `/annotations/export/${projectId}`,
      options
    );
  },

  // Get annotation statistics
  getAnnotationStats: async (
    projectId: string,
    timeRange?: {
      start_date: string;
      end_date: string;
    }
  ): Promise<
    ApiResponse<{
      total_annotations: number;
      approved_annotations: number;
      ai_generated: number;
      manual: number;
      average_confidence: number;
      annotations_by_tag: Array<{
        tag_name: string;
        count: number;
      }>;
      annotations_by_date: Array<{
        date: string;
        count: number;
      }>;
    }>
  > => {
    const params = timeRange
      ? new URLSearchParams({
          start_date: timeRange.start_date,
          end_date: timeRange.end_date,
        }).toString()
      : "";

    return get<
      ApiResponse<{
        total_annotations: number;
        approved_annotations: number;
        ai_generated: number;
        manual: number;
        average_confidence: number;
        annotations_by_tag: Array<{
          tag_name: string;
          count: number;
        }>;
        annotations_by_date: Array<{
          date: string;
          count: number;
        }>;
      }>
    >(`/annotations/stats/${projectId}${params ? `?${params}` : ""}`);
  },
};
