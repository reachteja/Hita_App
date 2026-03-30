'use client';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { apiClient } from '@/lib/api';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🪷</div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl mr-3">🪷</span>
              <h1 className="text-xl font-bold text-gray-900">Hita</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link href="/dashboard/documents" className="text-gray-600 hover:text-gray-900">Documents</Link>
              <Link href="/dashboard/ask" className="text-gray-600 hover:text-gray-900">Ask Hita</Link>
              <Link href="/dashboard/settings" className="text-gray-600 hover:text-gray-900">⚙️ Settings</Link>
              <button
                onClick={async () => {
                  try {
                    const refresh = localStorage.getItem('refresh_token');
                    if (refresh) {
                      await apiClient.auth.logout(refresh);
                    }
                  } catch {}
                  localStorage.clear();
                  router.push('/auth/login');
                }}
                className="px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200"
              >
                Logout
              </button>
             
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
