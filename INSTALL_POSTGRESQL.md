# ⚠️ PostgreSQL Not Installed

## Current Status
❌ PostgreSQL is **NOT installed** on this system
❌ `psql` command not found

---

## 🚀 Install PostgreSQL - Step by Step

### Step 1: Download PostgreSQL 16

Visit: **https://www.postgresql.org/download/windows/**

Click: **"Download the installer"**

Choose: **PostgreSQL 16** (latest stable version)

### Step 2: Run the Installer

1. Double-click the downloaded `.exe` file
2. Click "Next" on the welcome screen
3. Accept the default installation directory: `C:\Program Files\PostgreSQL\16`
4. Click "Next"

### Step 3: Installation Components

Make sure these are **CHECKED:**
- ✅ PostgreSQL Server
- ✅ pgAdmin 4 (GUI tool - helpful!)
- ✅ Stack Builder (to install pgvector later)
- ✅ Command Line Tools (psql)

Click "Next"

### Step 4: Set Data Directory

Default is fine:
- `C:\Program Files\PostgreSQL\16\data`

Click "Next"

### Step 5: Set Superuser Password

**Password for postgres user:**
```
qwerty123
```

**Confirm Password:**
```
qwerty123
```

⚠️ **IMPORTANT:** Remember this password!

Click "Next"

### Step 6: Port Number

Default port: **5432** ✅ (keep as is)

Click "Next"

### Step 7: Locale

Select: **English, United States** ✅

Click "Next"

### Step 8: Review Summary

Should look like:
```
Installation Summary
PostgreSQL 16
Installation Directory: C:\Program Files\PostgreSQL\16
Data Directory: C:\Program Files\PostgreSQL\16\data
Port: 5432
Locale: English, United States
```

Click "Next" to start installation

### Step 9: Installation Progress

Wait for installation to complete (2-5 minutes)

You'll see: ✅ "Installation Completed"

### Step 10: Stack Builder

A "Stack Builder" dialog may appear.

For now, just click "Finish" (we can install pgvector later if needed)

---

## ✅ Verify Installation

After installation completes, open **Command Prompt** and run:

```cmd
psql --version
```

Should output:
```
psql (PostgreSQL) 16.x on x86_64-pc-windows-msvc
```

If you see this, PostgreSQL is installed! ✅

---

## 🚀 Start PostgreSQL Service

### Method 1: Windows Services (Automatic)

1. Press: `Win + R`
2. Type: `services.msc`
3. Find: `postgresql-x64-16`
4. Status should show: **Running**

If it shows **Stopped**, right-click → **Start**

### Method 2: Manual Start

```cmd
"C:\Program Files\PostgreSQL\16\bin\pg_ctl" -D "C:\Program Files\PostgreSQL\16\data" start
```

---

## ✅ Test Connection

```cmd
psql -U postgres -c "SELECT version();"
```

When prompted, enter password: `qwerty123`

Should output PostgreSQL version! ✅

---

## 📋 After Installation

Once PostgreSQL is installed and running, continue with:

1. **Create database:**
   ```cmd
   psql -U postgres -c "CREATE DATABASE hita;"
   ```

2. **Create user:**
   ```cmd
   psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"
   ```

3. **Grant privileges:**
   ```cmd
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"
   ```

4. **Create pgvector extension:**
   ```cmd
   psql -U postgres -d hita -c "CREATE EXTENSION pgvector;"
   ```

5. **Run migrations:**
   ```cmd
   cd f:\Freelance\Hita_App\backend
   call venv\Scripts\activate.bat
   python manage.py migrate
   ```

---

## 🎯 Next Step

👉 **Install PostgreSQL 16 using the steps above, then return and run migrations!**

