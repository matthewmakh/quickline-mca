from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import ApplicationForm
from app.models import Application
from app import db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page with application form"""
    return render_template('index.html')


@bp.route('/apply', methods=['GET', 'POST'])
def apply():
    """Application form for potential clients"""
    form = ApplicationForm()
    
    if form.validate_on_submit():
        application = Application(
            # Business Information
            business_name=form.business_name.data,
            business_legal_name=form.business_legal_name.data,
            ein=form.ein.data,
            business_type=form.business_type.data,
            industry=form.industry.data,
            years_in_business=form.years_in_business.data,
            business_address=form.business_address.data,
            business_city=form.business_city.data,
            business_state=form.business_state.data,
            business_zip=form.business_zip.data,
            business_phone=form.business_phone.data,
            
            # Financial Information
            monthly_revenue=form.monthly_revenue.data,
            annual_revenue=form.annual_revenue.data,
            average_monthly_bank_balance=form.average_monthly_bank_balance.data,
            existing_debt=form.existing_debt.data,
            credit_score=form.credit_score.data,
            requested_amount=form.requested_amount.data,
            purpose_of_funding=form.purpose_of_funding.data,
            
            # Owner Information
            owner_first_name=form.owner_first_name.data,
            owner_last_name=form.owner_last_name.data,
            owner_email=form.owner_email.data,
            owner_phone=form.owner_phone.data,
            owner_ssn_last_4=form.owner_ssn_last_4.data,
            owner_date_of_birth=form.owner_date_of_birth.data,
            owner_address=form.owner_address.data,
            owner_city=form.owner_city.data,
            owner_state=form.owner_state.data,
            owner_zip=form.owner_zip.data,
            ownership_percentage=form.ownership_percentage.data,
            
            # Banking Information
            bank_name=form.bank_name.data,
            bank_account_type=form.bank_account_type.data,
            time_with_bank=form.time_with_bank.data,
            average_daily_balance=form.average_daily_balance.data,
            number_of_nsf_last_3_months=form.number_of_nsf_last_3_months.data,
            
            # Additional Information
            has_merchant_account=form.has_merchant_account.data,
            monthly_card_sales=form.monthly_card_sales.data,
            uses_online_sales=form.uses_online_sales.data,
            online_sales_percentage=form.online_sales_percentage.data,
            has_previous_mca=form.has_previous_mca.data,
            previous_mca_details=form.previous_mca_details.data,
            
            status='pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Your application has been submitted successfully! We will review it and contact you soon.', 'success')
        return redirect(url_for('main.thank_you'))
    
    return render_template('apply.html', form=form)


@bp.route('/thank-you')
def thank_you():
    """Thank you page after application submission"""
    return render_template('thank_you.html')
