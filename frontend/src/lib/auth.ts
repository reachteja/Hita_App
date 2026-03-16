/**
 * Authentication utilities and JWT token management
 */
import { apiClient } from './api';

export const authUtils = {
  setTokens: (access: string, refresh: string) => {
    apiClient.setTokens(access, refresh);
  },

  getAccessToken: () => {
    return apiClient.getAccessToken();
  },

  isAuthenticated: () => {
    return apiClient.isAuthenticated();
  },

  logout: () => {
    apiClient.logout();
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login';
    }
  },

  checkAuth: async () => {
    try {
      const response = await apiClient.auth.profile();
      return response.data;
    } catch {
      authUtils.logout();
      return null;
    }
  },
};
