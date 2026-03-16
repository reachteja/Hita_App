# 🚨 CRITICAL - PostgreSQL Installation Required

## Current Status

✅ **Ready:**
- Backend code (Django) - Complete
- Frontend code (Next.js) - Complete  
- Python packages - Installed
- Redis - Installed & Running
- Gemini API key - Configured

❌ **MISSING:**
- PostgreSQL 16 - **NOT INSTALLED**

---

## 🎯 YOU NEED TO DO THIS NOW

### What is PostgreSQL?
PostgreSQL is the database that stores:
- User accounts
- Uploaded documents  
- AI embeddings (vector search)
- Document metadata

Without it, Hita **CANNOT run**.

---

## ⚡ 5-Minute Installation

### Step 1: Download
Go to: https://www.postgresql.org/download/windows/

Click: "Download the installer"

Download: **PostgreSQL 16**

### Step 2: Install
1. Run the downloaded file
2. Click "Next" through all screens
3. **When asked for superuser password, enter:** `qwerty123`
4. **When asked for port, use:** `5432` (default)
5. Click "Next" → "Install" → "Finish"

That's it! ✅

### Step 3: Verify

Open Command Prompt and run:
```cmd
psql --version
```

Should show: `psql (PostgreSQL) 16.x`

---

## ✅ After PostgreSQL is Installed

Run these commands in Command Prompt:

```cmd
REM Create database
psql -U postgres -c "CREATE DATABASE hita;"

REM Create user
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"

REM Create pgvector extension
psql -U postgres -d hita -c "CREATE EXTENSION pgvector;"
```

When prompted for password, enter: `qwerty123`

---

## 🚀 Then Run Migrations

```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py migrate
```

---

## 🚀 Then Start All Services

**Terminal 1:**
```cmd
redis-server
```

**Terminal 2:**
```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

**Terminal 3:**
http://localhost:3000 (frontend)

---

## 🎉 Then Test Hita

1. Go to: http://localhost:3000
2. Sign up
3. Upload document
4. Ask a question
5. Get AI answer! 🎉

---

## 📖 Full Guide

See: `INSTALL_POSTGRESQL.md` in this folder for detailed steps.

---

## 🆘 Issues?

**psql command not found?**
- PostgreSQL not installed
- OR not in PATH
- See INSTALL_POSTGRESQL.md

**Password error?**
- Make sure you used `qwerty123` as superuser password
- Note: Different from hita user password (`hita123`)

**Port 5432 already in use?**
- Another PostgreSQL might be running
- Use pgAdmin to check

---

## ⏱️ Estimated Time

- Download PostgreSQL: 5 min
- Install PostgreSQL: 5-10 min
- Create database: 1 min
- Run migrations: 2 min
- **Total: ~15-20 minutes**

---

## ✨ Then You're Done!

Once PostgreSQL is installed and database is set up, Hita will be fully operational! 🚀

**Start with: INSTALL_POSTGRESQL.md** 👈

