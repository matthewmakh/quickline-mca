from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import Customer, LineOfCredit, WithdrawalRequest, ActivityLog
from app.forms import WithdrawalRequestForm
from app import db
from app.utils import log_activity

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
    
    # Get payment history
    payment_logs = ActivityLog.query.filter_by(
        line_of_credit_id=loc.id,
        action_type='payment_recorded'
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return render_template('customer/dashboard.html',
                         customer=customer,
                         loc=loc,
                         utilization_percentage=utilization_percentage,
                         payment_logs=payment_logs)


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


@bp.route('/request-withdrawal', methods=['GET', 'POST'])
@customer_login_required
def request_withdrawal():
    """Customer requests withdrawal from line of credit"""
    customer_id = session.get('customer_id')
    customer = Customer.query.get_or_404(customer_id)
    loc = customer.line_of_credit
    
    if not loc or loc.status != 'active':
        flash('You do not have an active line of credit.', 'error')
        return redirect(url_for('customer.dashboard'))
    
    form = WithdrawalRequestForm()
    
    if form.validate_on_submit():
        requested_amount = form.requested_amount.data
        
        # Calculate available credit
        loc.calculate_available_amount()
        available_credit = loc.available_amount
        
        # Check if requested amount exceeds available credit
        if requested_amount > available_credit:
            flash(f'Requested amount ${requested_amount:,.2f} exceeds available credit ${available_credit:,.2f}', 'error')
            return render_template('customer/request_withdrawal.html', form=form, loc=loc, customer=customer)
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            line_of_credit_id=loc.id,
            customer_id=customer.id,
            requested_amount=requested_amount,
            purpose=form.purpose.data,
            status='pending'
        )
        
        db.session.add(withdrawal)
        db.session.commit()
        
        # Log activity
        log_activity(
            action_type='withdrawal_requested',
            description=f'Customer {customer.business_name} requested withdrawal of ${requested_amount:,.2f}',
            customer_id=customer.id,
            line_of_credit_id=loc.id
        )
        
        flash(f'Withdrawal request for ${requested_amount:,.2f} submitted successfully! Your rep will review it shortly.', 'success')
        return redirect(url_for('customer.dashboard'))
    
    # Calculate available credit for display
    loc.calculate_available_amount()
    
    return render_template('customer/request_withdrawal.html', form=form, loc=loc, customer=customer)
