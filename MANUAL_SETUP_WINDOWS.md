# 🪷 Hita - Manual Local Setup (Windows)

**Complete step-by-step guide to run Hita locally without Docker**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have these installed:

- [ ] **Python 3.12+** - Download from https://www.python.org/downloads/
- [ ] **PostgreSQL 16** - Download from https://www.postgresql.org/download/windows/
- [ ] **Redis** - Download from https://github.com/microsoftarchive/redis/releases
- [ ] **Tesseract OCR** - Download from https://github.com/UB-Mannheim/tesseract/wiki
- [ ] **Node.js 18+** - Download from https://nodejs.org/
- [ ] **Git** (optional) - Download from https://git-scm.com/
- [ ] **Gemini API Key** - Get free from https://aistudio.google.com/

---

## 🔧 STEP 1: Install System Dependencies

### 1.1 Python 3.12+

**Check if installed:**
```cmd
python --version
```

**If not installed:**
1. Download from https://www.python.org/downloads/
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

**Verify installation:**
```cmd
python --version
pip --version
```

### 1.2 PostgreSQL 16

**Download & Install:**
1. Go to https://www.postgresql.org/download/windows/
2. Download PostgreSQL 16
3. Run installer
4. Follow wizard:
   - Accept default installation path
   - Set password for `postgres` user: **remember this!**
   - Port: **5432** (default)
   - Locale: **Default**
5. Finish installation

**Verify installation:**
```cmd
psql --version
```

### 1.3 Redis

**Download & Extract:**
1. Go to https://github.com/microsoftarchive/redis/releases
2. Download `Redis-x64-X.X.X.msi` (latest version)
3. Run installer (default settings are fine)
4. Redis will be installed in `C:\Program Files\Redis`

**Verify installation:**
```cmd
redis-cli --version
```

### 1.4 Tesseract OCR

**Download & Install:**
1. Go to https://github.com/UB-Mannheim/tesseract/wiki
2. Download `tesseract-ocr-w64-setup-v5.x.x.exe` (latest)
3. Run installer
4. Use default installation path: `C:\Program Files\Tesseract-OCR`
5. Finish installation

**Verify installation:**
```cmd
tesseract --version
```

### 1.5 Node.js 18+

**Download & Install:**
1. Go to https://nodejs.org/
2. Download LTS version (18+ or 20+)
3. Run installer (all defaults are fine)
4. Finish installation

**Verify installation:**
```cmd
node --version
npm --version
```

---

## ✅ STEP 2: Setup Backend

### 2.1 Create Virtual Environment

```cmd
# Navigate to backend folder
cd f:\Freelance\Hita_App\backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**You should see `(venv)` in your terminal prompt.**

### 2.2 Install Python Dependencies

```cmd
# Make sure you're in the backend folder with venv activated
pip install -r requirements.txt
```

This will install:
- Django 5.0.0
- Django REST Framework
- PostgreSQL driver
- Celery + Redis
- Gemini AI
- And more...

**Installation takes 3-5 minutes. Wait for it to complete.**

### 2.3 Create Database

**Open a new Command Prompt (keep venv terminal open):**

```cmd
# Connect to PostgreSQL
psql -U postgres

# Inside psql prompt, run:
CREATE DATABASE hita;
CREATE USER hita WITH PASSWORD 'hita123';
ALTER ROLE hita SET client_encoding TO 'utf8';
ALTER ROLE hita SET default_transaction_isolation TO 'read committed';
ALTER ROLE hita SET default_transaction_deferrable TO on;
ALTER ROLE hita SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE hita TO hita;

# Exit psql
\q
```

**Verify database created:**
```cmd
psql -U hita -d hita -c "SELECT version();"
```

### 2.4 Configure Environment

```cmd
# In backend folder
copy .env.example .env
```

**Open `.env` file and update:**

```ini
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=hita
DB_USER=hita
DB_PASSWORD=hita123
DB_HOST=localhost
DB_PORT=5432

# Redis / Celery
REDIS_URL=redis://localhost:6379/0

# Gemini API (Get from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# File upload
MAX_UPLOAD_SIZE_MB=25

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# Frontend
FRONTEND_URL=http://localhost:3000
```

### 2.5 Run Database Migrations

```cmd
# Make sure you're in backend folder with venv activated
python manage.py migrate
```

This creates all database tables. You should see:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying ai_engine.0001_initial... OK
```

### 2.6 Create Django Superuser (Optional - for Admin Panel)

```cmd
python manage.py createsuperuser
```

Follow prompts:
- Email: admin@hita.app
- Full Name: Admin User
- Password: (choose a password)

---

## 🚀 STEP 3: Start Backend Services

### 3.1 Start PostgreSQL

**PostgreSQL should auto-start on Windows. Verify:**
```cmd
psql -U hita -d hita -c "SELECT 1;"
```

If not running, start it:
- Search "Services" in Windows
- Find "postgresql-x64-16"
- Right-click → Start

### 3.2 Start Redis

**Open new Command Prompt:**
```cmd
redis-server
```

You should see:
```
oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
Ready to accept connections
```

**Keep this terminal open.**

### 3.3 Start Django

**In your first terminal (backend folder with venv activated):**

```cmd
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Keep this terminal open. Backend is running at http://localhost:8000**

### 3.4 Start Celery Worker

**Open a third Command Prompt:**

```cmd
# Navigate to backend
cd f:\Freelance\Hita_App\backend

# Activate venv
venv\Scripts\activate

# Start Celery (Windows requires --pool=solo)
celery -A hita_project worker --loglevel=info --pool=solo
```

You should see:
```
 -------------- celery@YOUR-PC v5.3.4 (pool: solo)
---------- [config]
. broker:      redis://localhost:6379/0
. app:         hita_project:0x...
```

**Keep this terminal open. Celery worker is processing background tasks.**

---

## 🎨 STEP 4: Setup Frontend

### 4.1 Install Dependencies

**Open a fourth Command Prompt:**

```cmd
cd f:\Freelance\Hita_App\frontend
npm install
```

Installation takes 3-5 minutes. Wait for:
```
added XXX packages
```

### 4.2 Configure Environment

```cmd
copy .env.local.example .env.local
```

**`.env.local` should contain:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**This is already set correctly.**

### 4.3 Start Frontend

```cmd
npm run dev
```

You should see:
```
> hita-frontend@0.1.0 dev
> next dev

  ▲ Next.js 14.0.0
  - Local:        http://localhost:3000
```

**Keep this terminal open. Frontend is running at http://localhost:3000**

---

## ✅ STEP 5: Verify Everything Works

### 5.1 Check Services Status

**Open http://localhost:3000 in your browser:**

You should see:
- 🪷 Hita logo
- "Your Personal Document Buddy" heading
- Register and Login buttons

### 5.2 Check Backend API

**Open http://localhost:8000/api/ in your browser:**

You should see Django REST Framework interface.

### 5.3 Check Admin Panel (Optional)

**Go to http://localhost:8000/admin/**
- Login with superuser credentials
- You can manage users, documents, etc.

---

## 🧪 STEP 6: Test the Application

### 6.1 Register a User

1. Go to http://localhost:3000
2. Click "Register"
3. Fill the form:
   - Email: `test@hita.app`
   - Full Name: `Test User`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
   - ✅ Check "I agree to terms"
4. Click "Register"

Expected: Redirects to dashboard with welcome message

### 6.2 Upload a Document

1. Go to Dashboard → Documents
2. Click "Choose file"
3. Select any file (PDF, Word, Excel, Image, or Text)
4. Status should change:
   - `uploaded` → `processing` → `ready`

**Behind the scenes:**
- Django saves your file
- Celery task starts async processing
- Text is extracted
- PII is scrubbed
- Embeddings are created
- Gemini categorizes it

### 6.3 Ask a Question

1. Go to Dashboard → Ask Hita
2. Type: "What documents do I have?"
3. Click Send

Expected: Hita responds with information from your documents

---

## 📊 Terminal Setup Summary

You need **4 terminals open** (or use tmux/split-pane):

| Terminal | Command | Port |
|----------|---------|------|
| 1 | `python manage.py runserver` | 8000 (Django) |
| 2 | `redis-server` | 6379 (Redis) |
| 3 | `celery -A hita_project worker --loglevel=info --pool=solo` | - (Celery) |
| 4 | `npm run dev` | 3000 (Frontend) |

---

## 🐛 Troubleshooting

### Error: "No module named 'django'"
```cmd
# Solution: Make sure venv is activated
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "psycopg2 connection refused"
```cmd
# PostgreSQL not running
# Start it from Windows Services or:
psql -U postgres
```

### Error: "Can't connect to Redis"
```cmd
# Redis not running
redis-server
```

### Error: "Tesseract not found"
```cmd
# Add to your .env:
# Or reinstall Tesseract ensuring it's in PATH
```

### Error: "GEMINI_API_KEY not set"
```cmd
# Add your API key to .env
GEMINI_API_KEY=your_actual_key_here
```

### Error: "Port 8000/3000 already in use"
```cmd
# Kill the process using the port:
# For Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📚 Useful Commands

### Django Commands
```cmd
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic
```

### PostgreSQL Commands
```cmd
# Connect to database
psql -U hita -d hita

# List all databases
\l

# List all tables
\dt

# Exit
\q
```

### Redis Commands
```cmd
# Connect to Redis CLI
redis-cli

# Check if Redis is running
ping

# Exit
exit
```

### Frontend Commands
```cmd
# Build for production
npm run build

# Start production build
npm start

# Run linter
npm run lint
```

---

## 🎯 Next Steps

1. **Explore the Dashboard**
   - Upload different file types
   - Test categorization
   - Ask various questions

2. **Check the Admin Panel**
   - Go to http://localhost:8000/admin/
   - View users, documents, tasks

3. **Monitor Celery Tasks**
   - Install Flower: `pip install flower`
   - Run: `flower -A hita_project`
   - Visit: http://localhost:5555

4. **Review Code**
   - Backend: `f:\Freelance\Hita_App\backend\`
   - Frontend: `f:\Freelance\Hita_App\frontend\`

5. **Read Documentation**
   - `README.md` - Full guide
   - `HITA_CONTEXT.md` - Technical details
   - `copilot-instructions.md` - AI context

---

## 🆘 Need Help?

If something doesn't work:

1. **Check terminal output** for error messages
2. **Verify all services are running** (Django, Redis, Celery, Frontend)
3. **Check `.env` file** has correct values
4. **Restart services** if needed
5. **Check port conflicts**: `netstat -ano | findstr :PORT`

---

## ✨ You're All Set!

When all 4 services are running:
- ✅ Frontend: http://localhost:3000
- ✅ Backend API: http://localhost:8000/api
- ✅ Django Admin: http://localhost:8000/admin
- ✅ PostgreSQL: localhost:5432
- ✅ Redis: localhost:6379

**Happy coding! 🪷**
