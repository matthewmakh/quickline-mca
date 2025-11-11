from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import Application, User, Customer, LineOfCredit, ActivityLog, WithdrawalRequest
from app.forms import CreateUserForm, LineOfCreditForm, AssignRepForm, CustomerPasswordForm, ChangeCustomerPasswordForm, UpdateDealStatusForm, ApplicationForm, RecordPaymentForm
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
    
    # Check for duplicate applications from same email
    duplicate_applications = Application.query.filter(
        Application.owner_email == application.owner_email,
        Application.id != application.id
    ).all()
    
    # Check if customer already exists with this email
    existing_customer = Customer.query.filter_by(email=application.owner_email).first()
    
    return render_template('admin/view_application.html', 
                         application=application,
                         duplicate_applications=duplicate_applications,
                         existing_customer=existing_customer)


@bp.route('/application/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_application(id):
    """Approve application and create customer account"""
    application = Application.query.get_or_404(id)
    
    if application.status == 'approved':
        flash('This application is already approved.', 'warning')
        return redirect(url_for('admin.view_application', id=id))
    
    # Check if customer with this email already exists
    existing_customer = Customer.query.filter_by(email=application.owner_email).first()
    
    if existing_customer:
        # Customer already exists - mark application as approved and create another LOC
        application.status = 'approved'
        application.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Application approved! Customer account already exists for {application.owner_email}. '
              f'You can now create an additional line of credit for this customer.', 'info')
        return redirect(url_for('admin.create_line_of_credit', customer_id=existing_customer.id))
    
    # Update application status
    application.status = 'approved'
    application.reviewed_at = datetime.utcnow()
    
    # Generate a secure random password
    alphabet = string.ascii_letters + string.digits
    generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Create new customer account
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


@bp.route('/application/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_application(id):
    """Edit an existing application"""
    application = Application.query.get_or_404(id)
    form = ApplicationForm(obj=application)
    
    if form.validate_on_submit():
        # Update all application fields
        application.business_name = form.business_name.data
        application.business_legal_name = form.business_legal_name.data
        application.ein = form.ein.data
        application.business_type = form.business_type.data
        application.industry = form.industry.data
        application.years_in_business = form.years_in_business.data
        application.business_address = form.business_address.data
        application.business_city = form.business_city.data
        application.business_state = form.business_state.data
        application.business_zip = form.business_zip.data
        application.business_phone = form.business_phone.data
        
        application.monthly_revenue = form.monthly_revenue.data
        application.annual_revenue = form.annual_revenue.data
        application.average_monthly_bank_balance = form.average_monthly_bank_balance.data
        application.existing_debt = form.existing_debt.data
        application.credit_score = form.credit_score.data
        application.requested_amount = form.requested_amount.data
        application.purpose_of_funding = form.purpose_of_funding.data
        
        application.owner_first_name = form.owner_first_name.data
        application.owner_last_name = form.owner_last_name.data
        application.owner_email = form.owner_email.data
        application.owner_phone = form.owner_phone.data
        application.owner_ssn_last_4 = form.owner_ssn_last_4.data
        application.owner_date_of_birth = form.owner_date_of_birth.data
        application.owner_address = form.owner_address.data
        application.owner_city = form.owner_city.data
        application.owner_state = form.owner_state.data
        application.owner_zip = form.owner_zip.data
        application.ownership_percentage = form.ownership_percentage.data
        
        application.bank_name = form.bank_name.data
        application.bank_account_type = form.bank_account_type.data
        application.time_with_bank = form.time_with_bank.data
        application.average_daily_balance = form.average_daily_balance.data
        application.number_of_nsf_last_3_months = form.number_of_nsf_last_3_months.data
        
        application.has_merchant_account = form.has_merchant_account.data
        application.monthly_card_sales = form.monthly_card_sales.data
        application.uses_online_sales = form.uses_online_sales.data
        application.online_sales_percentage = form.online_sales_percentage.data
        application.has_previous_mca = form.has_previous_mca.data
        application.previous_mca_details = form.previous_mca_details.data
        
        db.session.commit()
        
        # Log activity
        log_activity(
            action_type='edit_application',
            description=f'Edited application for {application.business_name}',
            user_id=current_user.id,
            application_id=application.id
        )
        
        flash(f'Application for {application.business_name} updated successfully.', 'success')
        return redirect(url_for('admin.view_application', id=application.id))
    
    return render_template('admin/edit_application.html', form=form, application=application)


@bp.route('/application/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_application(id):
    """Delete an application"""
    application = Application.query.get_or_404(id)
    business_name = application.business_name
    app_id = application.id
    
    # Check if application is linked to a customer
    customer = Customer.query.filter_by(application_id=application.id).first()
    
    if customer:
        flash(f'Cannot delete application: It is linked to customer account "{customer.business_name}". '
              f'Delete the customer account first if needed.', 'error')
        return redirect(url_for('admin.view_application', id=id))
    
    try:
        # Delete related activity logs first
        ActivityLog.query.filter_by(application_id=application.id).delete()
        db.session.flush()
        
        # Delete the application
        db.session.delete(application)
        db.session.commit()
        
        # Log the deletion after successful commit (with no application_id since we deleted it)
        log_activity(
            action_type='delete_application',
            description=f'Deleted application #{app_id} for {business_name}',
            user_id=current_user.id
        )
        
        flash(f'Application for {business_name} has been deleted.', 'info')
        return redirect(url_for('admin.applications'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting application: {str(e)}', 'error')
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
    
    # Get payment history from activity logs
    payment_logs = ActivityLog.query.filter_by(
        line_of_credit_id=loc.id,
        action_type='payment_recorded'
    ).order_by(ActivityLog.created_at.desc()).all()
    
    # Calculate metrics
    from datetime import date, timedelta
    
    # Days since last payment
    days_since_payment = None
    if loc.last_payment_date:
        days_since_payment = (date.today() - loc.last_payment_date).days
    
    # Calculate expected number of payments
    expected_payments = 0
    if loc.first_payment_date and loc.payment_frequency:
        days_since_start = (date.today() - loc.first_payment_date).days
        if days_since_start >= 0:  # Only calculate if first payment date has passed
            if loc.payment_frequency == 'Daily':
                expected_payments = max(0, days_since_start)
            elif loc.payment_frequency == 'Weekly':
                expected_payments = max(0, days_since_start // 7)
            elif loc.payment_frequency == 'Monthly':
                expected_payments = max(0, days_since_start // 30)
    
    # Payment compliance - calculate how ahead or behind customer is
    payment_ahead_behind = loc.number_of_payments_made - expected_payments
    
    # Calculate total expected from used amount
    total_expected = loc.used_amount
    if loc.factor_rate:
        total_expected = loc.used_amount * loc.factor_rate
    elif loc.interest_rate and loc.term_months:
        # Simple interest calculation
        total_expected = loc.used_amount * (1 + (loc.interest_rate / 100) * (loc.term_months / 12))
    
    # Remaining balance percentage
    balance_percentage = (loc.outstanding_balance / total_expected * 100) if total_expected > 0 else 0
    
    return render_template('admin/view_deal.html', 
                         loc=loc, 
                         payment_logs=payment_logs,
                         days_since_payment=days_since_payment,
                         expected_payments=expected_payments,
                         payment_ahead_behind=payment_ahead_behind,
                         total_expected=total_expected,
                         balance_percentage=balance_percentage)


@bp.route('/deal/<int:id>/record-payment', methods=['GET', 'POST'])
@login_required
@admin_required
def record_payment(id):
    """Record a payment made by customer"""
    loc = LineOfCredit.query.get_or_404(id)
    form = RecordPaymentForm()
    
    if form.validate_on_submit():
        payment_amount = form.payment_amount.data
        payment_date = form.payment_date.data
        payment_method = form.payment_method.data
        notes = form.notes.data or ''
        
        # Ensure outstanding_balance is set
        if loc.outstanding_balance is None:
            loc.outstanding_balance = 0.0
        
        # Validate payment amount doesn't exceed outstanding balance
        if loc.outstanding_balance > 0 and payment_amount > loc.outstanding_balance:
            flash(f'Payment amount ${payment_amount:,.2f} exceeds outstanding balance ${loc.outstanding_balance:,.2f}', 'error')
            return render_template('admin/record_payment.html', form=form, loc=loc)
        
        # Update line of credit financials
        loc.total_paid += payment_amount
        loc.outstanding_balance -= payment_amount
        loc.number_of_payments_made += 1
        loc.last_payment_date = payment_date
        loc.updated_at = datetime.utcnow()
        
        # Check if fully paid off
        if loc.outstanding_balance <= 0:
            loc.outstanding_balance = 0
            loc.status = 'paid_off'
            flash(f'🎉 Line of credit fully paid off!', 'success')
        
        db.session.commit()
        
        # Log activity with detailed payment info
        log_activity(
            action_type='payment_recorded',
            description=f'Payment of ${payment_amount:,.2f} recorded via {payment_method} on {payment_date.strftime("%m/%d/%Y")} by {current_user.username}. {notes}',
            user_id=current_user.id,
            customer_id=loc.customer_id,
            line_of_credit_id=loc.id,
            metadata={"amount": payment_amount, "method": payment_method, "date": payment_date.isoformat()}
        )
        
        flash(f'Payment of ${payment_amount:,.2f} recorded successfully!', 'success')
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    return render_template('admin/record_payment.html', form=form, loc=loc)


@bp.route('/deal/<int:id>/mark-paid-off', methods=['POST'])
@login_required
@admin_required
def mark_paid_off(id):
    """Mark a deal as paid off"""
    loc = LineOfCredit.query.get_or_404(id)
    
    if loc.status == 'paid_off':
        flash('This deal is already marked as paid off.', 'info')
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    loc.status = 'paid_off'
    loc.outstanding_balance = 0
    loc.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log activity
    log_activity(
        action_type='deal_paid_off',
        description=f'Deal #{loc.id} marked as paid off by {current_user.username}',
        user_id=current_user.id,
        customer_id=loc.customer_id,
        line_of_credit_id=loc.id
    )
    
    flash(f'🎉 Deal marked as paid off!', 'success')
    return redirect(url_for('admin.view_deal', id=loc.id))


@bp.route('/customer/<int:customer_id>/create-line-of-credit', methods=['GET', 'POST'])
@login_required
@admin_required
def create_line_of_credit(customer_id):
    """Create line of credit for approved customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Customer can now have multiple LOCs, so no need to check for existing
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
    """Delete a line of credit and associated customer"""
    loc = LineOfCredit.query.get_or_404(id)
    customer = loc.customer
    customer_name = customer.business_name
    customer_id = customer.id
    
    # Log the action before deletion
    log_activity(
        action_type='delete_deal',
        description=f'Deleted line of credit for {customer_name}',
        user_id=current_user.id,
        line_of_credit_id=loc.id
    )
    
    # First delete the line of credit
    db.session.delete(loc)
    db.session.flush()  # Flush to database but don't commit yet
    
    # Then delete activity logs related to this customer
    ActivityLog.query.filter_by(customer_id=customer_id).delete()
    
    # Finally delete the customer
    db.session.delete(customer)
    db.session.commit()
    
    flash(f'Line of credit and customer account for {customer_name} have been deleted.', 'info')
    return redirect(url_for('admin.deals'))


@bp.route('/deal/<int:id>/update-status', methods=['GET', 'POST'])
@login_required
@admin_required
def update_deal_status(id):
    """Update the status of a line of credit"""
    loc = LineOfCredit.query.get_or_404(id)
    form = UpdateDealStatusForm()
    
    if form.validate_on_submit():
        old_status = loc.status
        loc.status = form.status.data
        
        # Log the status change
        log_activity(
            action_type='update_deal_status',
            description=f'Changed status from {old_status} to {loc.status}. Notes: {form.notes.data or "None"}',
            user_id=current_user.id,
            line_of_credit_id=loc.id
        )
        
        db.session.commit()
        flash(f'Deal status updated to {loc.status}.', 'success')
        return redirect(url_for('admin.view_deal', id=loc.id))
    
    # Pre-populate with current status
    form.status.data = loc.status
    
    return render_template('admin/update_deal_status.html', form=form, loc=loc)


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
    
    try:
        # Get the line of credit for this customer (if exists)
        loc = customer.line_of_credit
        
        # Delete in correct order to avoid foreign key constraints
        # 1. Delete withdrawal requests
        if loc:
            WithdrawalRequest.query.filter_by(line_of_credit_id=loc.id).delete()
        WithdrawalRequest.query.filter_by(customer_id=customer.id).delete()
        
        # 2. Delete activity logs
        ActivityLog.query.filter_by(customer_id=customer.id).delete()
        if loc:
            ActivityLog.query.filter_by(line_of_credit_id=loc.id).delete()
        
        # 3. Delete the line of credit itself (must be before customer)
        if loc:
            db.session.delete(loc)
        
        # 4. Finally delete the customer
        db.session.delete(customer)
        db.session.commit()
        
        flash(f'Customer {business_name} and all related data have been deleted.', 'info')
        return redirect(url_for('admin.customers'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customer: {str(e)}', 'error')
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


@bp.route('/reports')
@login_required
@admin_required
def reports():
    """Financial summary reports"""
    from datetime import date, timedelta
    from sqlalchemy import func
    
    # Get all active lines of credit
    active_locs = LineOfCredit.query.filter_by(status='active').all()
    
    # Calculate totals
    total_outstanding = sum(loc.outstanding_balance for loc in active_locs)
    total_credit_issued = sum(loc.approved_amount for loc in active_locs)
    total_credit_used = sum(loc.used_amount for loc in active_locs)
    total_collected = db.session.query(func.sum(LineOfCredit.total_paid)).scalar() or 0
    
    # Calculate averages
    all_locs = LineOfCredit.query.all()
    avg_deal_size = (sum(loc.approved_amount for loc in all_locs) / len(all_locs)) if all_locs else 0
    
    # Get payment activity
    payment_logs = ActivityLog.query.filter_by(action_type='payment_recorded').all()
    payment_amounts = [float(log.extra_data.split('"amount": ')[1].split(',')[0]) 
                      for log in payment_logs if '"amount":' in log.extra_data]
    avg_payment = (sum(payment_amounts) / len(payment_amounts)) if payment_amounts else 0
    
    # This month's collections
    first_day_of_month = date.today().replace(day=1)
    monthly_payments = ActivityLog.query.filter(
        ActivityLog.action_type == 'payment_recorded',
        ActivityLog.created_at >= first_day_of_month
    ).all()
    this_month_collected = sum(float(log.extra_data.split('"amount": ')[1].split(',')[0]) 
                               for log in monthly_payments if '"amount":' in log.extra_data)
    
    # This year's collections
    first_day_of_year = date.today().replace(month=1, day=1)
    yearly_payments = ActivityLog.query.filter(
        ActivityLog.action_type == 'payment_recorded',
        ActivityLog.created_at >= first_day_of_year
    ).all()
    this_year_collected = sum(float(log.extra_data.split('"amount": ')[1].split(',')[0]) 
                              for log in yearly_payments if '"amount":' in log.extra_data)
    
    # Deal status breakdown
    status_counts = {
        'active': LineOfCredit.query.filter_by(status='active').count(),
        'paid_off': LineOfCredit.query.filter_by(status='paid_off').count(),
        'defaulted': LineOfCredit.query.filter_by(status='defaulted').count(),
        'suspended': LineOfCredit.query.filter_by(status='suspended').count()
    }
    
    # Top customers by outstanding balance
    top_customers = sorted(active_locs, key=lambda x: x.outstanding_balance, reverse=True)[:10]
    
    # Recent payments
    recent_payments = ActivityLog.query.filter_by(
        action_type='payment_recorded'
    ).order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    return render_template('admin/reports.html',
                         total_outstanding=total_outstanding,
                         total_credit_issued=total_credit_issued,
                         total_credit_used=total_credit_used,
                         total_collected=total_collected,
                         avg_deal_size=avg_deal_size,
                         avg_payment=avg_payment,
                         this_month_collected=this_month_collected,
                         this_year_collected=this_year_collected,
                         status_counts=status_counts,
                         top_customers=top_customers,
                         recent_payments=recent_payments,
                         active_deals_count=len(active_locs),
                         total_deals_count=len(all_locs))
