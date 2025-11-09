# QuickLine LLC - Quick Start Guide

## Local Development (5 minutes)

### 1. Install Dependencies
```bash
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///app.db
FLASK_ENV=development
```

### 3. Run Setup Script
```bash
python setup.py
```

This will:
- Create database tables
- Create an admin user
- Optionally create a sample rep

### 4. Start the Application
```bash
python run.py
```

Visit: http://localhost:5000

## Railway Deployment (10 minutes)

### 1. Push to GitHub (if not already)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-repo-url
git push -u origin main
```

### 2. Deploy to Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect configuration

### 3. Add PostgreSQL
1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set DATABASE_URL

### 4. Set Environment Variables
In Railway dashboard → Variables:
```
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
```

### 5. Run Initial Setup
In Railway terminal:
```bash
# Initialize database
flask db upgrade

# Create admin user (one-line command)
python -c "from app import create_app, db; from app.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); admin=User(username='admin', email='admin@yourcompany.com', role='admin', first_name='Admin', last_name='User'); admin.set_password('YourSecurePassword123!'); db.session.add(admin); db.session.commit(); print('✅ Admin created!'); ctx.pop()"
```

### 6. Connect Custom Domain (Hostinger)

#### In Railway:
1. Settings → Domains → "Custom Domain"
2. Enter your domain: `www.yourdomain.com`
3. Copy the CNAME target provided

#### In Hostinger:
1. Go to your domain's DNS settings
2. Add CNAME record:
   - Type: CNAME
   - Name: www
   - Target: [Railway CNAME from step 3]
   - TTL: 14400

3. For root domain, add:
   - Type: A
   - Name: @
   - Target: [Railway provides IP]
   - TTL: 14400

Wait 24-48 hours for DNS propagation.

## Testing the Application

### Admin Login
1. Go to `/auth/login`
2. Email: admin@yourcompany.com
3. Password: [what you set]

### Test Customer Flow
1. Go to `/apply` (public form)
2. Fill out application
3. Login as admin
4. Approve application
5. Create line of credit
6. Assign to rep
7. Customer can login at `/auth/customer-login`

### Test Rep Login
1. Create a rep user in admin panel
2. Assign deals to the rep
3. Rep logs in at `/auth/login`
4. Rep sees only assigned deals

## Common Issues

### Database Connection Error
- Check DATABASE_URL in environment variables
- For local: ensure PostgreSQL is running
- For Railway: ensure PostgreSQL service is connected

### Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Migration Issues
```bash
# Reset migrations
rm -rf migrations
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

## Features Checklist

- ✅ Public application form
- ✅ Admin dashboard (view/approve applications)
- ✅ Create/manage lines of credit
- ✅ User management (admin/reps)
- ✅ Rep dashboard (assigned deals only)
- ✅ Customer portal (view credit line)
- ✅ Assign deals to reps
- ✅ Railway deployment ready
- ✅ Custom domain support
- ✅ PostgreSQL database
- ✅ Secure authentication
- ✅ Responsive design

## Support

Check the main README.md for detailed documentation.
