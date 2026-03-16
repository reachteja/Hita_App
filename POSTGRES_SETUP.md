# 🗄️ PostgreSQL Installation & Setup Guide for Hita

## Step 1: Install PostgreSQL

### Download
1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Choose **PostgreSQL 16** (latest stable)

### Installation Steps
1. Run the installer
2. Follow the wizard
3. **Important - Remember these:**
   - Superuser Password: **qwerty123** ✅ (you provided this)
   - Port: **5432** (default)
   - Locale: English, United States
4. Click "Next" through the rest
5. Click "Finish" to complete

### Verify Installation
Open Command Prompt and run:
```cmd
psql --version
```

Should output something like: `psql (PostgreSQL) 16.x`

---

## Step 2: Create Database & User

Open Command Prompt and run these commands:

### Create Database
```cmd
psql -U postgres -c "CREATE DATABASE hita;"
```
When prompted, enter password: `qwerty123`

### Create User
```cmd
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"
```

### Grant Privileges
```cmd
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"
```

### Enable pgvector Extension
```cmd
psql -U postgres -d hita -c "CREATE EXTENSION pgvector;"
```

---

## Step 3: Verify Setup

Test the connection:
```cmd
psql -U hita -d hita -h localhost
```

Should connect without error. If it works, type `\q` to quit.

---

## Step 4: Run Django Migrations

Once database is ready:

```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py migrate
```

This creates all the tables in PostgreSQL.

---

## 🚀 Then Start the Backend

```cmd
python manage.py runserver 0.0.0.0:8000
```

Should now work! ✅

---

## ❓ Troubleshooting

### "psql: command not found"
- PostgreSQL not installed or not in PATH
- Solution: Reinstall PostgreSQL, make sure to add to PATH

### "password authentication failed"
- Wrong password for postgres user
- Solution: Use password you set during installation (qwerty123)

### "database hita already exists"
- Database was already created
- Just continue to Step 4

### "pgvector not found"
- pgvector not installed on this PostgreSQL
- It's optional for basic testing, but needed for AI features
- Install from: https://github.com/pgvector/pgvector/releases

---

## 📋 Quick Reference

| Item | Value |
|------|-------|
| **Database** | hita |
| **User** | hita |
| **Password** | hita123 |
| **Host** | localhost |
| **Port** | 5432 |
| **Superuser** | postgres |
| **Superuser Password** | qwerty123 |

