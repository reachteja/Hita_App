// Frontend TypeScript types and interfaces

export interface HitaUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Tag {
  id:   string;
  name: string;
}

export interface Document {
  id: string;
  original_name: string;
  file_type: string;
  file_size: number;
  category: string;
  summary: string;
  extracted_date: string | null;
  extracted_amount: number | null;
  extracted_vendor: string;
  status: 'uploaded' | 'processing' | 'ready' | 'failed';
  error_message: string;
  created_at: string;
  tags: Tag[]; 
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    id: string;
    name: string;
    category: string;
  }>;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  message: string;
  user: HitaUser;
  tokens: AuthTokens;
}
