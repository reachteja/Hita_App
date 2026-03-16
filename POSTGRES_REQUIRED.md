# 🚨 IMMEDIATE ACTION REQUIRED: Install PostgreSQL

## Current Error
```
'psql' is not recognized as an internal or external command
```

**Meaning:** PostgreSQL is not installed on your computer.

---

## ⚡ Quick Install (5 Steps, 10 minutes)

### Step 1: Download PostgreSQL
**URL:** https://www.postgresql.org/download/windows/

**Action:** Click "Download the installer" → Download PostgreSQL 16

### Step 2: Run Installer
1. Double-click the downloaded `.exe` file
2. Click "Next" on welcome screen

### Step 3: Installation Path
- Keep default: `C:\Program Files\PostgreSQL\16`
- Click "Next"

### Step 4: Set Password
**This is CRITICAL - Enter exactly:**

```
Username: postgres (already filled)
Password: qwerty123
Confirm:  qwerty123
```

⚠️ **Write this down: `qwerty123`**

Click "Next"

### Step 5: Complete Installation
- Port: `5432` (default - keep it)
- Locale: English, United States
- Click "Next" → "Install"
- Wait 2-5 minutes
- Click "Finish"

---

## ✅ Verify Installation

Open **Command Prompt** and run:
```cmd
psql --version
```

**Expected output:**
```
psql (PostgreSQL) 16.x on x86_64-pc-windows-msvc
```

If you see this, PostgreSQL is installed! ✅

---

## 🗄️ Create Database

After PostgreSQL is installed, run these 4 commands:

```cmd
psql -U postgres -c "CREATE DATABASE hita;"
```
When prompted, enter: `qwerty123`

```cmd
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"
```

```cmd
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"
```

```cmd
psql -U postgres -d hita -c "CREATE EXTENSION pgvector;"
```

**Expected output:** All should run without errors

---

## 🚀 Run Django Migrations

After database is created:

```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py migrate
```

**Expected output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## ✅ You're Almost Done!

Once migrations complete, start all 3 services:

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
http://localhost:3000 (already running)

---

## 🎉 Test Hita

1. Go to: http://localhost:3000
2. Click "Sign Up"
3. Create account
4. Upload document
5. Ask a question
6. Get AI answer! 🎉

---

## 🆘 Troubleshooting

### "psql command not found" after installation?

**Solution 1: Add to PATH**
1. Open System Properties → Environment Variables
2. Find "Path" under System Variables
3. Click "Edit" → "New"
4. Add: `C:\Program Files\PostgreSQL\16\bin`
5. Click "OK" three times
6. Restart Command Prompt
7. Try: `psql --version`

**Solution 2: Use full path**
```cmd
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -c "SELECT version();"
```

### "password authentication failed"?

- Make sure you used: `qwerty123` (not `hita123`)
- Superuser = postgres user
- Hita user = hita (password: hita123)

### "database hita already exists"?

- Just continue, database is already set up
- Run migrations: `python manage.py migrate`

---

## 📋 Credentials Reference

| System | Username | Password |
|--------|----------|----------|
| **PostgreSQL (superuser)** | postgres | qwerty123 |
| **PostgreSQL (hita user)** | hita | hita123 |
| **Django Admin** | (create after migrate) | (create after migrate) |

---

## ⏱️ Timeline

- Download PostgreSQL: 5 minutes
- Install PostgreSQL: 5-10 minutes
- Create database: 1 minute
- Run migrations: 2 minutes
- **Total: 15-20 minutes**

---

## 📖 Next Actions

1. **Download & Install PostgreSQL** from: https://www.postgresql.org/download/windows/
2. **Set superuser password to:** `qwerty123`
3. **Create database** using commands above
4. **Run migrations**
5. **Start all services**
6. **Visit http://localhost:3000**

---

## ✨ You're So Close!

PostgreSQL installation is the last missing piece. After that, Hita will be fully functional! 🚀

**Start downloading PostgreSQL now!** 👆

