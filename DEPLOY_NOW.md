# 🚀 QUICK DEPLOY COMMANDS

## Deploy to Railway (Option 1: GitHub)

```bash
# 1. Initialize git (if not done)
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit - MCA application ready for deployment"

# 4. Create GitHub repository and push
# (Create repo on GitHub.com first, then:)
git remote add origin https://github.com/yourusername/your-repo-name.git
git branch -M main
git push -u origin main

# 5. Go to Railway.app
# - Sign up/Login
# - Click "New Project"
# - Select "Deploy from GitHub repo"
# - Select your repository
# - Add PostgreSQL database
# - Add environment variables:
#   SECRET_KEY=<generate-new-key>
#   FLASK_ENV=production
#   ADMIN_PASSWORD=<your-password>
```

## Deploy to Railway (Option 2: Railway CLI)

```bash
# 1. Install Railway CLI
brew install railway

# 2. Login
railway login

# 3. Initialize project in your directory
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC
railway init

# 4. Add PostgreSQL
railway add

# 5. Set environment variables
railway variables set SECRET_KEY=$(python3 generate_secret_key.py)
railway variables set FLASK_ENV=production
railway variables set ADMIN_PASSWORD=YourSecurePassword123!

# 6. Deploy
railway up

# 7. Open in browser
railway open
```

## Generate New Secret Key

```bash
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC
source venv/bin/activate
python3 generate_secret_key.py
```

## Test Local Before Deploy

```bash
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC
source venv/bin/activate
python3 run.py

# Visit: http://127.0.0.1:5000
# Test everything works
```

## After Deployment

1. **Get your Railway URL**: https://your-app.up.railway.app
2. **Test it**: Visit the URL and submit a test application
3. **Login**: https://your-app.up.railway.app/auth/login
   - Email: info@quicklinellc.com
   - Password: (your ADMIN_PASSWORD)
4. **Change password immediately!**

## Connect Hostinger Domain

### In Hostinger DNS:
```
Type: CNAME
Name: app
Points to: your-app.up.railway.app
TTL: 14400
```

### In Railway:
- Settings → Domains → Add Custom Domain
- Enter: app.quicklinellc.com
- Wait for DNS propagation (15-30 mins)
- SSL will auto-configure

## Quick Status Check

```bash
# Check Railway deployment status
railway status

# View logs
railway logs

# Connect to database
railway run bash
```

---

## 📁 All Files Ready for Deployment

✅ `run.py` - Application entry point
✅ `config.py` - Configuration
✅ `requirements.txt` - Dependencies
✅ `Procfile` - Web process command
✅ `railway.json` - Railway configuration
✅ `init_production_db.py` - Auto database setup
✅ `.gitignore` - Excludes sensitive files
✅ `app/` - Complete application code

---

## 🎯 YOU'RE READY TO DEPLOY!

Choose your method:
- **Easiest**: Railway CLI (commands above)
- **Most common**: GitHub → Railway

Both will work perfectly! 🚀
