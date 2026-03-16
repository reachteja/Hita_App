# 🚀 HITA - Complete Launch Checklist

## Phase 1: System Prerequisites ✅ / ❌

- [ ] Python 3.9+ installed
- [ ] PostgreSQL 16 installed
- [ ] Redis installed
- [ ] Node.js installed
- [ ] Git (optional)

---

## Phase 2: Start PostgreSQL Service

### Windows Services Method (RECOMMENDED)

1. **Press:** `Win + R`
2. **Type:** `services.msc`
3. **Find:** Look for any of these:
   - postgresql-x64-16
   - postgresql-x64-15
   - PostgreSQL Database Server
   
4. **Right-click** on it → **Start**
5. **Wait** 3-5 seconds
6. **Refresh** the window (F5) - Status should show "Running"

### Verify PostgreSQL is Running

Open Command Prompt and run:
```cmd
psql -U postgres -c "SELECT version();"
```

**Expected output:**
```
PostgreSQL 16.x on x86_64-pc-windows...
```

If you see this, PostgreSQL is running! ✅

---

## Phase 3: Setup Database (After PostgreSQL is Running)

Open Command Prompt in `f:\Freelance\Hita_App\` and run:

```cmd
REM Create database
psql -U postgres -c "CREATE DATABASE hita;" ^
  && echo ✅ Database created ^
  || echo Database may already exist

REM Create user  
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';" ^
  && echo ✅ User created ^
  || echo User may already exist

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;" ^
  && echo ✅ Privileges granted ^
  || echo Already granted

REM Create pgvector extension
psql -U postgres -d hita -c "CREATE EXTENSION IF NOT EXISTS pgvector;" ^
  && echo ✅ pgvector enabled ^
  || echo pgvector not available
```

---

## Phase 4: Run Django Migrations

```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py migrate
```

**Expected:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  [... more migrations ...]
```

If you see "OK" for all migrations, you're ready! ✅

---

## Phase 5: Start All 3 Services

### Terminal 1: Redis
```cmd
redis-server
```

Expected:
```
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )
 |`-._`-...-` __...-.``-._|'` _.-'|
 |    `._.-._.-'|`._.-._.-'|_   .'
  `-._     `-._  `-._.-'      `-._.-'
 |`-._`-._    `-._.-'    _.-'_.-'|
 |    `-._`-._   -._    _.-'_.-'    |
  `-._    `-._`-._.-'_.-'_.-'    _.-'
 |`-._`-._    `-._.-'    _.-'_.-'|
 |    `-._`-._   -._    _.-'_.-'    |
  `-._    `-._`-._.-'_.-'_.-'    _.-'
      `-._    `-._.-'_.-'    _.-'
          `-._    `-.-'    _.-'
              `-._        _.-'
                  `-.__.-'

Ready to accept connections
```

Keep this terminal open ✅

### Terminal 2: Django Backend
```cmd
cd f:\Freelance\Hita_App\backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

Expected:
```
Watching for file changes with StatReloader
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Keep this terminal open ✅

### Terminal 3: Frontend (If Not Already Running)
```cmd
cd f:\Freelance\Hita_App\frontend
npm run dev
```

Expected:
```
▲ Next.js 14.x
- Local:        http://localhost:3000
```

---

## Phase 6: Test the Application

1. **Open browser:** http://localhost:3000
2. **Click:** "Get Started" or "Sign Up"
3. **Enter:** Email and password
4. **Click:** Register
5. **Login** with your credentials
6. **Upload:** A test document (PDF, Word, Image, etc.)
7. **Wait:** For status to change to "ready"
8. **Go to:** "Ask Hita" tab
9. **Ask:** A question like "What is the total amount?"
10. **Get:** AI answer! 🎉

---

## 🆘 Troubleshooting

### PostgreSQL Won't Start
- [ ] Is PostgreSQL installed? (Check: `psql --version`)
- [ ] Is service installed in Windows Services?
- [ ] Try manual start: `"C:\Program Files\PostgreSQL\16\bin\pg_ctl" -D "C:\Program Files\PostgreSQL\16\data" start`

### Django Migration Error
- [ ] PostgreSQL running? (`psql -U postgres -c "SELECT 1;"`)
- [ ] Database exists? (`psql -U postgres -c "\list"`)
- [ ] Check .env file exists with all values

### Network Error on Registration
- [ ] Redis running on 6379?
- [ ] Django running on 8000? (`netstat -ano | findstr :8000`)
- [ ] CORS configured? (Check settings.py)

### Document Upload Fails
- [ ] Celery running?
- [ ] Check backend terminal for error messages
- [ ] Is Tesseract OCR installed? (For image documents)

---

## 📊 Final Checklist Before Testing

- [ ] PostgreSQL running (port 5432)
- [ ] Database "hita" created
- [ ] User "hita" created with password "hita123"
- [ ] Migrations completed successfully
- [ ] Redis running (port 6379)
- [ ] Django running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] .env file exists with GEMINI_API_KEY
- [ ] All 3 terminals showing "running" status

---

## 🎉 You're Ready to Launch Hita!

Once all services are running, visit **http://localhost:3000** and enjoy! 🚀

