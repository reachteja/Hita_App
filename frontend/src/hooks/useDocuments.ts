/**
 * Documents hook for fetching and managing documents
 */
'use client';
import { useState, useEffect } from 'react';
import { Document } from '@/types';
import { apiClient } from '@/lib/api';

export function useDocuments(category?: string) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.documents.list(category);
      setDocuments(response.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [category]);

  const deleteDocument = async (id: string) => {
    try {
      await apiClient.documents.delete(id);
      setDocuments(documents.filter(d => d.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const updateCategory = async (id: string, newCategory: string) => {
    try {
      const response = await apiClient.documents.updateCategory(id, newCategory);
      setDocuments(documents.map(d => (d.id === id ? response.data : d)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update category');
    }
  };

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    deleteDocument,
    updateCategory,
  };
}
