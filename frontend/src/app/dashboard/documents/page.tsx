'use client';
import { useState } from 'react';
import { useDocuments } from '@/hooks/useDocuments';
import { useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function DocumentsPage() {
  const searchParams = useSearchParams();
  const category = searchParams.get('category');
  const { documents, loading, error, fetchDocuments, deleteDocument } = useDocuments(category || undefined);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      await apiClient.documents.upload(formData);
      fetchDocuments();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading documents...</div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        {category && <p className="text-gray-600 mt-1">Category: <span className="font-semibold">{category}</span></p>}
      </div>

      {/* Upload zone */}
      <div className="bg-white rounded-lg shadow p-8 mb-8">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <div className="text-center">
            <span className="text-4xl mb-4 block">📄</span>
            <p className="text-gray-700 mb-4">Drag and drop your document here, or click to browse</p>
            <label className="inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer">
              Choose file
              <input
                type="file"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
                accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png,.txt"
              />
            </label>
          </div>
          {uploading && <p className="text-center text-gray-600 mt-4">Uploading...</p>}
          {uploadError && <p className="text-center text-red-600 mt-4">{uploadError}</p>}
        </div>
      </div>

      {/* Documents list */}
      {error && <div className="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>}

      {documents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <span className="text-4xl mb-4 block">📂</span>
          <p className="text-gray-600">No documents yet</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Category</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Date</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Action</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div>{doc.original_name}</div>
                    {doc.error_message && (
                      <div className="text-xs text-red-600 mt-1">⚠️ {doc.error_message.substring(0, 80)}...</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className="inline-block px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-xs font-semibold capitalize">
                      {doc.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-1">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        doc.status === 'processed' ? 'bg-green-50 text-green-600' :
                        doc.status === 'processing' ? 'bg-yellow-50 text-yellow-600' :
                        doc.status === 'failed' ? 'bg-red-50 text-red-600' :
                        doc.status === 'awaiting_ocr' ? 'bg-orange-50 text-orange-600' :
                        'bg-gray-50 text-gray-600'
                      }`}>
                        {doc.status === 'processing' ? '⏳ Processing' :
                         doc.status === 'processed' ? '✅ Ready' :
                         doc.status === 'failed' ? '❌ Failed' :
                         doc.status === 'awaiting_ocr' ? '📸 Needs OCR' :
                         doc.status}
                      </span>
                      {doc.error_message && (
                        <div className="group relative">
                          <button className="text-blue-600 hover:text-blue-800 text-lg" title="View error">?</button>
                          <div className="hidden group-hover:block absolute z-10 bg-gray-900 text-white text-xs px-3 py-2 rounded whitespace-nowrap mb-2">
                            {doc.error_message}
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="text-red-600 hover:text-red-900 text-sm font-semibold"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
