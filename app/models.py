from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Admin and Rep users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'rep'
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    assigned_deals = db.relationship('LineOfCredit', backref='assigned_rep', lazy='dynamic',
                                    foreign_keys='LineOfCredit.rep_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Application(db.Model):
    """Initial customer applications for MCA"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Business Information
    business_name = db.Column(db.String(200), nullable=False)
    business_legal_name = db.Column(db.String(200))
    ein = db.Column(db.String(20))
    business_type = db.Column(db.String(50))  # LLC, Corporation, Sole Proprietorship, etc.
    industry = db.Column(db.String(100))
    years_in_business = db.Column(db.Float)
    business_address = db.Column(db.String(200))
    business_city = db.Column(db.String(100))
    business_state = db.Column(db.String(2))
    business_zip = db.Column(db.String(10))
    business_phone = db.Column(db.String(20))
    
    # Financial Information
    monthly_revenue = db.Column(db.Float)
    annual_revenue = db.Column(db.Float)
    average_monthly_bank_balance = db.Column(db.Float)
    existing_debt = db.Column(db.Float)
    credit_score = db.Column(db.Integer)
    requested_amount = db.Column(db.Float)
    purpose_of_funding = db.Column(db.Text)
    
    # Owner Information
    owner_first_name = db.Column(db.String(100))
    owner_last_name = db.Column(db.String(100))
    owner_email = db.Column(db.String(120), nullable=False, index=True)
    owner_phone = db.Column(db.String(20))
    owner_ssn_last_4 = db.Column(db.String(4))
    owner_date_of_birth = db.Column(db.Date)
    owner_address = db.Column(db.String(200))
    owner_city = db.Column(db.String(100))
    owner_state = db.Column(db.String(2))
    owner_zip = db.Column(db.String(10))
    ownership_percentage = db.Column(db.Float)
    
    # Banking Information
    bank_name = db.Column(db.String(100))
    bank_account_type = db.Column(db.String(50))  # Checking, Savings
    time_with_bank = db.Column(db.Float)  # years
    average_daily_balance = db.Column(db.Float)
    number_of_nsf_last_3_months = db.Column(db.Integer)  # Non-sufficient funds
    
    # Additional Information
    has_merchant_account = db.Column(db.Boolean, default=False)
    monthly_card_sales = db.Column(db.Float)
    uses_online_sales = db.Column(db.Boolean, default=False)
    online_sales_percentage = db.Column(db.Float)
    has_previous_mca = db.Column(db.Boolean, default=False)
    previous_mca_details = db.Column(db.Text)
    
    # Application Status
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reviewed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationship to customer (after approval)
    customer = db.relationship('Customer', backref='original_application', uselist=False)
    
    def __repr__(self):
        return f'<Application {self.business_name} - {self.status}>'


class Customer(db.Model):
    """Approved customers with login credentials"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), unique=True)
    
    # Login credentials
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    
    # Basic info (copied from application)
    business_name = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Relationship
    line_of_credit = db.relationship('LineOfCredit', backref='customer', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return f'customer_{self.id}'
    
    def __repr__(self):
        return f'<Customer {self.business_name}>'


class LineOfCredit(db.Model):
    """Line of credit details for approved customers"""
    __tablename__ = 'lines_of_credit'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True, nullable=False)
    rep_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Line of Credit Details
    approved_amount = db.Column(db.Float, nullable=False)  # Total credit line
    used_amount = db.Column(db.Float, default=0.0)  # Amount drawn
    available_amount = db.Column(db.Float)  # Calculated: approved - used
    
    # Terms
    interest_rate = db.Column(db.Float, nullable=False)  # Annual percentage rate
    factor_rate = db.Column(db.Float)  # Alternative to interest rate (e.g., 1.2)
    payment_frequency = db.Column(db.String(50))  # Daily, Weekly, Monthly
    payment_amount = db.Column(db.Float)  # Regular payment amount
    term_months = db.Column(db.Integer)  # Term length in months
    
    # Dates
    approved_date = db.Column(db.DateTime, default=datetime.utcnow)
    first_payment_date = db.Column(db.Date)
    maturity_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(50), default='active')  # active, paid_off, defaulted, suspended
    
    # Financial tracking
    total_paid = db.Column(db.Float, default=0.0)
    outstanding_balance = db.Column(db.Float, default=0.0)
    number_of_payments_made = db.Column(db.Integer, default=0)
    number_of_payments_remaining = db.Column(db.Integer)
    last_payment_date = db.Column(db.Date)
    next_payment_date = db.Column(db.Date)
    
    # Additional info
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_available_amount(self):
        """Calculate available credit"""
        self.available_amount = self.approved_amount - self.used_amount
        return self.available_amount
    
    def __repr__(self):
        return f'<LineOfCredit ${self.approved_amount} for Customer {self.customer_id}>'


class ActivityLog(db.Model):
    """Log all important activities on the platform"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)  # e.g., 'application_submitted', 'application_approved', 'password_changed', 'withdrawal_requested', 'withdrawal_approved'
    description = db.Column(db.Text, nullable=False)
    
    # Who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # If action was by admin/rep
    user = db.relationship('User', backref='activity_logs')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)  # If action was by customer
    customer = db.relationship('Customer', backref='activity_logs')
    
    # Related entities
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=True)
    line_of_credit_id = db.Column(db.Integer, db.ForeignKey('lines_of_credit.id'), nullable=True)
    
    # Additional data (JSON format)
    extra_data = db.Column(db.Text)  # Can store JSON data for extra details
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.action_type} at {self.created_at}>'


class WithdrawalRequest(db.Model):
    """Customer requests to withdraw from line of credit"""
    __tablename__ = 'withdrawal_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    line_of_credit_id = db.Column(db.Integer, db.ForeignKey('lines_of_credit.id'), nullable=False)
    line_of_credit = db.relationship('LineOfCredit', backref='withdrawal_requests')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref='withdrawal_requests')
    
    requested_amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, denied
    
    # Approval/Denial info
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_by = db.relationship('User', backref='reviewed_withdrawals')
    reviewed_at = db.Column(db.DateTime)
    denial_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<WithdrawalRequest ${self.requested_amount} - {self.status}>'
