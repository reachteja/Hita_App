'use client';
import { useState, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import ReactMarkdown from 'react-markdown';

interface Message {
  role:    'user' | 'hita';
  content: string;
  sources?: { id: string; name: string; category: string }[];
}

const SUGGESTIONS = [
  'How much did I spend on medicines last month?',
  'Show me all grocery bills from January',
  'What was my last maintenance expense?',
  'Find my hospital bills from 2025',
];

export default function AskPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role:    'hita',
      content: "Hello! I'm Hita, your personal document assistant. Ask me anything about your uploaded documents — bills, medical records, receipts, or notes.",
    },
  ]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading]   = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleAsk = async (q?: string) => {
    const text = (q || question).trim();
    if (!text || loading) return;

    const userMessage: Message = { role: 'user', content: text };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setQuestion('');
    setLoading(true);

    try {
      const res = await apiClient.ai.query(text, updatedMessages);
      setMessages(prev => [...prev, {
        role:    'hita',
        content: res.data.answer,
        intent:    res.data.intent,
        documents: res.data.documents || [],
        sources:   res.data.sources   || [],
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role:    'hita',
        content: 'Sorry, I encountered an error. Please try again.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-8 py-4">
        <h1 className="font-bold text-gray-800">💬 Ask Hita</h1>
        <p className="text-xs text-gray-400 mt-0.5">Ask anything about your documents in plain language</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl rounded-2xl px-5 py-3 text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-sm'
                : 'bg-white border border-gray-100 text-gray-800 rounded-bl-sm shadow-sm'}`}>
              {msg.role === 'hita' && (
                <div className="flex items-center gap-2 mb-2">
                  <span>🪷</span>
                  <span className="font-semibold text-indigo-700 text-xs">Hita</span>
                </div>
              )}
              {/* Answer text — renders markdown bullets and line breaks */}
              <div className="prose prose-sm max-w-none
                prose-p:my-1 prose-ul:my-1 prose-li:my-0.5
                prose-ul:pl-4 ${msg.role === 'user' ? 'prose-invert' : ''}`}">
                <ReactMarkdown>
                  {msg.content
                    .replace(/^•\s*/gm, '- ')
                    .replace(/:\s*•/g, ':\n- ')
                    .replace(/\s•\s/g, '\n- ')
                  }</ReactMarkdown>
              </div>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Sources:</p>
                  {msg.sources.map(s => (
                    <span key={s.id} className="inline-block text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full mr-1 mt-1">
                      📄 {s.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 rounded-2xl px-5 py-3 shadow-sm">
              <div className="flex items-center gap-2">
                <span>🪷</span>
                <span className="text-xs text-gray-400">Hita is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="px-8 py-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-500 mb-3 font-semibold">Try asking:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => handleAsk(s)}
                className="text-left text-xs bg-white border border-gray-200 rounded px-3 py-2 hover:bg-indigo-50 hover:border-indigo-300 transition"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-8 py-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
            placeholder="Ask anything about your documents..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            onClick={() => handleAsk()}
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition font-semibold"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
