'use client';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function HomePageContent() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const deleted      = searchParams.get('deleted');

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-50">

      {deleted && (
        <div className="bg-green-600 text-white text-center py-3 px-4 text-sm">
          ✅ Your account and all data has been permanently deleted. Thank you for using Hita.
        </div>
      )}

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">🪷</span>
              <span className="font-bold text-xl text-gray-900">Hita</span>
            </div>
            <div className="space-x-4">
              <Link href="/auth/login" className="px-4 py-2 text-gray-700 hover:text-gray-900">
                Login
              </Link>
              <Link href="/auth/register" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                Register
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Your Personal Document Buddy
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Upload bills, medical records, receipts, and more. Hita will organize and answer questions about your documents.
          </p>
          <div className="space-x-4">
            <Link href="/auth/register" className="inline-block px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold">
              Get Started
            </Link>
            <Link href="/auth/login" className="inline-block px-8 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold">
              Login
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg p-8 shadow-sm">
            <div className="text-4xl mb-4">📤</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Documents</h3>
            <p className="text-gray-600">Upload any document - PDFs, Word files, Excel sheets, images, or text.</p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-sm">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Organization</h3>
            <p className="text-gray-600">AI automatically categorizes and extracts key information from your documents.</p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-sm">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Ask Questions</h3>
            <p className="text-gray-600">Ask natural language questions and get answers from your document collection.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2025 Hita. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

// ─── Outer component — wraps with Suspense ────────────────────
export default function HomePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🪷</div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <HomePageContent />
    </Suspense>
  );
}