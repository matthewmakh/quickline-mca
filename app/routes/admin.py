from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import Application, User, Customer, LineOfCredit, ActivityLog, WithdrawalRequest
from app.forms import CreateUserForm, LineOfCreditForm, AssignRepForm, CustomerPasswordForm, ChangeCustomerPasswordForm
from app import db
from datetime import datetime
from functools import wraps
import secrets
import string
from app.utils import log_activity

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard - overview of applications and deals"""
    pending_applications = Application.query.filter_by(status='pending').order_by(Application.submitted_at.desc()).all()
    approved_applications = Application.query.filter_by(status='approved').order_by(Application.reviewed_at.desc()).limit(10).all()
    
    total_applications = Application.query.count()
    pending_count = Application.query.filter_by(status='pending').count()
    approved_count = Application.query.filter_by(status='approved').count()
    rejected_count = Application.query.filter_by(status='rejected').count()
    
    active_deals = LineOfCredit.query.filter_by(status='active').count()
    total_credit_issued = db.session.query(db.func.sum(LineOfCredit.approved_amount)).filter_by(status='active').scalar() or 0
    
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    
    reps = User.query.filter_by(role='rep', is_active=True).all()
    
    return render_template('admin/dashboard.html',
                         pending_applications=pending_applications,
                         approved_applications=approved_applications,
                         total_applications=total_applications,
                         pending_count=pending_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count,
                         active_deals=active_deals,
                         total_credit_issued=total_credit_issued,
                         pending_withdrawals=pending_withdrawals,
                         reps=reps)


@bp.route('/applications')
@login_required
@admin_required
def applications():
    """View all applications"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        applications = Application.query.order_by(Application.submitted_at.desc()).all()
    else:
        applications = Application.query.filter_by(status=status_filter).order_by(Application.submitted_at.desc()).all()
    
    return render_template('admin/applications.html', applications=applications, status_filter=status_filter)


@bp.route('/application/<int:id>')
@login_required
@admin_required
def view_application(id):
    """View detailed application"""
    application = Application.query.get_or_404(id)
    return render_template('admin/view_application.html', application=application)


@bp.route('/application/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_application(id):
    """Approve application and create customer account"""
    application = Application.query.get_or_404(id)
    
    if application.status == 'approved':
        flash('This application is already approved.', 'warning')
        return redirect(url_for('admin.view_application', id=id))
    
    # Update application status
    application.status = 'approved'
    application.reviewed_at = datetime.utcnow()
    
    # Generate a secure random password
    alphabet = string.ascii_letters + string.digits
    generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Create customer account
    customer = Customer(
        application_id=application.id,
        email=application.owner_email,
        business_name=application.business_name,
        owner_name=f"{application.owner_first_name} {application.owner_last_name}",
        phone=application.business_phone
    )
    
    # Set the generated password
    customer.set_password(generated_password)
    
    db.session.add(customer)
    db.session.commit()
    
    # Log activity
    log_activity(
        action_type='application_approved',
        description=f'Application #{application.id} for {application.business_name} approved by {current_user.username}',
        application_id=application.id,
        customer_id=customer.id
    )
    
    # Store password in session to show on next page
    session['new_customer_password'] = generated_password
    session['new_customer_email'] = application.owner_email
    session['new_customer_business'] = application.business_name
    
    flash(f'Application approved! Customer account created for {application.business_name}.', 'success')
    return redirect(url_for('admin.create_line_of_credit', customer_id=customer.id))


@bp.route('/application/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_application(id):
    """Reject application"""
    application = Application.query.get_or_404(id)
    
    application.status = 'rejected'
    application.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Application for {application.business_name} has been rejected.', 'info')
    return redirect(url_for('admin.applications'))


@bp.route('/deals')
@login_required
@admin_required
def deals():
    """View all deals (lines of credit)"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        lines_of_credit = LineOfCredit.query.order_by(LineOfCredit.created_at.desc()).all()
    else:
        lines_of_credit = LineOfCredit.query.filter_by(status=status_filter).order_by(LineOfCredit.created_at.desc()).all()
    
    return render_template('admin/deals.html', lines_of_credit=lines_of_credit, status_filter=status_filter)


@bp.route('/deal/<int:id>')
@login_required
@admin_required
def view_deal(id):
    """View deal details"""
    loc = LineOfCredit.query.get_or_404(id)
    return render_template('admin/view_deal.html', loc=loc)


@bp.route('/customer/<int:customer_id>/create-line-of-credit', methods=['GET', 'POST'])
@login_required
@admin_required
def create_line_of_credit(customer_id):
    """Create line of credit for approved customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    if customer.line_of_credit:
        flash('This customer already has a line of credit.', 'warning')
        return redirect(url_for('admin.edit_line_of_credit', id=customer.line_of_credit.id))
    
    form = LineOfCreditForm()
    
    if form.validate_on_submit():
        loc = LineOfCredit(
            customer_id=customer.id,
            approved_amount=form.approved_amount.data,
            used_amount=form.used_amount.data,
            interest_rate=form.interest_rate.data,
            factor_rate=form.factor_rate.data,
            payment_frequency=form.payment_frequency.data,
            payment_amount=form.payment_amount.data,
            term_months=form.term_months.data,
            first_payment_date=form.first_payment_date.data,
            maturity_date=form.maturity_date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        
        loc.calculate_available_amount()
        loc.outstanding_balance = loc.used_amount
        
        db.session.add(loc)
        db.session.commit()
        
        flash(f'Line of credit created for {customer.business_name}!', 'success')
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    return render_template('admin/create_line_of_credit.html', form=form, customer=customer)


@bp.route('/deal/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_line_of_credit(id):
    """Edit line of credit"""
    loc = LineOfCredit.query.get_or_404(id)
    form = LineOfCreditForm(obj=loc)
    
    if form.validate_on_submit():
        loc.approved_amount = form.approved_amount.data
        loc.used_amount = form.used_amount.data
        loc.interest_rate = form.interest_rate.data
        loc.factor_rate = form.factor_rate.data
        loc.payment_frequency = form.payment_frequency.data
        loc.payment_amount = form.payment_amount.data
        loc.term_months = form.term_months.data
        loc.first_payment_date = form.first_payment_date.data
        loc.maturity_date = form.maturity_date.data
        loc.status = form.status.data
        loc.notes = form.notes.data
        
        loc.calculate_available_amount()
        loc.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Line of credit updated successfully!', 'success')
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    return render_template('admin/edit_line_of_credit.html', form=form, loc=loc)


@bp.route('/deal/<int:id>/assign-rep', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_rep(id):
    """Assign a rep to a deal"""
    loc = LineOfCredit.query.get_or_404(id)
    form = AssignRepForm()
    
    # Populate rep choices
    reps = User.query.filter_by(role='rep', is_active=True).all()
    form.rep_id.choices = [(0, 'Unassigned')] + [(rep.id, f"{rep.first_name} {rep.last_name} ({rep.username})") for rep in reps]
    
    if form.validate_on_submit():
        if form.rep_id.data == 0:
            loc.rep_id = None
            flash('Rep unassigned from deal.', 'info')
        else:
            loc.rep_id = form.rep_id.data
            rep = User.query.get(form.rep_id.data)
            flash(f'Deal assigned to {rep.first_name} {rep.last_name}!', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    # Pre-select current rep
    if loc.rep_id:
        form.rep_id.data = loc.rep_id
    
    return render_template('admin/assign_rep.html', form=form, loc=loc)


@bp.route('/deal/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_deal(id):
    """Delete a line of credit"""
    loc = LineOfCredit.query.get_or_404(id)
    customer_name = loc.customer.business_name
    
    db.session.delete(loc)
    db.session.commit()
    
    flash(f'Line of credit for {customer_name} has been deleted.', 'info')
    return redirect(url_for('admin.deals'))


@bp.route('/users')
@login_required
@admin_required
def users():
    """View all users (admins and reps)"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user (admin or rep)"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('admin/create_user.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'error')
            return render_template('admin/create_user.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)


@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Delete a user"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted.', 'info')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(id):
    """Activate/deactivate a user"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'info')
    return redirect(url_for('admin.users'))


@bp.route('/customers')
@login_required
@admin_required
def customers():
    """View all customers"""
    all_customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('admin/customers.html', customers=all_customers)


@bp.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_customer(id):
    """Delete a customer (and their line of credit)"""
    customer = Customer.query.get_or_404(id)
    business_name = customer.business_name
    
    db.session.delete(customer)
    db.session.commit()
    
    flash(f'Customer {business_name} has been deleted.', 'info')
    return redirect(url_for('admin.customers'))


@bp.route('/customers/<int:id>/password', methods=['GET', 'POST'])
@login_required
@admin_required
def view_customer_password(id):
    """View and change customer password"""
    customer = Customer.query.get_or_404(id)
    form = ChangeCustomerPasswordForm()
    
    # Generate a new random password if requested
    generated_password = None
    if request.args.get('generate') == 'true':
        alphabet = string.ascii_letters + string.digits
        generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
        flash(f'New password generated: {generated_password}', 'info')
    
    if form.validate_on_submit():
        customer.set_password(form.new_password.data)
        db.session.commit()
        
        # Log activity
        log_activity(
            action_type='password_changed',
            description=f'Password changed for customer {customer.business_name} by {current_user.username}',
            customer_id=customer.id
        )
        
        flash(f'Password changed successfully for {customer.business_name}!', 'success')
        return redirect(url_for('admin.customers'))
    
    return render_template('admin/customer_password.html', customer=customer, form=form, generated_password=generated_password)


@bp.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    """View all activity logs"""
    page = request.args.get('page', 1, type=int)
    action_type_filter = request.args.get('type', 'all')
    
    query = ActivityLog.query
    
    if action_type_filter != 'all':
        query = query.filter_by(action_type=action_type_filter)
    
    logs = query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    
    # Get unique action types for filter
    action_types = db.session.query(ActivityLog.action_type).distinct().all()
    action_types = [at[0] for at in action_types]
    
    return render_template('admin/activity_logs.html', logs=logs, action_types=action_types, action_type_filter=action_type_filter)


@bp.route('/withdrawal-requests')
@login_required
@admin_required
def withdrawal_requests():
    """View all pending withdrawal requests"""
    status_filter = request.args.get('status', 'pending')
    
    query = WithdrawalRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(WithdrawalRequest.created_at.desc()).all()
    
    return render_template('admin/withdrawal_requests.html', requests=requests, status_filter=status_filter)


@bp.route('/withdrawal-request/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_withdrawal(id):
    """Approve withdrawal request"""
    withdrawal = WithdrawalRequest.query.get_or_404(id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal request has already been processed.', 'warning')
        return redirect(url_for('admin.withdrawal_requests'))
    
    # Update line of credit used amount
    loc = withdrawal.line_of_credit
    loc.used_amount += withdrawal.requested_amount
    loc.calculate_available_amount()
    
    # Update withdrawal request
    withdrawal.status = 'approved'
    withdrawal.reviewed_by_id = current_user.id
    withdrawal.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log activity
    log_activity(
        action_type='withdrawal_approved',
        description=f'Withdrawal request #{withdrawal.id} for ${withdrawal.requested_amount:,.2f} approved by {current_user.username}',
        customer_id=withdrawal.customer_id,
        line_of_credit_id=withdrawal.line_of_credit_id
    )
    
    flash(f'Withdrawal request for ${withdrawal.requested_amount:,.2f} approved! Customer has been notified.', 'success')
    return redirect(url_for('admin.withdrawal_requests'))


@bp.route('/withdrawal-request/<int:id>/deny', methods=['POST'])
@login_required
@admin_required
def deny_withdrawal(id):
    """Deny withdrawal request"""
    withdrawal = WithdrawalRequest.query.get_or_404(id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal request has already been processed.', 'warning')
        return redirect(url_for('admin.withdrawal_requests'))
    
    reason = request.form.get('reason', 'No reason provided')
    
    withdrawal.status = 'denied'
    withdrawal.reviewed_by_id = current_user.id
    withdrawal.reviewed_at = datetime.utcnow()
    withdrawal.denial_reason = reason
    
    db.session.commit()
    
    # Log activity
    log_activity(
        action_type='withdrawal_denied',
        description=f'Withdrawal request #{withdrawal.id} for ${withdrawal.requested_amount:,.2f} denied by {current_user.username}. Reason: {reason}',
        customer_id=withdrawal.customer_id,
        line_of_credit_id=withdrawal.line_of_credit_id
    )
    
    flash(f'Withdrawal request denied.', 'info')
    return redirect(url_for('admin.withdrawal_requests'))
