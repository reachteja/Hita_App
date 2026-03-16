# Hita — AI Copilot Instructions
# This file is read automatically by GitHub Copilot, Cursor, and Continue.
# It gives the AI full context about this project so it can assist correctly.

## What is Hita?
Hita (హిత) is a personal document vault app for Indian users.
The name means "wellwisher" in Telugu/Sanskrit — an AI buddy that remembers your documents for you.
Users upload bills, medical records, grocery receipts, maintenance documents, and personal notes.
The AI reads, categorises, and stores them. Users can ask natural language questions to retrieve information.

## Tech Stack
- Backend:   Django 5.x + Django REST Framework
- Frontend:  Next.js 14 (App Router) + TypeScript + Tailwind CSS
- Database:  PostgreSQL 16 with pgvector extension
- Queue:     Celery + Redis (async document processing)
- AI:        Google Gemini API (gemini-1.5-flash + text-embedding-004)
- OCR:       Tesseract (local, free, for scanned documents)
- Auth:      JWT via djangorestframework-simplejwt
- Storage:   Local filesystem (uploads/ folder) — S3-ready later

## Project Structure
```
F:\Freelance\Hita_App\
├── backend/                         # Django project root
│   ├── hita_project/
│   │   ├── settings.py              # All config — DB, JWT, Celery, Gemini
│   │   ├── urls.py                  # Root URL router
│   │   ├── celery.py                # Celery app config
│   │   └── __init__.py              # Loads celery on startup
│   ├── apps/
│   │   ├── users/                   # Auth module
│   │   │   ├── models.py            # HitaUser (custom AbstractBaseUser)
│   │   │   ├── serializers.py       # Register, Login, Profile serializers
│   │   │   ├── views.py             # Register, Login, Logout, Profile views
│   │   │   └── urls.py              # /api/auth/ routes
│   │   ├── documents/               # Document management module
│   │   │   ├── models.py            # Document model (status, category, extracted fields)
│   │   │   ├── serializers.py       # Upload, List, Category update serializers
│   │   │   ├── views.py             # Upload, List, Detail, Delete, Category views
│   │   │   ├── urls.py              # /api/documents/ routes
│   │   │   └── utils.py             # File parsers + PII scrubber + text chunker
│   │   └── ai_engine/               # AI processing module
│   │       ├── gemini.py            # Gemini API — categorise, embed, answer
│   │       ├── embeddings.py        # pgvector store/search/delete
│   │       ├── tasks.py             # Celery async task — full processing pipeline
│   │       ├── views.py             # Query (RAG) + Status endpoints
│   │       └── urls.py              # /api/ai/ routes
│   ├── uploads/                     # User uploaded files (gitignored)
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
└── frontend/                        # Next.js project root
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx           # Root layout
    │   │   ├── page.tsx             # Landing page
    │   │   ├── globals.css          # Tailwind base
    │   │   ├── auth/
    │   │   │   ├── login/page.tsx   # Login page
    │   │   │   └── register/page.tsx# Register page with consent
    │   │   └── dashboard/
    │   │       ├── layout.tsx       # Sidebar layout (auth guard)
    │   │       ├── page.tsx         # Dashboard home with category tiles
    │   │       ├── documents/page.tsx # Upload + document list
    │   │       └── ask/page.tsx     # Chat interface — Ask Hita
    │   ├── lib/
    │   │   ├── api.ts               # Axios client — ALL API calls defined here
    │   │   └── auth.ts              # JWT token management (cookies + localStorage)
    │   └── types/index.ts           # TypeScript interfaces for all data models
    ├── package.json
    ├── tailwind.config.js
    └── next.config.js
```

## API Endpoints (Complete)
```
POST   /api/auth/register/              Register new user
POST   /api/auth/login/                 Login → returns JWT tokens
POST   /api/auth/logout/                Blacklist refresh token
POST   /api/auth/refresh/               Refresh access token
GET    /api/auth/profile/               Get/update user profile

GET    /api/documents/                  List user's documents (filter by ?category=)
POST   /api/documents/upload/           Upload file (multipart/form-data)
GET    /api/documents/{id}/             Get single document
DELETE /api/documents/{id}/             Hard delete (file + embeddings + DB record)
PATCH  /api/documents/{id}/category/    Update category manually

POST   /api/ai/query/                   Ask a question → RAG answer
GET    /api/ai/status/{id}/             Check document processing status
```

## Data Flow — Document Processing Pipeline
```
1. User uploads file via POST /api/documents/upload/
2. Django saves file to uploads/{user_id}/{uuid}.ext
3. Document record created (status=uploaded)
4. Celery task triggered: process_document(document_id)
5. Document status → processing
6. File type detected → routed to correct parser:
   - .pdf  (digital)  → PyMuPDF text extraction
   - .pdf  (scanned)  → Tesseract OCR
   - .docx            → python-docx
   - .xlsx            → openpyxl/pandas
   - .jpg/.png        → Tesseract OCR via PIL
   - .txt             → direct read
7. PII scrubbed: Aadhaar, phone, PAN, bank account → placeholders
8. Text chunked into 500-token overlapping chunks
9. Each chunk embedded via Gemini text-embedding-004 (768 dimensions)
10. Embeddings stored in pgvector (hita_embeddings table)
11. Full document sent to Gemini for categorisation + field extraction
12. Document record updated: status=ready, category, amount, vendor, date, summary
```

## Data Flow — Query (RAG Pipeline)
```
1. User sends question via POST /api/ai/query/
2. Question converted to embedding via Gemini
3. pgvector cosine similarity search → top 5 matching chunks
4. Chunks filtered by user ownership (security)
5. Chunks passed to Gemini with system prompt
6. Gemini generates grounded answer (no hallucination)
7. Response includes answer + source document names
```

## Key Models

### HitaUser (apps/users/models.py)
```python
id, email, full_name, is_active, is_staff
consent_given, consent_given_at           # DPDP Act 2023 compliance
USERNAME_FIELD = 'email'                  # Login with email not username
```

### Document (apps/documents/models.py)
```python
id (UUID), user (FK), original_name, file_path, file_type, file_size
category                    # grocery/medical/maintenance/personal/events/finance/other
extracted_text, extracted_date, extracted_amount, extracted_vendor, summary
status                      # uploaded/processing/ready/failed
celery_task_id, error_message
is_deleted                  # soft delete flag
```

### hita_embeddings (raw SQL table — apps/ai_engine/embeddings.py)
```sql
id, document_id, chunk_index, chunk_text, embedding vector(768), created_at
```
Note: This table is NOT a Django model — created via raw SQL in _ensure_table()

## Environment Variables (.env in backend/)
```
SECRET_KEY                  Django secret key
DEBUG                       True for dev
ALLOWED_HOSTS               localhost,127.0.0.1
DB_NAME/USER/PASSWORD/HOST/PORT   PostgreSQL connection
REDIS_URL                   redis://localhost:6379/0
GEMINI_API_KEY              Get free from aistudio.google.com
UPLOAD_DIR                  uploads
MAX_UPLOAD_SIZE_MB          25
ACCESS_TOKEN_LIFETIME_MINUTES  60
REFRESH_TOKEN_LIFETIME_DAYS    7
FRONTEND_URL                http://localhost:3000
```

## Frontend Environment Variables (.env.local in frontend/)
```
NEXT_PUBLIC_API_URL         http://localhost:8000/api
```

## Authentication Flow
- JWT — access token (1hr) + refresh token (7 days)
- Tokens stored in cookies (secure, sameSite strict)
- Axios interceptor auto-attaches Bearer token to every request
- Axios interceptor auto-refreshes on 401 response
- On refresh failure → redirect to /auth/login

## Security Decisions (Important — do not change without understanding)
- PII is scrubbed BEFORE any Gemini API call (scrub_pii in utils.py)
- Embeddings search filters by user_id — users cannot see each other's data
- File deletion is HARD delete — removes S3/local file + pgvector embeddings + DB record
- Consent is recorded with timestamp (DPDP Act 2023 compliance)
- Admin has zero access to document contents — metadata only

## Document Categories
grocery, medical, maintenance, personal, events, finance, other

## Celery Configuration
- Broker: Redis
- Result backend: django-db (django_celery_results)
- Task: process_document (apps/ai_engine/tasks.py)
- Max retries: 3, retry delay: 60 seconds
- Windows: always use --pool=solo flag

## Running Locally (Windows without Docker)
```
Terminal 1: python manage.py runserver
Terminal 2: celery -A hita_project worker --loglevel=info --pool=solo
Terminal 3 (frontend): npm run dev
```

## Known Windows-Specific Issues
- Celery requires --pool=solo on Windows
- Tesseract must be installed separately and added to PATH
- Redis not native on Windows — use Memurai (memurai.com)
- pgvector requires PostgreSQL 14+ (use Supabase free tier if local install is complex)

## What's NOT Built Yet (Next Steps)
- Password reset flow
- Email notifications when document processing is complete
- WhatsApp/email document ingestion
- Mobile app (React Native)
- Admin dashboard
- Usage analytics
- Multi-language OCR (Tamil, Hindi)
- Export documents as ZIP
- Family/shared vault feature

## Code Style Conventions
- Django views use APIView (not ViewSets) — explicit is better
- All views return consistent JSON: {message, data} or {error}
- UUIDs used for all primary keys
- Soft delete on documents (is_deleted flag) — hard delete only on explicit user request
- Frontend API calls centralised in src/lib/api.ts — never call axios directly in components
- TypeScript strict mode — all types defined in src/types/index.ts
