# 🚀 DEPLOYMENT GUIDE - Railway + Hostinger Domain

## Quick Deployment Checklist

### ✅ Pre-Deployment (Complete)
- [x] All code tested locally
- [x] Virtual environment with all dependencies
- [x] Database working (SQLite locally, will use PostgreSQL on Railway)
- [x] `.gitignore` configured
- [x] `requirements.txt` with all dependencies
- [x] `Procfile` for web process
- [x] `railway.json` with database initialization
- [x] `init_production_db.py` for automatic setup

---

## 📋 STEP-BY-STEP DEPLOYMENT

### Step 1: Prepare Git Repository

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - MCA application ready for deployment"
```

### Step 2: Create Railway Account & Deploy

1. **Go to Railway:** https://railway.app
2. **Sign up/Login** (use GitHub account recommended)
3. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - If first time: Connect your GitHub account
   - Push your code to GitHub first, then select the repository
   
   **OR Use Railway CLI:**
   ```bash
   # Install Railway CLI
   brew install railway
   
   # Login
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a PostgreSQL database
   - Database credentials will be auto-configured

2. **Railway automatically sets:** `DATABASE_URL` environment variable
   - No manual configuration needed!

### Step 4: Configure Environment Variables

In Railway Project → Variables tab, add:

```bash
# Required Variables
SECRET_KEY=<generate-a-new-secret-key>
FLASK_ENV=production

# Optional - Admin Password (recommended to change default)
ADMIN_PASSWORD=<your-secure-admin-password>
```

**To generate a new SECRET_KEY:**
```bash
# Run locally to generate a secure key
python3 generate_secret_key.py
```

Copy the generated key and paste it into Railway's SECRET_KEY variable.

### Step 5: Deploy & Initialize

1. **Railway will automatically:**
   - Install dependencies from `requirements.txt`
   - Run `init_production_db.py` (creates tables + admin user)
   - Start the application with Gunicorn

2. **Check deployment logs:**
   - Look for: "✅ Database tables created successfully!"
   - Look for: "✅ Admin user created"

3. **Get your Railway URL:**
   - Format: `https://your-app-name.up.railway.app`
   - Test it by visiting the URL

### Step 6: Test Production Deployment

1. **Visit your Railway URL**
2. **Test the application form:** `/apply`
3. **Login as admin:** `/auth/login`
   - Email: `info@quicklinellc.com`
   - Password: Value from `ADMIN_PASSWORD` variable (or default: `ChangeMe123!`)
4. **Change admin password immediately!**

---

## 🌐 CONNECT HOSTINGER DOMAIN

### Step 1: Get Railway Domain Settings

1. In Railway Project → Settings → Domains
2. Click "Generate Domain" if you don't have one yet
3. Note your Railway URL: `your-app-name.up.railway.app`

### Step 2: Configure Hostinger DNS

1. **Login to Hostinger:** https://www.hostinger.com
2. **Go to:** Domains → Your Domain → DNS / Name Servers
3. **Add DNS Records:**

#### Option A: Use Root Domain (example.com)
Add these records:

```
Type: A
Name: @
Points to: <Railway-IP-Address>
TTL: 14400
```

**To get Railway IP:**
```bash
# In terminal
nslookup your-app-name.up.railway.app
```

#### Option B: Use Subdomain (www.example.com or app.example.com)
Add CNAME record:

```
Type: CNAME
Name: www (or app)
Points to: your-app-name.up.railway.app
TTL: 14400
```

**Recommended:** Use subdomain like `app.quicklinellc.com` for easier setup

### Step 3: Add Custom Domain in Railway

1. Railway Project → Settings → Domains
2. Click "Custom Domain"
3. Enter your domain: `app.quicklinellc.com`
4. Railway will automatically:
   - Provision SSL certificate (HTTPS)
   - Configure DNS validation

### Step 4: Wait for DNS Propagation

- **Time:** 5 minutes to 48 hours (usually 15-30 minutes)
- **Check status:** https://dnschecker.org

### Step 5: Test Custom Domain

1. Visit: `https://app.quicklinellc.com`
2. Verify SSL certificate is active (🔒 in browser)
3. Test all functionality

---

## 🔐 SECURITY CHECKLIST

### Before Going Live:

- [ ] Changed default admin password
- [ ] Generated new SECRET_KEY for production
- [ ] Verified FLASK_ENV=production
- [ ] Tested all login flows (admin, rep, customer)
- [ ] Tested application form submission
- [ ] Verified database is PostgreSQL (not SQLite)
- [ ] SSL certificate active on custom domain
- [ ] Created additional admin/rep users as needed

---

## 🛠️ POST-DEPLOYMENT TASKS

### Create Additional Users

**SSH into Railway or use Python console:**

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Create rep user
    rep = User(
        username='rep1',
        email='rep1@quicklinellc.com',
        role='rep',
        first_name='John',
        last_name='Smith'
    )
    rep.set_password('SecurePassword123!')
    
    db.session.add(rep)
    db.session.commit()
    print(f"Rep created: {rep.email}")
```

### Monitor Application

1. **Railway Dashboard:**
   - View logs in real-time
   - Monitor resource usage
   - Check deployment status

2. **Database Backups:**
   - Railway automatically backs up PostgreSQL
   - Can restore from any point in time

---

## 📊 DATABASE MANAGEMENT

### View Database (Railway CLI)

```bash
# Connect to production database
railway run bash

# Then run Python
python3
>>> from app import create_app, db
>>> from app.models import Application, User, Customer, LineOfCredit
>>> app = create_app()
>>> with app.app_context():
...     print(f"Applications: {Application.query.count()}")
...     print(f"Users: {User.query.count()}")
```

### Run Database Migrations (if models change)

```bash
# Locally first
flask db init
flask db migrate -m "Description of changes"
flask db upgrade

# Then commit and push
git add .
git commit -m "Database migration"
git push

# Railway will auto-deploy and run migrations
```

---

## 🔄 UPDATING THE APPLICATION

### Deploy Updates:

```bash
# Make changes locally
# Test locally first!

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub (if using GitHub integration)
git push

# OR use Railway CLI
railway up
```

Railway will automatically:
1. Pull latest code
2. Install any new dependencies
3. Restart the application
4. Keep database intact

---

## 🚨 TROUBLESHOOTING

### Application won't start
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure `DATABASE_URL` exists (should be automatic)

### Database connection errors
- Railway should auto-configure PostgreSQL connection
- Check if PostgreSQL service is running in Railway dashboard
- Verify `DATABASE_URL` variable exists

### Custom domain not working
- DNS propagation can take up to 48 hours
- Verify CNAME record points to correct Railway domain
- Check Railway domain settings for validation status

### Admin login not working
- Check `ADMIN_PASSWORD` environment variable
- Try default password: `ChangeMe123!`
- Check logs for "Admin user created" message

---

## 📞 SUPPORT RESOURCES

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Hostinger Support:** https://www.hostinger.com/support

---

## 🎯 FINAL CHECKLIST

- [ ] Application deployed to Railway
- [ ] PostgreSQL database connected
- [ ] Environment variables configured
- [ ] Database initialized with admin user
- [ ] Tested application form submission
- [ ] Tested admin login and dashboard
- [ ] Custom domain connected (Hostinger)
- [ ] SSL certificate active
- [ ] Admin password changed
- [ ] Additional users created
- [ ] All functionality tested in production

---

## 📧 DEFAULT CREDENTIALS

**Admin Login:**
- URL: `https://your-domain.com/auth/login`
- Email: `info@quicklinellc.com`
- Password: Set via `ADMIN_PASSWORD` environment variable (or `ChangeMe123!`)

**⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN!**

---

## 🎉 YOU'RE LIVE!

Once all checklist items are complete, your MCA application is ready to accept real applications!

**Share these URLs with your team:**
- Public Application: `https://your-domain.com/apply`
- Admin Login: `https://your-domain.com/auth/login`
- Rep Login: `https://your-domain.com/auth/login`
- Customer Login: `https://your-domain.com/auth/customer-login`
