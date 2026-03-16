# 🪷 Hita - Your Personal Document Assistant

**Hita (హిత)** means "wellwisher" in Telugu/Sanskrit. Hita is an AI-powered personal document vault app for Indian families to manage their household documents, extract information, and ask natural language questions.

## 🎯 Features

- **📤 Document Upload**: Upload PDFs, Word files, Excel sheets, images, and text files
- **🤖 AI Organization**: Automatic categorization (grocery, medical, maintenance, personal, events, finance)
- **🔍 Smart Extraction**: Extract dates, amounts, vendors, and summaries using Gemini AI
- **💬 Ask Questions**: Query your documents in plain language using RAG (Retrieval-Augmented Generation)
- **🔒 Privacy First**: All PII (Aadhaar, PAN, phone) scrubbed before any AI processing
- **🚀 Async Processing**: Fast uploads with background processing using Celery

## 🏗️ Project Structure

```
hita/
├── backend/                    # Django 5.x API
│   ├── hita_project/
│   ├── apps/
│   │   ├── users/             # Authentication (JWT)
│   │   ├── documents/         # Document upload & management
│   │   └── ai_engine/         # Gemini integration & RAG
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
└── frontend/                   # Next.js 14 UI
    ├── src/
    │   ├── app/               # App Router pages
    │   ├── components/        # React components
    │   ├── lib/               # API client & utilities
    │   ├── hooks/             # Custom React hooks
    │   └── types/             # TypeScript interfaces
    ├── package.json
    ├── tsconfig.json
    └── .env.local.example
```

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Axios |
| **Backend** | Django 5.x, Django REST Framework |
| **Database** | PostgreSQL 16 with pgvector extension |
| **Queue** | Celery + Redis |
| **AI** | Google Gemini API (gemini-1.5-flash) |
| **OCR** | Tesseract (for scanned documents) |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Storage** | Local filesystem (S3-ready) |

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker & Docker Compose
- Gemini API key (free from [aistudio.google.com](https://aistudio.google.com))

### Step 1: Configure Environment

```bash
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Step 2: Start Backend

```bash
cd backend
docker-compose up --build
```

Services will be running:
- ✅ **Django API**: http://localhost:8000
- ✅ **Celery Worker**: Background processing
- ✅ **PostgreSQL**: Database
- ✅ **Redis**: Cache & message broker
- ✅ **Flower**: Task monitor at http://localhost:5555

### Step 3: Run Migrations

```bash
# In a new terminal
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser  # optional
```

### Step 4: Start Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend will be running:
- ✅ **Next.js**: http://localhost:3000

### Step 5: Test

1. Go to http://localhost:3000
2. Register a new account
3. Upload a document
4. Ask questions about it!

---

## 🚀 Quick Start (Without Docker - Windows)

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- Redis
- Tesseract OCR

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
copy .env.example .env
# Edit .env with your database and Gemini API key

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 2: Start Backend Services

**Terminal 1** - Django:
```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

**Terminal 2** - Celery Worker (Note: Windows requires --pool=solo):
```bash
cd backend
venv\Scripts\activate
celery -A hita_project worker --loglevel=info --pool=solo
```

### Step 3: Frontend Setup

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

---

## 📚 API Endpoints

### Authentication
```
POST   /api/auth/register/              # Register new user
POST   /api/auth/login/                 # Login → returns JWT
POST   /api/auth/logout/                # Logout
GET    /api/auth/profile/               # Get user profile
PATCH  /api/auth/profile/               # Update profile
```

### Documents
```
GET    /api/documents/                  # List user's documents (filter: ?category=)
POST   /api/documents/upload/           # Upload file
GET    /api/documents/{id}/             # Get single document
DELETE /api/documents/{id}/             # Delete document (hard)
PATCH  /api/documents/{id}/category/    # Update category
```

### AI / RAG Query
```
POST   /api/ai/query/                   # Ask a question → RAG answer
GET    /api/ai/status/                  # Check document processing status
```

---

## 🔐 Security Features

✅ **PII Scrubbing**: Aadhaar, PAN, phone, bank accounts removed before any AI call
✅ **User Isolation**: pgvector search filters by user_id
✅ **Hard Delete**: Files + embeddings + DB records removed
✅ **JWT Tokens**: Secure access token (1hr) + refresh token (7 days)
✅ **CORS**: Restricted to frontend URL
✅ **Consent Tracking**: DPDP Act 2023 compliance

---

## 📖 Document Categories

- 🛒 **Grocery** - Grocery bills, food receipts
- ⚕️ **Medical** - Medical bills, prescriptions, health records
- 🔧 **Maintenance** - Repair bills, maintenance receipts
- 👤 **Personal** - Personal notes, identity documents
- 🎉 **Events** - Event tickets, invoices
- 💰 **Finance** - Loan documents, investment records
- 📄 **Other** - Everything else

---

## 🧪 Testing

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@hita.app",
    "full_name":"Test User",
    "password":"testpass123",
    "confirm_password":"testpass123",
    "consent_given":true
  }'
```

### Upload a Document
```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@invoice.pdf"
```

### Ask a Question
```bash
curl -X POST http://localhost:8000/api/ai/query/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"How much did I spend on medicines?"}'
```

---

## 🛠️ Development

### Backend Development
- Models in `apps/*/models.py`
- Serializers in `apps/*/serializers.py`
- Views in `apps/*/views.py`
- Celery tasks in `apps/ai_engine/tasks.py`
- Gemini integration in `apps/ai_engine/gemini.py`

### Frontend Development
- Pages in `src/app/`
- Components in `src/components/`
- API client in `src/lib/api.ts`
- Hooks in `src/hooks/`
- Types in `src/types/`

### Running Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# View SQL
python manage.py sqlmigrate apps.documents 0001
```

---

## 🐛 Troubleshooting

### Celery not processing tasks
- Ensure Redis is running: `redis-cli ping`
- Check Celery worker logs for errors
- On Windows, use `--pool=solo` flag

### Tesseract OCR errors
- **Windows**: Install from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-eng`
- Update path in `pytesseract` if needed

### PostgreSQL connection errors
- Ensure PostgreSQL is running on port 5432
- Check credentials in `.env`
- Verify database exists: `psql -U hita -d hita`

### Gemini API errors
- Verify `GEMINI_API_KEY` in `.env`
- Check API quota at [console.cloud.google.com](https://console.cloud.google.com)
- Ensure free tier is not rate-limited

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in terminal
3. Check Django admin at http://localhost:8000/admin

---

## 📝 License

Built with ❤️ for Indian families managing their documents.

**Document privacy is sacred. Your documents stay with you.**
#   A p p - t e s t i n g  
 