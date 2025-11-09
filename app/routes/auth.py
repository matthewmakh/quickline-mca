from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm
from app.models import User, Customer
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login for admins and reps"""
    if current_user.is_authenticated:
        if hasattr(current_user, 'role'):
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('rep.dashboard'))
        else:
            return redirect(url_for('customer.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            next_page = request.args.get('next')
            
            if user.role == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('rep.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/customer-login', methods=['GET', 'POST'])
def customer_login():
    """Login for customers"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        
        if customer and customer.check_password(form.password.data):
            if not customer.is_active:
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('auth.customer_login'))
            
            # Update last login
            customer.last_login = db.func.now()
            db.session.commit()
            
            # Login customer (custom implementation needed)
            session['customer_id'] = customer.id
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/customer_login.html', form=form)


@bp.route('/logout')
def logout():
    """Logout"""
    logout_user()
    if 'customer_id' in session:
        session.pop('customer_id')
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
