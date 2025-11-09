# QuickLine LLC - MCA Platform
## Project Summary & Features

---

## 🎯 Overview

A complete, production-ready web application for managing Merchant Cash Advance (MCA) lines of credit. Built with Flask and PostgreSQL, designed for Railway deployment with custom domain support (Hostinger).

---

## ✨ Key Features

### 1. Public Application System
- **Comprehensive Application Form** (30+ fields)
  - Business Information (name, EIN, type, industry, years in business)
  - Financial Details (monthly/annual revenue, bank balances, credit score, existing debt)
  - Owner Information (personal details, SSN last 4, ownership percentage)
  - Banking Information (bank details, account type, NSF history)
  - Additional MCA-specific fields (merchant account, online sales, previous MCAs)

### 2. Admin Dashboard
- **Application Management**
  - View all applications with filtering (pending/approved/rejected)
  - Detailed application review with all submitted information
  - One-click approve/reject functionality
  - Automatic customer account creation on approval

- **Customer Management**
  - View all customers
  - Create/delete customer accounts
  - Track customer status and creation dates

- **Line of Credit Management**
  - Create and configure lines of credit
  - Set approved amount, interest rates, payment terms
  - Track used vs available credit
  - Edit credit line details
  - Delete credit lines

- **Deal Assignment**
  - Assign deals to specific reps
  - Reassign or unassign deals
  - Track rep workload

- **User Management**
  - Create admin and rep accounts
  - Activate/deactivate users
  - Delete users
  - View user statistics

- **Dashboard Analytics**
  - Total applications count
  - Pending applications
  - Active deals count
  - Total credit issued
  - Application status breakdown
  - Rep performance metrics

### 3. Rep Dashboard
- **Restricted Access** - Reps see ONLY their assigned deals
- **Deal Overview**
  - Customer business names
  - Credit line details (approved, used, available)
  - Interest rates
  - Deal status
  
- **Performance Metrics**
  - Active deals count
  - Total credit managed
  - Outstanding balances

- **Deal Details**
  - Complete customer information
  - Line of credit specifics
  - Payment terms
  - Contact information

### 4. Customer Portal
- **Secure Login** - Dedicated authentication for customers
- **Credit Line Dashboard**
  - Visual display of approved, used, and available credit
  - Utilization percentage with color-coded progress bars
  - Real-time credit availability

- **Account Details**
  - Interest rate
  - Payment frequency and amount
  - Term length
  - Important dates (first payment, maturity)
  - Outstanding balance
  - Total amount paid
  - Payment history

- **Rep Contact**
  - Assigned representative information
  - Direct email link to rep

### 5. Security Features
- **Role-Based Access Control**
  - Admin: Full system access
  - Rep: Access only to assigned deals
  - Customer: Access only to their own account

- **Authentication**
  - Secure password hashing (Werkzeug)
  - Flask-Login session management
  - Separate login portals for staff and customers
  - CSRF protection on all forms

- **Data Protection**
  - Sensitive data (SSN) partially masked
  - Secure database connections
  - Environment variable configuration

---

## 🛠 Technical Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy 3.1
- **Migrations**: Flask-Migrate 4.0
- **Authentication**: Flask-Login 0.6
- **Forms**: WTForms 3.1 with validation

### Frontend
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons 1.11
- **Template Engine**: Jinja2
- **Responsive Design**: Mobile-first approach

### Deployment
- **Platform**: Railway
- **Web Server**: Gunicorn
- **Domain**: Custom domain support (Hostinger/any DNS)
- **SSL**: Automatic via Railway

---

## 📊 Database Schema

### Tables

1. **users** - Admin and Rep accounts
   - Role-based permissions
   - Secure password storage
   - Activity tracking

2. **applications** - Business funding applications
   - Complete business data capture
   - Financial information
   - Owner and banking details
   - Status tracking (pending/approved/rejected)

3. **customers** - Approved customer accounts
   - Login credentials
   - Business information
   - Links to original application

4. **lines_of_credit** - Credit line details
   - Approved vs used vs available amounts
   - Interest rates and terms
   - Payment schedules
   - Rep assignment
   - Status management

---

## 🚀 Deployment Options

### Railway (Recommended)
- One-click PostgreSQL provisioning
- Automatic SSL certificates
- Environment variable management
- Auto-restart on errors
- Built-in monitoring

### Custom Domain Setup (Hostinger)
- CNAME configuration for www subdomain
- A record for root domain
- Automatic SSL via Railway
- 24-48 hour DNS propagation

---

## 📁 Project Structure

```
QuickLineLLC/
├── app/
│   ├── __init__.py              # App factory
│   ├── models.py                # Database models
│   ├── forms.py                 # Form definitions
│   ├── routes/
│   │   ├── main.py              # Public routes
│   │   ├── auth.py              # Authentication
│   │   ├── admin.py             # Admin dashboard
│   │   ├── rep.py               # Rep dashboard
│   │   └── customer.py          # Customer portal
│   └── templates/
│       ├── base.html            # Base template
│       ├── index.html           # Homepage
│       ├── apply.html           # Application form
│       ├── auth/                # Login templates
│       ├── admin/               # Admin templates
│       ├── rep/                 # Rep templates
│       └── customer/            # Customer templates
├── config.py                    # Configuration
├── run.py                       # App entry point
├── setup.py                     # Setup script
├── init_db.py                   # Database init
├── generate_secret_key.py       # Secret key generator
├── requirements.txt             # Dependencies
├── Procfile                     # Railway config
├── railway.json                 # Railway settings
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick setup guide
├── DEPLOYMENT.md                # Deployment checklist
└── .env.example                 # Environment template
```

---

## 🎨 Design Features

- **Professional UI**: Modern gradient design with primary/secondary colors
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Role-specific menus and dashboards
- **Visual Feedback**: Color-coded status badges and progress bars
- **Card-Based Layout**: Clean, organized information presentation
- **Bootstrap Icons**: Professional iconography throughout

---

## 🔒 Security Best Practices

✅ Password hashing with Werkzeug
✅ CSRF protection on forms
✅ Role-based access control
✅ SQL injection prevention (SQLAlchemy ORM)
✅ Environment variable configuration
✅ Secure session management
✅ HTTPS in production (Railway)
✅ Sensitive data masking (SSN)

---

## 📈 Scalability

- **Database**: PostgreSQL handles high transaction volumes
- **Web Server**: Gunicorn with multiple workers
- **Cloud Platform**: Railway auto-scales based on traffic
- **Session Management**: Database-backed sessions
- **Caching**: Can add Redis for improved performance

---

## 🧪 Testing Workflow

1. **Submit Application** → Public form at `/apply`
2. **Admin Reviews** → Login at `/auth/login`
3. **Approve & Setup** → Create customer account + line of credit
4. **Assign to Rep** → Assign deal to representative
5. **Rep Manages** → Rep logs in and views their deals
6. **Customer Access** → Customer logs in at `/auth/customer-login`

---

## 📝 Future Enhancements (Optional)

- Email notifications (approval, payment reminders)
- Document upload (bank statements, tax returns)
- Payment processing integration
- Automated credit scoring
- Advanced analytics and reporting
- Multi-factor authentication
- API for third-party integrations
- Mobile app

---

## 📞 Support & Documentation

- **README.md** - Complete setup and deployment guide
- **QUICKSTART.md** - 5-minute local setup
- **DEPLOYMENT.md** - Railway deployment checklist
- **Code Comments** - Inline documentation throughout

---

## ✅ Production Ready

This application is ready to deploy to Railway and connect to your Hostinger domain. All security best practices are implemented, and the code is structured for maintainability and scalability.

**Total Development**: Complete full-stack MCA platform with admin, rep, and customer interfaces.

---

Made with ❤️ for QuickLine LLC
