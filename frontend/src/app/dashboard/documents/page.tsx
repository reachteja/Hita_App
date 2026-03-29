'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { Document, Tag } from '@/types';

const CATEGORY_ICONS: Record<string, string> = {
  grocery: '🛒', medical: '🏥', maintenance: '🔧',
  personal: '📝', finance: '💰', events: '🎉',
  education: '📚', other: '📄',
};

const CATEGORIES = [
  { key: 'all',         label: 'All' },
  { key: 'medical',     label: 'Medical' },
  { key: 'grocery',     label: 'Grocery' },
  { key: 'finance',     label: 'Finance' },
  { key: 'education',   label: 'Education' },
  { key: 'maintenance', label: 'Maintenance' },
  { key: 'personal',    label: 'Personal' },
  { key: 'events',      label: 'Events' },
  { key: 'other',       label: 'Other' },
];

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  uploaded:   { color: 'bg-gray-100 text-gray-600',     label: 'Uploaded'   },
  processing: { color: 'bg-yellow-100 text-yellow-700', label: 'Processing' },
  ready:      { color: 'bg-green-100 text-green-700',   label: 'Ready'      },
  processed:  { color: 'bg-green-100 text-green-700',   label: 'Ready'      },
  failed:     { color: 'bg-red-100 text-red-700',       label: 'Failed'     },
};

export default function DocumentsPage() {
  const searchParams  = useSearchParams();
  const router        = useRouter();

  const urlCategory   = searchParams.get('category') || 'all';

  const [documents, setDocuments]       = useState<Document[]>([]);
  const [allTags, setAllTags]           = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [activeCategory, setActiveCategory] = useState(urlCategory);
  const [loading, setLoading]           = useState(true);
  const [uploading, setUploading]       = useState(false);
  const [uploadMsg, setUploadMsg]       = useState('');
  const [newlyReady, setNewlyReady]     = useState<string[]>([]);
  const [newTagInput, setNewTagInput]   = useState<Record<string, string>>({});
  const pollRef                         = useRef<NodeJS.Timeout | null>(null);
  const prevStatusRef                   = useRef<Record<string, string>>({});

  // Fetch documents with current filters
  const fetchDocuments = useCallback(async () => {
    try {
      const cat  = activeCategory === 'all' ? undefined : activeCategory;
      const res  = await apiClient.documents.list(cat, selectedTags);
      const docs = (Array.isArray(res.data) 
        ? res.data 
        : (res.data?.documents || [])) as Document[];

      const justReady = docs.filter(doc =>
        (doc.status === 'ready' || doc.status === 'processed') &&
        prevStatusRef.current[doc.id] === 'processing'
      );
      if (justReady.length > 0) {
        setNewlyReady(prev => [...prev, ...justReady.map(d => d.id)]);
        setTimeout(() => {
          setNewlyReady(prev => prev.filter(id => !justReady.map(d => d.id).includes(id)));
        }, 4000);
      }

      prevStatusRef.current = Object.fromEntries(docs.map(d => [d.id, d.status]));
      setDocuments(docs);
    } catch {}
  }, [activeCategory, selectedTags]);

  // Fetch all user tags
  const fetchTags = useCallback(async () => {
    try {
      const res = await apiClient.documents.listTags();
      setAllTags(res.data.tags);
    } catch {}
  }, []);

  // Initial load
  useEffect(() => {
    setActiveCategory(urlCategory);
  }, [urlCategory]);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchDocuments(), fetchTags()])
      .finally(() => setLoading(false));
  }, [fetchDocuments, fetchTags]);

  // Smart polling
  useEffect(() => {
    const hasProcessing = documents.some(
      d => d.status === 'processing' || d.status === 'uploaded'
    );
    if (hasProcessing) {
      pollRef.current = setInterval(fetchDocuments, 5000);
    } else {
      if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [documents, fetchDocuments]);

  // Category change
  const handleCategoryChange = (cat: string) => {
    setActiveCategory(cat);
    router.push(`/dashboard/documents${cat !== 'all' ? `?category=${cat}` : ''}`);
  };

  // Tag filter toggle
  const toggleTagFilter = (tagName: string) => {
    setSelectedTags(prev =>
      prev.includes(tagName)
        ? prev.filter(t => t !== tagName)
        : [...prev, tagName]
    );
  };

  // Add tag to document
  const handleAddTag = async (docId: string) => {
    const name = (newTagInput[docId] || '').trim().toLowerCase();
    if (!name) return;
    try {
      await apiClient.documents.addTag(docId, name);
      setNewTagInput(prev => ({ ...prev, [docId]: '' }));
      await Promise.all([fetchDocuments(), fetchTags()]);
    } catch {}
  };

  // Remove tag from document
  const handleRemoveTag = async (docId: string, tagId: string) => {
    try {
      await apiClient.documents.removeTag(docId, tagId);
      await fetchDocuments();
    } catch {}
  };

  // Upload
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true);
      setUploadMsg(`Uploading ${file.name}...`);
      try {
        const formData = new FormData();
        formData.append('file', file);
        await apiClient.documents.upload(formData);
        setUploadMsg(`✅ ${file.name} uploaded — processing started`);
        await fetchDocuments();
      } catch (err: any) {
        const msg = err.response?.data?.file?.[0] || 'Upload failed';
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
    if (!confirm('Permanently delete this document?')) return;
    try {
      await apiClient.documents.delete(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch { alert('Delete failed'); }
  };

  const processingCount = documents.filter(
    d => d.status === 'processing' || d.status === 'uploaded'
  ).length;

  return (
    <div className="p-8">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Documents</h1>
        {processingCount > 0 && (
          <div className="flex items-center gap-2 bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-2 rounded-xl text-sm">
            <span className="animate-spin inline-block">⚙️</span>
            Processing {processingCount} document{processingCount > 1 ? 's' : ''}...
          </div>
        )}
      </div>

      {/* Category filter tabs */}
      <div className="flex gap-2 flex-wrap mb-5">
        {CATEGORIES.map(cat => (
          <button
            key={cat.key}
            onClick={() => handleCategoryChange(cat.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition
              ${activeCategory === cat.key
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'}`}>
            {cat.key !== 'all' && CATEGORY_ICONS[cat.key]} {cat.label}
          </button>
        ))}
      </div>

      {/* Tag filter */}
      {allTags.length > 0 && (
        <div className="mb-5">
          <div className="text-xs text-gray-400 mb-2 font-medium">Filter by tag:</div>
          <div className="flex gap-2 flex-wrap">
            {allTags.map(tag => (
              <button
                key={tag.id}
                onClick={() => toggleTagFilter(tag.name)}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition
                  ${selectedTags.includes(tag.name)
                    ? 'bg-purple-600 text-white border-purple-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-purple-300'}`}>
                # {tag.name}
                {selectedTags.includes(tag.name) && (
                  <span className="ml-1">×</span>
                )}
              </button>
            ))}
            {selectedTags.length > 0 && (
              <button
                onClick={() => setSelectedTags([])}
                className="px-3 py-1 rounded-full text-xs text-gray-400 hover:text-gray-600">
                Clear filters
              </button>
            )}
          </div>
        </div>
      )}

      {/* Newly ready notification */}
      {newlyReady.length > 0 && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 mb-4 text-sm">
          ✅ {newlyReady.length} document{newlyReady.length > 1 ? 's' : ''} ready — ask Hita about {newlyReady.length > 1 ? 'them' : 'it'}!
        </div>
      )}

      {/* Upload zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition mb-6
          ${isDragActive ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300 bg-white'}`}>
        <input {...getInputProps()} />
        <div className="text-3xl mb-2">{isDragActive ? '📂' : '⬆️'}</div>
        <p className="font-medium text-gray-700 text-sm">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-xs text-gray-400 mt-1">PDF, DOCX, XLSX, JPG, PNG, TXT · Max 25MB</p>
        <button className="mt-3 bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-indigo-700 transition">
          Browse Files
        </button>
      </div>

      {/* Upload status */}
      {(uploading || uploadMsg) && (
        <div className={`rounded-xl px-4 py-3 text-sm mb-4
          ${uploadMsg.startsWith('❌') ? 'bg-red-50 text-red-600' : 'bg-indigo-50 text-indigo-700'}`}>
          {uploadMsg || 'Uploading...'}
        </div>
      )}

      {/* Document list */}
      {loading ? (
        <div className="text-center py-16">
          <div className="text-3xl mb-3 animate-spin">⚙️</div>
          <p className="text-gray-400 text-sm">Loading documents...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
          <div className="text-4xl mb-3">📭</div>
          <p className="text-gray-500 text-sm">
            {selectedTags.length > 0 || activeCategory !== 'all'
              ? 'No documents match your filters.'
              : 'No documents yet. Upload your first one above!'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => {
            const statusCfg = STATUS_CONFIG[doc.status] || STATUS_CONFIG.uploaded;
            const isNew = newlyReady.includes(doc.id);
            const isProcessing = doc.status === 'processing' || doc.status === 'uploaded';

            return (
              <div
                key={doc.id}
                className={`bg-white border rounded-2xl px-6 py-4 transition
                  ${isNew ? 'border-green-300 shadow-md' : 'border-gray-100 hover:shadow-sm'}`}>

                {/* Top row */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <span className="text-2xl flex-shrink-0">
                      {CATEGORY_ICONS[doc.category] || '📄'}
                    </span>
                    <div className="min-w-0">
                      <div className="font-medium text-gray-800 flex items-center gap-2 flex-wrap">
                        <span className="truncate">{doc.original_name}</span>
                        {isNew && (
                          <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full flex-shrink-0">
                            Just ready!
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {doc.category}
                        {doc.extracted_vendor  && ` · ${doc.extracted_vendor}`}
                        {doc.extracted_amount  && ` · ₹${doc.extracted_amount}`}
                        {doc.extracted_date    && ` · ${doc.extracted_date}`}
                      </div>
                      {doc.summary && (
                        <div className="text-xs text-gray-500 mt-1 truncate max-w-lg">
                          {doc.summary}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1 ${statusCfg.color}`}>
                      {isProcessing && <span className="animate-spin inline-block text-xs">⚙️</span>}
                      {statusCfg.label}
                    </span>
                    <button onClick={() => handleDelete(doc.id)}
                      className="text-gray-300 hover:text-red-400 transition" title="Delete">
                      🗑️
                    </button>
                  </div>
                </div>

                {/* Tags row */}
                <div className="mt-3 flex items-center gap-2 flex-wrap pl-10">
                  {/* Existing tags */}
                  {(doc.tags || []).map(tag => (
                    <span
                      key={tag.id}
                      className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-full text-xs">
                      # {tag.name}
                      <button
                        onClick={() => handleRemoveTag(doc.id, tag.id)}
                        className="hover:text-red-500 transition ml-0.5 leading-none">
                        ×
                      </button>
                    </span>
                  ))}

                  {/* Add tag input */}
                  <div className="flex items-center gap-1">
                    <input
                      type="text"
                      placeholder="+ add tag"
                      value={newTagInput[doc.id] || ''}
                      onChange={e => setNewTagInput(prev => ({ ...prev, [doc.id]: e.target.value }))}
                      onKeyDown={e => e.key === 'Enter' && handleAddTag(doc.id)}
                      className="text-xs border border-dashed border-gray-300 rounded-full px-3 py-0.5 w-24 focus:outline-none focus:border-purple-400 focus:w-32 transition-all placeholder-gray-400"
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {processingCount > 0 && (
        <p className="text-center text-xs text-gray-400 mt-6">
          🔄 Auto-updating every 5 seconds
        </p>
      )}
    </div>
  );
}