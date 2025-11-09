from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import Customer, LineOfCredit
from app import db

bp = Blueprint('customer', __name__, url_prefix='/customer')


def customer_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access your account.', 'error')
            return redirect(url_for('auth.customer_login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@customer_login_required
def dashboard():
    """Customer dashboard - shows their line of credit details"""
    customer_id = session.get('customer_id')
    customer = Customer.query.get_or_404(customer_id)
    
    # Get line of credit
    loc = customer.line_of_credit
    
    if not loc:
        flash('You do not have an active line of credit.', 'info')
        return render_template('customer/no_credit.html', customer=customer)
    
    # Calculate available credit
    loc.calculate_available_amount()
    
    # Calculate utilization percentage
    utilization_percentage = (loc.used_amount / loc.approved_amount * 100) if loc.approved_amount > 0 else 0
    
    return render_template('customer/dashboard.html',
                         customer=customer,
                         loc=loc,
                         utilization_percentage=utilization_percentage)


@bp.route('/details')
@customer_login_required
def details():
    """Detailed view of line of credit"""
    customer_id = session.get('customer_id')
    customer = Customer.query.get_or_404(customer_id)
    loc = customer.line_of_credit
    
    if not loc:
        flash('You do not have an active line of credit.', 'info')
        return redirect(url_for('customer.dashboard'))
    
    return render_template('customer/details.html', customer=customer, loc=loc)
