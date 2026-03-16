# 🔧 Fix Network Error on Registration

## Problem
When you click "Sign Up" button, you get a **Network Error**. This means the frontend (port 3000) cannot reach the backend (port 8000).

---

## ✅ Status Check

**What's running:**
- ✅ Redis on port 6379
- ✅ Next.js Frontend on port 3000
- ❌ **Django Backend is NOT running on port 8000**

---

## 🚀 Solution - Start All 3 Services

### Option A: Quick Fix (3 Terminals)

**Terminal 1 - Redis:**
```cmd
redis-server
```

**Terminal 2 - Django Backend:**
```cmd
cd f:\Freelance\Hita_App\backend
python manage.py runserver 0.0.0.0:8000
```

**Terminal 3 - Next.js Frontend:**
```cmd
cd f:\Freelance\Hita_App\frontend
npm run dev
```

Then **refresh your browser** at http://localhost:3000

---

### Option B: Use Debug Script

Run this in a new terminal:
```cmd
cd f:\Freelance\Hita_App
start_backend_debug.bat
```

This will show any errors if Django fails to start.

---

## 🧪 Verify Services Are Running

Run this in a new terminal:
```cmd
cd f:\Freelance\Hita_App
troubleshoot.bat
```

This will check all 3 services and tell you which are running.

---

## ❓ Common Issues

### 1. "Address already in use" on port 8000
- Another Django instance is running
- **Solution:** Kill it with:
  ```cmd
  netstat -ano | findstr ":8000"
  taskkill /PID <PID> /F
  ```

### 2. "ModuleNotFoundError" in Django
- Dependencies not installed
- **Solution:**
  ```cmd
  cd f:\Freelance\Hita_App\backend
  pip install -r requirements.txt
  ```

### 3. "Database does not exist"
- PostgreSQL not configured
- **Solution:** Follow MANUAL_SETUP_WINDOWS.md for database setup

### 4. "redis.ConnectionError"
- Redis not running
- **Solution:** Start Redis in a separate terminal:
  ```cmd
  redis-server
  ```

---

## 📋 Port Reference

| Service | Port | Status |
|---------|------|--------|
| **Redis** | 6379 | ✅ Running |
| **Django** | 8000 | ❌ NOT Running |
| **Next.js** | 3000 | ✅ Running |
| **Celery** | - | Need to check |
| **PostgreSQL** | 5432 | Need to check |

---

## 🎯 Next Steps

1. **Start Terminal 2 with Django backend** using the command above
2. **Wait 5 seconds** for Django to initialize
3. **Refresh browser** at http://localhost:3000
4. **Try registering again** - Network Error should be gone! ✅

---

## 🆘 Still Having Issues?

Check backend logs:
```cmd
cd f:\Freelance\Hita_App\backend
python manage.py shell
```

Or test API directly:
```cmd
curl http://localhost:8000/api/auth/register/
```

Should return an error about missing credentials (which means backend IS running).
