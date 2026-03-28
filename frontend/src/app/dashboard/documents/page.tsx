'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiClient } from '@/lib/api';
import { Document } from '@/types';

const CATEGORY_ICONS: Record<string, string> = {
  grocery:     '🛒',
  medical:     '🏥',
  maintenance: '🔧',
  personal:    '📝',
  finance:     '💰',
  events:      '🎉',
  education:   '📚',
  other:       '📄',
};

const STATUS_CONFIG: Record<string, { color: string; icon: string; label: string }> = {
  uploaded:   { color: 'bg-gray-100 text-gray-600',    icon: '📤', label: 'Uploaded'   },
  processing: { color: 'bg-yellow-100 text-yellow-700', icon: '⚙️', label: 'Processing' },
  ready:      { color: 'bg-green-100 text-green-700',   icon: '✅', label: 'Ready'      },
  failed:     { color: 'bg-red-100 text-red-700',       icon: '❌', label: 'Failed'     },
  
};

export default function DocumentsPage() {
  const [documents, setDocuments]   = useState<Document[]>([]);
  const [loading, setLoading]       = useState(true);
  const [uploading, setUploading]   = useState(false);
  const [uploadMsg, setUploadMsg]   = useState('');
  const [newlyReady, setNewlyReady] = useState<string[]>([]);  // docs just turned ready
  const pollRef                     = useRef<NodeJS.Timeout | null>(null);
  const prevStatusRef               = useRef<Record<string, string>>({});

  // Fetch documents and detect status changes
  const fetchDocuments = useCallback(async () => {
    try {
      const res  = await apiClient.documents.list();
      //const docs = res.data.documents as Document[];
      const docs = (Array.isArray(res.data) 
      ? res.data 
      : (res.data?.documents || [])) as Document[];
      console.log("Fetched docs:", docs);

      // Detect which documents just became ready
      const justReady = docs.filter(doc =>
        doc.status === 'ready' &&
        prevStatusRef.current[doc.id] === 'processing'
      );

      if (justReady.length > 0) {
        setNewlyReady(prev => [...prev, ...justReady.map(d => d.id)]);
        // Clear notification after 4 seconds
        setTimeout(() => {
          setNewlyReady(prev => prev.filter(id => !justReady.map(d => d.id).includes(id)));
        }, 4000);
      }

      // Update previous status map
      prevStatusRef.current = Object.fromEntries(docs.map(d => [d.id, d.status]));
      setDocuments(docs);
    } catch {}
  }, []);

  // Initial load
  useEffect(() => {
    fetchDocuments().finally(() => setLoading(false));
  }, [fetchDocuments]);

  // Smart polling — only runs when documents are processing
  useEffect(() => {
    const hasProcessing = documents.some(
      d => d.status === 'processing' || d.status === 'uploaded'
    );

    if (hasProcessing) {
      // Start polling every 5 seconds
      pollRef.current = setInterval(fetchDocuments, 5000);
    } else {
      // Stop polling — nothing processing
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [documents, fetchDocuments]);

  // File upload handler
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true);
      setUploadMsg(`Uploading ${file.name}...`);
      try {
        const formData = new FormData();
        formData.append('file', file);
        await apiClient.documents.upload(formData);
        setUploadMsg(`✅ ${file.name} uploaded — processing started`);
        await fetchDocuments();  // refresh immediately after upload
      } catch (err: any) {
        const msg = err.response?.data?.file?.[0] ||
                    err.response?.data?.error ||
                    'Upload failed';
        setUploadMsg(`❌ ${msg}`);
      } finally {
        setUploading(false);
        setTimeout(() => setUploadMsg(''), 4000);
      }
    }
  }, [fetchDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png':  ['.png'],
      'text/plain': ['.txt'],
    },
    maxSize: 25 * 1024 * 1024,
    multiple: true,
  });

  const handleDelete = async (id: string) => {
    if (!confirm('Permanently delete this document? This cannot be undone.')) return;
    try {
      await apiClient.documents.delete(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch {
      alert('Delete failed — please try again');
    }
  };

  const processingCount = documents.filter(
    d => d.status === 'processing' || d.status === 'uploaded'
  ).length;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Documents</h1>
        {/* Live processing indicator */}
        {processingCount > 0 && (
          <div className="flex items-center gap-2 bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-2 rounded-xl text-sm">
            <span className="animate-spin">⚙️</span>
            Processing {processingCount} document{processingCount > 1 ? 's' : ''}...
            <span className="text-xs text-yellow-500">auto-updating</span>
          </div>
        )}
      </div>

      {/* Newly ready notification */}
      {newlyReady.length > 0 && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 mb-4 text-sm flex items-center gap-2 animate-pulse">
          ✅ {newlyReady.length} document{newlyReady.length > 1 ? 's' : ''} ready — you can now ask Hita about {newlyReady.length > 1 ? 'them' : 'it'}!
        </div>
      )}

      {/* Upload zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition mb-6
          ${isDragActive
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-gray-200 hover:border-indigo-300 bg-white'}`}>
        <input {...getInputProps()} />
        <div className="text-4xl mb-3">{isDragActive ? '📂' : '⬆️'}</div>
        <p className="font-medium text-gray-700">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-sm text-gray-400 mt-1">
          PDF, DOCX, XLSX, JPG, PNG, TXT · Max 25MB
        </p>
        <button className="mt-4 bg-indigo-600 text-white px-5 py-2 rounded-xl text-sm font-medium hover:bg-indigo-700 transition">
          Browse Files
        </button>
      </div>

      {/* Upload status */}
      {(uploading || uploadMsg) && (
        <div className={`rounded-xl px-4 py-3 text-sm mb-4
          ${uploadMsg.startsWith('❌')
            ? 'bg-red-50 text-red-600'
            : 'bg-indigo-50 text-indigo-700'}`}>
          {uploading && <span className="mr-2 animate-spin inline-block">⏳</span>}
          {uploadMsg || 'Uploading...'}
        </div>
      )}

      {/* Document list */}
      {loading ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-3 animate-spin">⚙️</div>
          <p className="text-gray-400">Loading documents...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
          <div className="text-5xl mb-4">📭</div>
          <p className="text-gray-500">No documents yet. Upload your first one above!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => {
            const statusCfg = STATUS_CONFIG[doc.status] || {
              color: 'bg-gray-100 text-gray-600',
              icon: '📄',
              label: doc.status || 'Unknown'
        };
            const isNew      = newlyReady.includes(doc.id);
            const isProcessing = doc.status === 'processing' || doc.status === 'uploaded';

            return (
              <div
                key={doc.id}
                className={`bg-white border rounded-2xl px-6 py-4 flex items-center justify-between transition
                  ${isNew ? 'border-green-300 shadow-md shadow-green-50' : 'border-gray-100 hover:shadow-sm'}
                `}>
                <div className="flex items-center gap-4">
                  {/* Category icon */}
                  <span className="text-2xl">
                    {CATEGORY_ICONS[doc.category] || '📄'}
                  </span>

                  <div>
                    <div className="font-medium text-gray-800 flex items-center gap-2">
                      {doc.original_name}
                      {isNew && (
                        <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">
                          Just ready!
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {doc.category}
                      {doc.extracted_vendor  && ` · ${doc.extracted_vendor}`}
                      {doc.extracted_amount  && ` · ₹${doc.extracted_amount}`}
                      {doc.extracted_date    && ` · ${doc.extracted_date}`}
                      {` · ${new Date(doc.created_at).toLocaleDateString('en-IN')}`}
                    </div>
                    {doc.summary && (
                      <div className="text-xs text-gray-500 mt-1 max-w-lg truncate">
                        {doc.summary}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Status badge */}
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1
                    ${statusCfg.color}`}>
                    {isProcessing && (
                      <span className="animate-spin inline-block text-xs">⚙️</span>
                    )}
                    {statusCfg.label}
                  </span>

                  {/* Delete button */}
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-gray-300 hover:text-red-400 transition text-lg"
                    title="Delete document">
                    🗑️
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer — polling indicator */}
      {processingCount > 0 && (
        <p className="text-center text-xs text-gray-400 mt-6">
          🔄 Page updates automatically every 5 seconds
        </p>
      )}
    </div>
  );
}