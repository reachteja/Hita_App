'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';



export default function SettingsPage() {
  const router   = useRouter();
  const { user } = useAuth();
  
  const [showDeleteSection, setShowDeleteSection] = useState(false);
  const [confirmEmail, setConfirmEmail]           = useState('');
  const [deleting, setDeleting]                   = useState(false);
  const [error, setError]                         = useState('');

  const handleDeleteAccount = async () => {
    if (!confirmEmail) {
      setError('Please type your email to confirm');
      return;
    }
    if (confirmEmail.toLowerCase() !== user?.email.toLowerCase()) {
      setError('Email does not match your account email');
      return;
    }

    setDeleting(true);
    setError('');

    try {
      const refreshToken = localStorage.getItem('refresh_token') || '';
      await apiClient.auth.deleteAccount(confirmEmail, refreshToken);

      // Clear all local data
      localStorage.clear();

      // Redirect to landing page with message
      router.push('/?deleted=true');
    } catch (err: any) {
      setError(
        err.response?.data?.error || 'Deletion failed. Please try again.'
      );
      setDeleting(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-800 mb-8">Settings</h1>

      {/* Profile section */}
      <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-6">
        <h2 className="font-semibold text-gray-700 mb-4">Account</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-gray-50">
            <span className="text-sm text-gray-500">Name</span>
            <span className="text-sm font-medium text-gray-800">{user?.full_name}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-gray-50">
            <span className="text-sm text-gray-500">Email</span>
            <span className="text-sm font-medium text-gray-800">{user?.email}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-sm text-gray-500">Member since</span>
            <span className="text-sm font-medium text-gray-800">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric', month: 'long', year: 'numeric'
                  })
                : '—'}
            </span>
          </div>
        </div>
      </div>

      {/* Privacy section */}
      <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-6">
        <h2 className="font-semibold text-gray-700 mb-2">Privacy & Data</h2>
        <p className="text-sm text-gray-500 mb-4">
          In compliance with India's DPDP Act 2023, you have the right to
          access, correct, and delete all your personal data.
        </p>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="text-green-500">✅</span>
            Your documents are encrypted at rest (AES-256)
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="text-green-500">✅</span>
            Personal identifiers removed before AI processing
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="text-green-500">✅</span>
            Data stored in Asia Pacific region
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="text-green-500">✅</span>
            Your data is never sold or shared
          </div>
        </div>
      </div>

      {/* Danger zone */}
      <div className="bg-white border border-red-100 rounded-2xl p-6">
        <h2 className="font-semibold text-red-600 mb-1">Danger zone</h2>
        <p className="text-sm text-gray-500 mb-4">
          These actions are permanent and cannot be undone.
        </p>

        {!showDeleteSection ? (
          <button
            onClick={() => setShowDeleteSection(true)}
            className="px-4 py-2 text-sm text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition">
            Delete my account
          </button>
        ) : (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">

            <h3 className="font-semibold text-red-700 mb-2">
              Permanently delete account
            </h3>

            <p className="text-sm text-red-600 mb-4 leading-relaxed">
              This will permanently delete:
            </p>

            <ul className="text-sm text-red-600 mb-4 space-y-1 ml-4">
              <li>• All your uploaded documents and files</li>
              <li>• All AI-extracted data and embeddings</li>
              <li>• All tags and categories</li>
              <li>• Your account and profile</li>
            </ul>

            <p className="text-sm text-red-700 font-medium mb-3">
              This action cannot be undone. Type your email to confirm:
            </p>

            <input
              type="email"
              value={confirmEmail}
              onChange={e => setConfirmEmail(e.target.value)}
              placeholder={user?.email}
              className="w-full border border-red-300 rounded-xl px-4 py-2.5 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white"
            />

            {error && (
              <div className="text-sm text-red-600 mb-3 flex items-center gap-2">
                ⚠️ {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleDeleteAccount}
                disabled={deleting || !confirmEmail}
                className="px-5 py-2.5 bg-red-600 text-white text-sm font-medium rounded-xl hover:bg-red-700 transition disabled:opacity-50">
                {deleting ? 'Deleting everything...' : 'Delete my account permanently'}
              </button>
              <button
                onClick={() => {
                  setShowDeleteSection(false);
                  setConfirmEmail('');
                  setError('');
                }}
                className="px-5 py-2.5 text-sm text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50 transition">
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}