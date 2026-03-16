# HITA — Complete Coding Plan

## Stack
- Backend: Django 5.x + Django REST Framework
- Frontend: Next.js 14 (App Router)
- Database: PostgreSQL + pgvector
- Queue: Celery + Redis
- AI: Google Gemini API (free tier)
- OCR: Tesseract (local, free)
- File Storage: Local (MinIO-ready for later)
- Auth: JWT (djangorestframework-simplejwt)

## Project Structure
```
hita/
├── backend/                        # Django project
│   ├── hita_project/               # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/                  # Auth, registration, profile
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── documents/              # Upload, storage, management
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── utils.py            # File parsing utilities
│   │   └── ai_engine/              # AI processing, RAG, query
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── tasks.py            # Celery async tasks
│   │       ├── gemini.py           # Gemini API integration
│   │       ├── embeddings.py       # Vector embeddings
│   │       └── rag.py              # RAG pipeline
│   ├── uploads/                    # Uploaded files (gitignored)
│   ├── requirements.txt
│   ├── .env.example
│   ├── manage.py
│   └── docker-compose.yml
│
└── frontend/                       # Next.js project
    ├── src/
    │   ├── app/                    # App Router pages
    │   │   ├── layout.tsx
    │   │   ├── page.tsx            # Landing page
    │   │   ├── auth/
    │   │   │   ├── login/page.tsx
    │   │   │   └── register/page.tsx
    │   │   └── dashboard/
    │   │       ├── layout.tsx
    │   │       ├── page.tsx        # Dashboard home
    │   │       ├── documents/page.tsx
    │   │       └── ask/page.tsx    # Query interface
    │   ├── components/
    │   │   ├── layout/
    │   │   │   ├── Navbar.tsx
    │   │   │   └── Sidebar.tsx
    │   │   ├── documents/
    │   │   │   ├── UploadZone.tsx
    │   │   │   ├── DocumentCard.tsx
    │   │   │   └── DocumentList.tsx
    │   │   └── chat/
    │   │       ├── ChatWindow.tsx
    │   │       └── MessageBubble.tsx
    │   ├── lib/
    │   │   ├── api.ts              # Axios API client
    │   │   └── auth.ts             # Auth helpers
    │   ├── hooks/
    │   │   ├── useAuth.ts
    │   │   └── useDocuments.ts
    │   └── types/
    │       └── index.ts
    ├── .env.local.example
    └── package.json
```

## Module Build Order (Validated Sequence)
1. Backend foundation (settings, DB, auth)
2. Users app (register, login, JWT)
3. Documents app (upload, parse, store)
4. AI Engine (Gemini, embeddings, RAG)
5. Celery tasks (async processing)
6. Frontend foundation (Next.js, Axios)
7. Auth pages (login, register)
8. Dashboard (upload, document list)
9. Query interface (ask Hita)
10. End-to-end integration test

## API Endpoints
### Auth
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/
- POST /api/auth/logout/

### Documents
- GET    /api/documents/
- POST   /api/documents/upload/
- GET    /api/documents/{id}/
- DELETE /api/documents/{id}/
- PATCH  /api/documents/{id}/category/

### AI
- POST /api/ai/query/          — ask a question
- GET  /api/ai/status/{doc_id}/ — processing status

## Data Flow (Validated)
Upload → Django view receives file
       → Saves to /uploads/
       → Creates Document record (status=processing)
       → Triggers Celery task (async)
       → Returns {doc_id, status} to frontend

Celery → Detects file type
       → Extracts text (PyMuPDF/Tesseract/python-docx/pandas)
       → Scrubs PII
       → Chunks text
       → Generates embeddings via Gemini
       → Stores in pgvector
       → Categorises via Gemini
       → Updates Document record (status=ready)
       → Sends notification

Query  → Frontend sends question
       → Django converts to embedding
       → pgvector finds top-k chunks
       → Gemini generates grounded answer
       → Returns answer + source document
