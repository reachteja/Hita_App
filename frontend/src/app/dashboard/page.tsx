'use client';
import { useDocuments } from '@/hooks/useDocuments';

export default function DashboardPage() {
  const { documents } = useDocuments();

  const categories = ['grocery', 'medical', 'maintenance', 'personal', 'events', 'finance'];
  const categoryEmojis: Record<string, string> = {
    grocery: '🛒',
    medical: '⚕️',
    maintenance: '🔧',
    personal: '👤',
    events: '🎉',
    finance: '💰',
  };

  const getCountByCategory = (category: string) => {
    return documents.filter(d => d.category === category).length;
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Manage your documents by category</p>
      </div>

      {/* Category tiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map(category => (
          <a
            key={category}
            href={`/dashboard/documents?category=${category}`}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 capitalize">{category}</h3>
                <p className="text-3xl font-bold text-indigo-600 mt-2">{getCountByCategory(category)}</p>
                <p className="text-sm text-gray-500 mt-1">documents</p>
              </div>
              <div className="text-4xl">{categoryEmojis[category]}</div>
            </div>
          </a>
        ))}
      </div>

      {/* Quick actions */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/dashboard/documents"
            className="bg-indigo-600 text-white rounded-lg p-6 hover:bg-indigo-700 transition"
          >
            <span className="text-2xl mr-3">📤</span>
            <span className="font-semibold">Upload document</span>
          </a>
          <a
            href="/dashboard/ask"
            className="bg-green-600 text-white rounded-lg p-6 hover:bg-green-700 transition"
          >
            <span className="text-2xl mr-3">💬</span>
            <span className="font-semibold">Ask Hita</span>
          </a>
        </div>
      </div>
    </div>
  );
}
