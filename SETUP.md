# Hita — Setup & Run Guide

## Prerequisites
- Python 3.12+
- Node.js 18+
- Docker + Docker Compose
- Tesseract OCR (for local installs without Docker)

---

## Step 1 — Clone & Configure Backend

```bash
cd hita/backend

# Copy and fill environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

---

## Step 2 — Start with Docker (Recommended)

```bash
cd hita/backend

# Start PostgreSQL + Redis + Django + Celery
docker-compose up --build

# In a new terminal — run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional — for Django admin)
docker-compose exec web python manage.py createsuperuser
```

✅ Backend running at: http://localhost:8000
✅ API docs at:        http://localhost:8000/api/
✅ Celery monitor at:  http://localhost:5555
✅ Django admin at:    http://localhost:8000/admin

---

## Step 3 — Start WITHOUT Docker (manual)

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install tesseract-ocr tesseract-ocr-eng postgresql redis-server

# Install Python packages
cd hita/backend
pip install -r requirements.txt

# Start PostgreSQL and Redis manually
# Then update .env with your local DB credentials

# Run migrations
python manage.py migrate

# Start Django
python manage.py runserver

# Start Celery worker (new terminal)
celery -A hita_project worker --loglevel=info
```

---

## Step 4 — Start Frontend

```bash
cd hita/frontend

# Install dependencies
npm install

# Copy env
cp .env.local.example .env.local

# Start Next.js
npm run dev
```

✅ Frontend running at: http://localhost:3000

---

## Step 5 — Validate Everything Works

### Test 1 — Register a user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@hita.app","full_name":"Test User","password":"test1234","confirm_password":"test1234","consent_given":true}'
```
Expected: 201 Created with tokens

### Test 2 — Upload a document
```bash
# Get your access token from Test 1 response
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/test.pdf"
```
Expected: 201 Created, status=processing

### Test 3 — Check processing status
```bash
curl http://localhost:8000/api/ai/status/DOCUMENT_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
Expected: status=ready after processing

### Test 4 — Ask a question
```bash
curl -X POST http://localhost:8000/api/ai/query/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"What documents do I have?"}'
```
Expected: answer with sources

---

## Project File Map (Quick Reference)

```
backend/
  hita_project/settings.py    — All configuration
  hita_project/urls.py        — Root URL routing
  hita_project/celery.py      — Celery setup
  apps/users/                 — Auth (register, login, JWT)
  apps/documents/             — Upload, parse, manage files
  apps/ai_engine/
    gemini.py                 — Gemini API calls
    embeddings.py             — pgvector store/search
    tasks.py                  — Celery async processing
    views.py                  — Query endpoint

frontend/
  src/lib/api.ts              — All API calls (single source of truth)
  src/lib/auth.ts             — Token management
  src/app/auth/               — Login + Register pages
  src/app/dashboard/          — Main app (home, documents, ask)
```

---

## Common Issues & Fixes

**pgvector extension error**
```sql
-- Connect to your DB and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

**Tesseract not found**
```bash
sudo apt install tesseract-ocr
# or on Mac:
brew install tesseract
```

**Celery not processing tasks**
- Confirm Redis is running: redis-cli ping
- Check REDIS_URL in .env matches your Redis address

**CORS error from frontend**
- Confirm FRONTEND_URL=http://localhost:3000 in backend .env
- Restart Django after .env changes
