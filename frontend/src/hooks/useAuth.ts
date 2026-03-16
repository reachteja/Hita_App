/**
 * Authentication hook for use in components
 */
'use client';
import { useState, useEffect } from 'react';
import { HitaUser } from '@/types';
import { authUtils } from '@/lib/auth';

export function useAuth() {
  const [user, setUser] = useState<HitaUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (authUtils.isAuthenticated()) {
          const userData = await authUtils.checkAuth();
          if (userData) {
            setUser(userData);
            setIsAuthenticated(true);
          } else {
            setIsAuthenticated(false);
          }
        }
      } catch {
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return { user, loading, isAuthenticated };
}
