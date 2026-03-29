/**
 * Axios API client with JWT token management
 */
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.loadTokens();
    this.setupInterceptors();
  }

  private loadTokens() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  private saveTokens(access: string, refresh: string) {
    this.accessToken = access;
    this.refreshToken = refresh;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
    }
  }

  private clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  private setupInterceptors() {
    // Request interceptor - add token to headers
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle 401 and refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry && this.refreshToken) {
          originalRequest._retry = true;

          try {
            const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
              refresh: this.refreshToken,
            });

            const { access } = response.data;
            this.accessToken = access;
            localStorage.setItem('access_token', access);

            originalRequest.headers.Authorization = `Bearer ${access}`;
            return this.client(originalRequest);
          } catch {
            this.clearTokens();
            window.location.href = '/auth/login';
            return Promise.reject(error);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  auth = {
    register: (data: { email: string; full_name: string; password: string; confirm_password: string; consent_given: boolean }) =>
      this.client.post('/auth/register/', data),
    login: (data: { email: string; password: string }) =>
      this.client.post('/auth/login/', data),
    logout: () => this.client.post('/auth/logout/'),
    profile: () => this.client.get('/auth/profile/'),
    updateProfile: (data: Partial<{ full_name: string }>) =>
      this.client.patch('/auth/profile/', data),
  };

  // Document endpoints
  documents = {
    list: (category?: string, tags?: string[]) => {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (tags && tags.length > 0) {
        tags.forEach(tag => params.append('tag', tag));
      }
      return this.client.get('/documents/', { params });
    },
    upload: (formData: FormData) =>
      this.client.post('/documents/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    get: (id: string) => this.client.get(`/documents/${id}/`),
    delete: (id: string) => this.client.delete(`/documents/${id}/`),
    updateCategory: (id: string, category: string) =>
      this.client.patch(`/documents/${id}/category/`, { category }),

    // Tag operations
    addTag: (docId: string, name: string) =>
      this.client.post(`/documents/${docId}/tags/`, { name }),
    removeTag: (docId: string, tagId: string) =>
      this.client.delete(`/documents/${docId}/tags/`, { data: { tag_id: tagId } }),
    listTags: () =>
      this.client.get('/documents/tags/'),
    deleteTag: (tagId: string) =>
      this.client.delete(`/documents/tags/${tagId}/`),
  };

  // AI endpoints
  ai = {
    query: (question: string) =>
      this.client.post('/ai/query/', { question }),
    status: (documentId: string) =>
      this.client.get('/ai/status/', { params: { document_id: documentId } }),
  };

  // Token management
  setTokens(access: string, refresh: string) {
    this.saveTokens(access, refresh);
  }

  getAccessToken() {
    return this.accessToken;
  }

  isAuthenticated() {
    return !!this.accessToken;
  }

  logout() {
    this.clearTokens();
  }
}

export const apiClient = new APIClient();
export const aiAPI = apiClient; // Alias for convenience
