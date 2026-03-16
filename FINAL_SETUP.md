# 🚀 Hita - Final Setup & Launch Guide

## ✅ What We've Done So Far

- ✅ Created complete backend (Django, DRF, Celery)
- ✅ Created complete frontend (Next.js, React)
- ✅ Installed all Python dependencies
- ✅ Configured environment (.env with Gemini API key)
- ✅ Set up Redis
- ✅ **PostgreSQL password: qwerty123**

---

## 📋 Remaining Steps (3 Steps Total)

### Step 1: Ensure PostgreSQL is Running
```cmd
REM Check Windows Services
Services > PostgreSQL > Start

OR use pgAdmin to start PostgreSQL service
```

### Step 2: Setup Database & Migrations
```cmd
cd f:\Freelance\Hita_App
complete_setup.bat
```

This will:
- Create database "hita"
- Create user "hita" with password "hita123"
- Enable pgvector extension
- Run all Django migrations

### Step 3: Start All 3 Services

**Open 3 Command Prompts:**

#### Terminal 1 - Redis (if not already running)
```cmd
redis-server
```

#### Terminal 2 - Django Backend
```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

#### Terminal 3 - Frontend (if not already running)
```cmd
cd f:\Freelance\Hita_App\frontend
npm run dev
```

---

## 🎯 Test the Application

1. Go to **http://localhost:3000**
2. Click **"Get Started"** or **"Sign Up"**
3. Enter email and password
4. Register ✅
5. Login ✅
6. Upload a document (PDF, Word, Image, etc.)
7. Wait for processing (status: uploaded → processing → ready)
8. Go to **"Ask Hita"** tab
9. Ask a question about your document
10. Hita answers using AI! 🎉

---

## 📊 Service Ports

| Service | Port | URL |
|---------|------|-----|
| **Frontend** | 3000 | http://localhost:3000 |
| **Backend API** | 8000 | http://localhost:8000/api |
| **Django Admin** | 8000 | http://localhost:8000/admin |
| **Redis** | 6379 | localhost:6379 |
| **PostgreSQL** | 5432 | localhost:5432 |

---

## 🔑 Credentials

| System | Username | Password |
|--------|----------|----------|
| **PostgreSQL (superuser)** | postgres | qwerty123 |
| **PostgreSQL (hita user)** | hita | hita123 |
| **Django Admin** | (create after migrate) | (create after migrate) |

---

## 🎮 Create Django Superuser (Optional)

After migrations, create admin account:
```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py createsuperuser
```

Then access at: http://localhost:8000/admin

---

## 📁 Project Structure

```
f:\Freelance\Hita_App\
├── backend/
│   ├── hita_project/        (Django config)
│   ├── apps/
│   │   ├── users/          (Auth)
│   │   ├── documents/      (File upload & parsing)
│   │   └── ai_engine/      (Gemini & embeddings)
│   ├── venv/               (Python virtual env)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            (Next.js pages)
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   ├── node_modules/
│   └── package.json
├── .env                    (Gemini API key)
└── [startup scripts]
```

---

## 🆘 Troubleshooting

### Django won't start
- Check PostgreSQL is running
- Check .env file exists with GEMINI_API_KEY
- Run: `python manage.py migrate` first

### Network error on registration
- Check Django is running on port 8000
- Check Redis is running on port 6379
- Refresh browser

### pgvector not found
- Optional for basic testing
- Install from: https://github.com/pgvector/pgvector

### Port already in use
- Kill the process using that port
- Or use different port (8001, 3001, etc.)

---

## ✨ Key Features

- 🔐 **JWT Authentication** - Email/password login
- 📄 **Multi-format Documents** - PDF, Word, Excel, Images, Text
- 🤖 **AI Processing** - Google Gemini for categorization & Q&A
- 🔍 **Semantic Search** - pgvector embeddings
- ⚡ **Async Processing** - Celery background tasks
- 🎨 **Beautiful UI** - Next.js + Tailwind CSS
- 📊 **Dashboard** - View documents by category

---

## 🎉 You're Ready!

Follow the 3 steps above to start Hita completely. Enjoy! 🚀
