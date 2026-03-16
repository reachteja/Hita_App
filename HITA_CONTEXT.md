# HITA_CONTEXT.md
# Master Technical Reference — Read this file to understand everything about Hita
# Place this at: F:\Freelance\Hita_App\HITA_CONTEXT.md

---

## 1. PROJECT IDENTITY

**App Name:** Hita (హిత)
**Meaning:** Wellwisher in Telugu/Sanskrit
**Tagline:** Your personal document buddy
**Target Users:** Indian families managing household documents
**Core Problem:** People lose bills, medical records, receipts across WhatsApp, email, paper

---

## 2. WHAT THE APP DOES

1. User uploads any document (PDF, Word, Excel, image, text)
2. AI reads and understands the document
3. AI categorises it (grocery/medical/maintenance etc.)
4. AI extracts key info (date, amount, vendor)
5. User can ask natural language questions
6. AI retrieves answers from their documents

Example query: "How much did I spend on medicines in January?"
Example answer: "You spent ₹4,200 on medicines in January across 3 medical bills."

---

## 3. COMPLETE BACKEND REFERENCE

### settings.py — Key Configuration
```python
AUTH_USER_MODEL = 'users.HitaUser'      # Custom user model
TIME_ZONE = 'Asia/Kolkata'              # Indian timezone
CELERY_BROKER_URL = Redis URL           # Task queue
CELERY_RESULT_BACKEND = 'django-db'    # Store results in DB
MAX_UPLOAD_SIZE = 25MB
ALLOWED_FILE_TYPES = [pdf, docx, xlsx, jpg, png, txt]
DOCUMENT_CATEGORIES = [grocery, medical, maintenance, personal, events, finance, other]
```

### apps/users/ — Authentication
```
HitaUser model:
  - Uses email as USERNAME_FIELD (not username)
  - Has consent_given + consent_given_at (DPDP compliance)
  - UUID primary key

RegisterSerializer:
  - Validates password match
  - Requires consent_given=True
  - Records consent timestamp

Views return format:
  { message, user: {...}, tokens: {access, refresh} }
```

### apps/documents/ — File Management
```
Document model fields:
  id              UUID
  user            FK to HitaUser
  original_name   original filename
  file_path       absolute path on disk
  file_type       MIME type
  file_size       bytes
  category        one of DOCUMENT_CATEGORIES
  extracted_text  first 5000 chars of raw text
  extracted_date  date found in document
  extracted_amount rupee amount found
  extracted_vendor shop/hospital/vendor name
  summary         one-line AI summary
  status          uploaded→processing→ready/failed
  celery_task_id  for tracking async task
  error_message   if failed
  is_deleted      soft delete flag

utils.py functions:
  extract_text(file_path)    → routes to correct parser
  scrub_pii(text)            → removes Aadhaar/PAN/phone/bank details
  chunk_text(text)           → splits into 500-token chunks with 50-token overlap
```

### apps/ai_engine/ — Intelligence Layer
```
gemini.py:
  categorise_document(text)           → returns {category, date, amount, vendor, summary}
  generate_embeddings(text)           → returns vector[768]
  answer_query(question, chunks)      → returns grounded answer string

embeddings.py:
  store_embeddings(doc_id, chunks)    → saves to pgvector
  search_similar_chunks(q, user_id)   → returns top-5 relevant chunks
  delete_document_embeddings(doc_id)  → cleanup on delete

tasks.py (Celery):
  process_document(document_id):
    1. Load Document from DB
    2. extract_text → raw text
    3. scrub_pii → clean text
    4. chunk_text → chunks[]
    5. store_embeddings → pgvector
    6. categorise_document → metadata
    7. Update Document record → status=ready
```

---

## 4. COMPLETE FRONTEND REFERENCE

### src/lib/api.ts — Single Source of Truth for API calls
```typescript
authAPI.register(data)              POST /api/auth/register/
authAPI.login(data)                 POST /api/auth/login/
authAPI.logout(refresh)             POST /api/auth/logout/
authAPI.profile()                   GET  /api/auth/profile/

documentsAPI.list(category?)        GET  /api/documents/
documentsAPI.upload(formData)       POST /api/documents/upload/
documentsAPI.get(id)                GET  /api/documents/{id}/
documentsAPI.delete(id)             DELETE /api/documents/{id}/
documentsAPI.updateCategory(id, c)  PATCH /api/documents/{id}/category/

aiAPI.query(question)               POST /api/ai/query/
aiAPI.status(docId)                 GET  /api/ai/status/{id}/
```

### src/lib/auth.ts — Token Management
```typescript
saveTokens(tokens)      stores in cookies
clearTokens()           removes cookies
getAccessToken()        reads cookie
isLoggedIn()            checks if token exists
saveUser(user)          stores in localStorage
getUser()               reads from localStorage
```

### Pages
```
/                           Landing page with CTA
/auth/login                 Email+password login
/auth/register              Registration with privacy consent checkbox
/dashboard                  Home — category tiles + recent docs
/dashboard/documents        Upload zone (react-dropzone) + document list
/dashboard/ask              Chat interface — Ask Hita
```

### Key Component Behaviours
```
DocumentsPage:
  - Polls every 5 seconds if any doc is in 'processing' status
  - Shows status badge (uploaded/processing/ready/failed)
  - Drag & drop + click to browse
  - Delete with confirmation dialog

AskPage:
  - Maintains full conversation history in state
  - Shows source documents under each Hita answer
  - Suggested questions shown on first load
  - Enter key submits question

DashboardLayout:
  - Checks isLoggedIn() on mount — redirects to login if false
  - Logout blacklists refresh token then clears cookies
```

---

## 5. DATABASE SCHEMA

### hita_users
```sql
id UUID PK, email VARCHAR UNIQUE, full_name VARCHAR,
password VARCHAR, is_active BOOL, is_staff BOOL,
consent_given BOOL, consent_given_at TIMESTAMP,
created_at TIMESTAMP, updated_at TIMESTAMP
```

### hita_documents
```sql
id UUID PK, user_id UUID FK,
original_name VARCHAR, file_path VARCHAR,
file_type VARCHAR, file_size BIGINT,
category VARCHAR, extracted_text TEXT,
extracted_date DATE, extracted_amount DECIMAL,
extracted_vendor VARCHAR, summary TEXT,
status VARCHAR, error_message TEXT,
celery_task_id VARCHAR, is_deleted BOOL,
created_at TIMESTAMP, updated_at TIMESTAMP
```

### hita_embeddings (raw SQL — not Django model)
```sql
id BIGSERIAL PK, document_id TEXT,
chunk_index INT, chunk_text TEXT,
embedding vector(768), created_at TIMESTAMP
INDEX: ivfflat on embedding (cosine distance)
```

### django_celery_results_taskresult
```sql
(managed by django-celery-results library)
```

---

## 6. SECURITY RULES — NEVER VIOLATE THESE

1. scrub_pii() MUST run before any text reaches Gemini API
2. pgvector search ALWAYS filters by user_id — no cross-user data
3. File paths must be inside uploads/{user_id}/ — no path traversal
4. Consent must be True before creating user account
5. Refresh token must be blacklisted on logout
6. Admin views must never return document file contents

---

## 7. ERROR HANDLING CONVENTIONS

### Backend
```python
# Always return consistent error format
return Response({'error': 'message'}, status=400)
return Response({'message': 'success', 'data': {...}}, status=200)
```

### Frontend
```typescript
// Always catch API errors
try {
  const res = await documentsAPI.upload(formData)
} catch (err: any) {
  const msg = err.response?.data?.error || 'Something went wrong'
  setError(msg)
}
```

---

## 8. WHAT TO BUILD NEXT (Priority Order)

### High Priority
1. **Password Reset** — forgot password email flow
2. **Email Notifications** — notify user when document processing is complete
3. **Document Preview** — show extracted text and metadata in a modal
4. **Category Filter** — filter documents by category on documents page
5. **Date Range Filter** — filter by date on documents page

### Medium Priority
6. **Spending Analytics** — chart of expenses by category over time
7. **Export Feature** — download all documents as ZIP
8. **Bulk Upload** — upload multiple files at once (already supported in dropzone)
9. **Tamil/Hindi OCR** — add tam+hin Tesseract language packs
10. **Dark Mode** — toggle between light/dark theme

### Future
11. WhatsApp ingestion — forward documents to a WhatsApp number
12. Email ingestion — forward bills to bills@hita.app
13. Mobile app — React Native
14. Family vault — share specific categories with family members
15. Insurance claim helper — compile all medical records for a claim

---

## 9. RUNNING THE APP (Quick Reference)

```cmd
# Terminal 1 — Backend
cd F:\Freelance\Hita_App\backend
venv\Scripts\activate
python manage.py runserver

# Terminal 2 — Celery (MUST use --pool=solo on Windows)
cd F:\Freelance\Hita_App\backend
venv\Scripts\activate
celery -A hita_project worker --loglevel=info --pool=solo

# Terminal 3 — Frontend
cd F:\Freelance\Hita_App\frontend
npm run dev
```

URLs:
- Frontend:  http://localhost:3000
- Backend:   http://localhost:8000
- API docs:  http://localhost:8000/api/
- Admin:     http://localhost:8000/admin

---

## 10. COMMON ERRORS & FIXES

### "pgvector extension not found"
```sql
-- Run in psql or Supabase SQL editor:
CREATE EXTENSION IF NOT EXISTS vector;
```

### "Tesseract not found"
```cmd
-- Install from github.com/UB-Mannheim/tesseract/wiki
-- Add to PATH: C:\Program Files\Tesseract-OCR
```

### "Celery task not processing"
```cmd
-- Confirm Redis is running:
redis-cli ping   (should return PONG)
-- Always use --pool=solo on Windows
celery -A hita_project worker --loglevel=info --pool=solo
```

### "CORS error from frontend"
```
-- Check backend .env:
FRONTEND_URL=http://localhost:3000
-- Restart Django after changing .env
```

### "JWT token expired"
```
-- Axios interceptor handles this automatically
-- If still failing, check SIMPLE_JWT settings in settings.py
```

### "Document stuck in processing"
```python
# Check Celery logs in Terminal 2
# Manually retry via Django shell:
python manage.py shell
from apps.ai_engine.tasks import process_document
process_document.delay('document-uuid-here')
```
