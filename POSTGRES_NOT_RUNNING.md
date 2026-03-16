# 🔧 PostgreSQL Not Running - Diagnostic & Fix

## Current Status
❌ PostgreSQL service is **NOT running**

---

## Quick Fix - Start PostgreSQL

### Option 1: Windows Services (Recommended)
1. Press `Win + R`
2. Type: `services.msc`
3. Find: **postgresql-x64-16** (or similar)
4. Right-click → **Start**
5. Wait 5 seconds for it to start

### Option 2: Command Line
```cmd
net start postgresql-x64-16
REM or
sc start postgresql-x64-16
```

### Option 3: pgAdmin
1. Open **pgAdmin** (should be installed with PostgreSQL)
2. Look for PostgreSQL service control
3. Start the service

### Option 4: Manual Start
```cmd
"C:\Program Files\PostgreSQL\16\bin\pg_ctl" -D "C:\Program Files\PostgreSQL\16\data" start
```

---

## Verify PostgreSQL is Running

After starting, run:
```cmd
psql -U postgres -c "SELECT version();"
```

Should output PostgreSQL version.

---

## If PostgreSQL is Still Not Found

### PostgreSQL Not Installed?
If you get "psql: command not found", PostgreSQL is not installed.

**Install PostgreSQL:**
1. Download: https://www.postgresql.org/download/windows/
2. Run installer
3. Set superuser password to: `qwerty123`
4. Complete installation
5. Start PostgreSQL service

---

## After Starting PostgreSQL

Run these commands to setup database:

```cmd
REM Create database
psql -U postgres -c "CREATE DATABASE hita;"

REM Create user
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"

REM Create pgvector extension
psql -U postgres -d hita -c "CREATE EXTENSION IF NOT EXISTS pgvector;"
```

---

## Run Django Migrations

```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py migrate
```

---

## ✅ Verify Everything Works

```cmd
psql -U hita -d hita -c "SELECT * FROM users_hitauser LIMIT 1;"
```

If no error, database is ready! ✅

---

## Next: Start All Services

After PostgreSQL is running and migrations complete:

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
Frontend already running on http://localhost:3000

Then visit http://localhost:3000 and test! 🚀
