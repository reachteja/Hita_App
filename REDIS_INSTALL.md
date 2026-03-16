# 🪷 Redis Installation Guide for Windows

Redis is required for Hita to work (for caching and Celery task queue).

## Quick Install (Recommended)

### Option 1: Chocolatey (Easiest) ⭐

1. **Open PowerShell as Administrator**
   - Right-click PowerShell → "Run as administrator"

2. **Run this command:**
   ```powershell
   choco install redis-64 -y
   ```

3. **Verify installation:**
   ```cmd
   redis-server --version
   ```

4. **Restart your terminal and try again:**
   ```cmd
   start_all.bat
   ```

---

## Option 2: Manual Installation (Windows)

### Step 1: Download Redis
- Visit: https://github.com/microsoftarchive/redis/releases
- Download the latest **Redis-x64-latest.zip** or **MSI installer**

### Step 2: Install/Extract
- **If ZIP:** Extract to `C:\Redis`
- **If MSI:** Install to `C:\Program Files\Redis`

### Step 3: Add to PATH (if extracted as ZIP)
1. Press `Win + X` → Choose "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", select "Path" → Click "Edit"
5. Click "New" and add: `C:\Redis`
6. Click "OK" three times

### Step 4: Verify
Open Command Prompt and run:
```cmd
redis-server --version
```

---

## Option 3: Use Docker

If you have Docker installed:

```cmd
docker run -d -p 6379:6379 redis
```

---

## Option 4: Use WSL2 (Windows Subsystem for Linux)

If you have WSL2 installed:

```bash
sudo apt-get update
sudo apt-get install redis-server
redis-server
```

---

## Troubleshooting

### Error: "'redis-server' is not recognized"
- Redis is not installed OR not in PATH
- **Solution:** Install using Option 1 above, then **restart your terminal**

### Port 6379 already in use
- Another Redis instance is running
- **Solution:** Run `redis-cli shutdown` to stop it

### Permission denied
- You don't have write permissions
- **Solution:** Run terminal as Administrator

---

## Verify Redis is Working

After installation, run:
```cmd
redis-cli ping
```

**Expected output:** `PONG`

If you see `PONG`, Redis is working! ✅

---

## Start Hita After Installing Redis

Once Redis is installed:

```cmd
cd f:\Freelance\Hita_App
start_all.bat
```

All 4 services should now launch successfully! 🚀
