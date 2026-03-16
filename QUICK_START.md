# 🪷 Hita Manual Setup - Quick Reference

## ⚡ TL;DR - Super Quick Start (Experienced Users)

```cmd
# 1. Python venv + dependencies
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Database (psql)
createdb hita
psql -U postgres -d hita -c "CREATE USER hita WITH PASSWORD 'hita123';"
# ... (see MANUAL_SETUP_WINDOWS.md for full SQL)

# 3. .env configuration
copy .env.example .env
# Edit .env and add GEMINI_API_KEY

# 4. Migrations
python manage.py migrate

# 5. FOUR TERMINALS:
# Terminal 1:
python manage.py runserver

# Terminal 2:
redis-server

# Terminal 3:
celery -A hita_project worker --loglevel=info --pool=solo

# Terminal 4:
cd ..\frontend
npm install
npm run dev
```

---

## ✅ Pre-Flight Checklist

Before you start, verify:

- [ ] Python 3.12+ installed: `python --version`
- [ ] PostgreSQL installed: `psql --version`
- [ ] Redis installed: `redis-cli --version`
- [ ] Tesseract installed: `tesseract --version`
- [ ] Node.js installed: `node --version`
- [ ] Gemini API key obtained: https://aistudio.google.com/

---

## 📍 Locations

All paths relative to: `f:\Freelance\Hita_App\`

| Component | Path | Port |
|-----------|------|------|
| Backend | `backend/` | 8000 |
| Frontend | `frontend/` | 3000 |
| Database | PostgreSQL | 5432 |
| Cache | Redis | 6379 |

---

## 🎯 5-Minute Startup Sequence

After first-time setup, to start the app:

**Terminal 1 - Backend**
```cmd
cd f:\Freelance\Hita_App\backend
venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Redis**
```cmd
redis-server
```

**Terminal 3 - Celery**
```cmd
cd f:\Freelance\Hita_App\backend
venv\Scripts\activate
celery -A hita_project worker --loglevel=info --pool=solo
```

**Terminal 4 - Frontend**
```cmd
cd f:\Freelance\Hita_App\frontend
npm run dev
```

Then open: http://localhost:3000

---

## 📚 Full Setup Guide

See `MANUAL_SETUP_WINDOWS.md` for complete step-by-step instructions with:
- Detailed system dependency installation
- Database setup with SQL
- Environment configuration
- Troubleshooting
- Testing procedures

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError: No module named 'django' | Run `pip install -r requirements.txt` with venv activated |
| connection refused (PostgreSQL) | Start PostgreSQL via Windows Services |
| Error from the Celery worker (Redis) | Start Redis: `redis-server` |
| Port 8000 already in use | Kill process: `netstat -ano \| findstr :8000` then `taskkill /PID XXX /F` |
| GEMINI_API_KEY error | Add your API key to `.env` file |
| Tesseract not found | Reinstall Tesseract, ensure `C:\Program Files\Tesseract-OCR` is in PATH |

---

## 🔗 Quick Links

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin
- Documentation: `README.md`, `MANUAL_SETUP_WINDOWS.md`

---

## ✨ What Happens After Setup

1. **Register** at http://localhost:3000
2. **Upload** a document (PDF, Word, Excel, Image, Text)
3. **Wait** for Celery to process it (extract text, scrub PII, embed, categorize)
4. **Ask** questions in the "Ask Hita" interface
5. **Get** AI-powered answers from your documents

---

**Ready? Start with Terminal 1!** 🚀
