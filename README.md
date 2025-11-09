# QuickLine LLC - MCA Business Funding Platform

A comprehensive web application for managing Merchant Cash Advance (MCA) lines of credit, built with Flask and PostgreSQL. This platform allows businesses to apply for funding, and provides admin and rep dashboards for managing applications and customer accounts.

## Features

### Public Features
- **Business Funding Application Form**: Comprehensive form capturing business information, financials, owner details, and banking information
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Professional UI**: Modern gradient design with intuitive navigation

### Admin Features
- **Application Management**: Review, approve, or reject funding applications
- **Customer Management**: Create and manage customer accounts
- **Line of Credit Management**: Set up and configure credit lines with customizable terms
- **Rep Assignment**: Assign deals to specific reps
- **User Management**: Create admin and rep accounts, activate/deactivate users
- **Comprehensive Dashboard**: Overview of applications, deals, and team performance

### Rep Features
- **Deal Dashboard**: View only deals assigned to them
- **Customer Details**: Access complete line of credit information for assigned customers
- **Performance Metrics**: Track total credit managed and outstanding balances

### Customer Portal
- **Secure Login**: Dedicated customer authentication
- **Credit Line Overview**: Real-time view of approved, used, and available credit
- **Utilization Tracking**: Visual progress bars showing credit usage
- **Payment Information**: View payment schedules and account status
- **Rep Contact**: Direct access to assigned representative information

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Forms**: WTForms with validation
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Deployment**: Railway (with custom domain support)

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Local Development Setup

1. **Clone the repository**
```bash
cd /path/to/your/project
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and configure:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/mca_db
FLASK_ENV=development
```

5. **Create PostgreSQL database**
```bash
createdb mca_db
```

6. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. **Create admin user (Python shell)**
```bash
python3 -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@quickline.com',
        role='admin',
        first_name='Admin',
        last_name='User'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
"
```

8. **Run the application**
```bash
python run.py
```

Visit `http://localhost:5000`

## Railway Deployment

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository (optional but recommended)
- Hostinger domain (or any DNS provider)

### Deployment Steps

1. **Create new project on Railway**
   - Go to Railway.app and create a new project
   - Add PostgreSQL database service
   - Add web service from your repository

2. **Configure environment variables**
   In Railway dashboard, add:
   ```
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://... (auto-provided by Railway)
   FLASK_ENV=production
   ```

3. **Deploy**
   - Railway will automatically detect the `Procfile` and `railway.json`
   - The app will build and deploy automatically

4. **Run database migrations**
   In Railway terminal:
   ```bash
   flask db upgrade
   ```

5. **Create admin user**
   In Railway terminal:
   ```bash
   python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); admin = User(username='admin', email='admin@quickline.com', role='admin', first_name='Admin', last_name='User'); admin.set_password('your-secure-password'); db.session.add(admin); db.session.commit(); print('Admin created!')"
   ```

### Custom Domain Setup (Hostinger)

1. **Get Railway domain**
   - In Railway project settings, copy your app URL (e.g., `yourapp.up.railway.app`)

2. **Configure DNS in Hostinger**
   - Log in to Hostinger
   - Go to Domains → Manage → DNS/Name Servers
   - Add these records:

   **For root domain (example.com):**
   ```
   Type: A
   Name: @
   Points to: [Railway IP - check Railway docs for current IP]
   TTL: 14400
   ```

   **For subdomain (www.example.com):**
   ```
   Type: CNAME
   Name: www
   Points to: yourapp.up.railway.app
   TTL: 14400
   ```

3. **Configure custom domain in Railway**
   - Go to Railway project settings
   - Click "Add Domain"
   - Enter your custom domain (e.g., `www.example.com`)
   - Railway will provide specific DNS configuration

4. **SSL Certificate**
   - Railway automatically provides SSL certificates
   - Wait 24-48 hours for DNS propagation

## Default Login Credentials

After setup, use these credentials:

**Admin Login** (`/auth/login`):
- Email: `admin@quickline.com`
- Password: `admin123` (change immediately!)

**Create Test Customer**:
1. Submit an application at `/apply`
2. Login as admin and approve the application
3. Create line of credit for the customer
4. Customer can login at `/auth/customer-login` with their email and temp password

## Database Models

### User
- Admins and Reps
- Role-based access control
- Secure password hashing

### Application
- Complete business application data
- Financial information
- Owner and banking details
- Application status tracking

### Customer
- Approved customer accounts
- Login credentials
- Links to original application

### LineOfCredit
- Credit line details (approved, used, available)
- Interest rates and payment terms
- Rep assignment
- Status tracking (active, paid_off, defaulted, suspended)

## Project Structure

```
QuickLineLLC/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── routes/              # Route blueprints
│   │   ├── main.py          # Public routes
│   │   ├── auth.py          # Authentication
│   │   ├── admin.py         # Admin dashboard
│   │   ├── rep.py           # Rep dashboard
│   │   └── customer.py      # Customer portal
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── apply.html
│       ├── auth/
│       ├── admin/
│       ├── rep/
│       └── customer/
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment
├── railway.json             # Railway configuration
└── README.md
```

## Security Notes

- Change default admin password immediately
- Use strong SECRET_KEY in production
- Keep DATABASE_URL secure
- Enable HTTPS in production (Railway provides this automatically)
- Regular security updates for dependencies

## Support

For issues or questions:
- Check Railway deployment logs
- Verify database connection
- Ensure all environment variables are set correctly

## License

Proprietary - QuickLine LLC

## Version

1.0.0 - Initial Release
