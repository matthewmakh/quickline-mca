# 🚀 GETTING STARTED - QuickLine LLC MCA Platform

## What You Have

✅ Complete MCA web application
✅ Public application form for potential clients
✅ Admin dashboard for managing applications and deals
✅ Rep dashboard (reps see only their assigned deals)
✅ Customer portal (customers see their line of credit)
✅ Ready for Railway deployment
✅ Custom domain support (Hostinger)
✅ PostgreSQL database configured
✅ All templates and functionality complete

---

## 🏃 Quick Start (Choose One)

### Option A: Local Development (Testing)

```bash
# 1. Navigate to project
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate secret key
python3 generate_secret_key.py

# 5. Create .env file
cp .env.example .env
# Edit .env and paste the secret key

# 6. Run setup (creates database + admin user)
python3 setup.py

# 7. Start the application
python3 run.py
```

**Access the app**: http://localhost:5000

---

### Option B: Deploy to Railway (Production)

#### Step 1: Prepare for Deployment
```bash
cd /Users/matthewmakh/PycharmProjects/QuickLineLLC

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - QuickLine LLC MCA Platform"

# Create GitHub repo and push
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

#### Step 2: Railway Setup
1. Go to https://railway.app and sign up/login
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your QuickLine LLC repository
5. Railway will detect the configuration automatically

#### Step 3: Add PostgreSQL
1. In your Railway project, click **"New"** → **"Database"**
2. Select **"PostgreSQL"**
3. Railway auto-connects it (DATABASE_URL set automatically)

#### Step 4: Set Environment Variables
Click your web service → **"Variables"** → Add:
```
SECRET_KEY=run-generate_secret_key.py-and-paste-here
FLASK_ENV=production
```

#### Step 5: Initialize Database
In Railway → **"Terminal"**:
```bash
flask db upgrade
```

Create admin user:
```bash
python -c "from app import create_app, db; from app.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); admin=User(username='admin', email='admin@quickline.com', role='admin', first_name='Admin', last_name='User'); admin.set_password('YourPassword123!'); db.session.add(admin); db.session.commit(); print('Admin created!'); ctx.pop()"
```

#### Step 6: Connect Your Hostinger Domain
**In Railway:**
1. Settings → Domains → "Add Domain"
2. Enter: `www.yourdomain.com`
3. Copy the CNAME value shown

**In Hostinger:**
1. Login to Hostinger
2. Domains → Your Domain → DNS Records
3. Add CNAME Record:
   - Type: CNAME
   - Name: www
   - Points to: [Paste Railway CNAME]
   - TTL: 14400

Wait 24-48 hours for DNS to propagate.

---

## 🎯 Test Your Application

### 1. Test Public Application Form
- Go to: `/apply`
- Fill out the business application form
- Submit

### 2. Login as Admin
- Go to: `/auth/login`
- Email: admin@quickline.com
- Password: [what you set]

### 3. Approve Application
- Go to Applications
- Click "View" on the submitted application
- Click "Approve Application"
- This creates a customer account

### 4. Create Line of Credit
- After approval, click "Create Line of Credit"
- Set:
  - Approved Amount: $50,000
  - Used Amount: $10,000
  - Interest Rate: 12%
  - Payment Frequency: Monthly
  - Payment Amount: $1,500
  - Term: 12 months
- Save

### 5. Create a Rep User
- Go to Users → Create User
- Create a rep account
- Username: rep1
- Email: rep1@quickline.com
- Role: Rep

### 6. Assign Deal to Rep
- Go to Deals
- Click "View" on the line of credit
- Click "Assign Rep"
- Select the rep and assign

### 7. Test Rep Login
- Logout
- Go to `/auth/login`
- Login as the rep
- You should see ONLY assigned deals

### 8. Test Customer Login
- Go to `/auth/customer-login`
- Email: [the owner email from application]
- Password: TempPass123! (default, should be changed)
- View your credit line details

---

## 📋 What Each User Sees

### Admin (Full Access)
- Dashboard with all stats
- All applications (pending/approved/rejected)
- All customers
- All lines of credit
- Create/edit/delete everything
- Manage users (create admins and reps)
- Assign deals to reps

### Rep (Limited Access)
- Dashboard with ONLY their assigned deals
- Can view customer details for assigned deals
- Can contact customers
- Cannot create/edit/delete
- Cannot see other reps' deals

### Customer (Personal Access)
- Dashboard showing their credit line
- Approved amount vs used vs available
- Interest rate and payment terms
- Payment schedule
- Outstanding balance
- Assigned rep contact info

---

## 🔗 URLs

### Public
- **Homepage**: `/`
- **Apply for Funding**: `/apply`

### Staff
- **Admin/Rep Login**: `/auth/login`
- **Admin Dashboard**: `/admin/dashboard`
- **Rep Dashboard**: `/rep/dashboard`

### Customer
- **Customer Login**: `/auth/customer-login`
- **Customer Dashboard**: `/customer/dashboard`

---

## 📚 Documentation Files

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute setup guide
- **DEPLOYMENT.md** - Railway deployment checklist
- **PROJECT_SUMMARY.md** - Feature overview

---

## 🆘 Need Help?

### Common Issues

**"Import errors"**
```bash
pip install -r requirements.txt
```

**"Database connection failed"**
- Check .env file has correct DATABASE_URL
- For local: use SQLite (default)
- For Railway: PostgreSQL auto-configured

**"Page not found"**
- Make sure Flask app is running
- Check URL spelling
- Verify routes are registered

**"Can't login"**
- Verify user was created (run setup.py)
- Check email and password
- Try resetting database and running setup again

---

## 🎉 You're All Set!

Your MCA platform is complete and ready to use. Whether you choose to test locally first or deploy directly to Railway, everything is configured and ready to go.

**Next Steps:**
1. Choose Option A (local) or Option B (Railway)
2. Follow the steps above
3. Test all features
4. Connect your domain
5. Start using your MCA platform!

---

## 💡 Pro Tips

- Test locally first to understand the workflow
- Change default passwords immediately
- Use strong SECRET_KEY in production
- Regular database backups
- Monitor Railway logs for issues

---

Made for QuickLine LLC 🚀
Ready to deploy and scale!
