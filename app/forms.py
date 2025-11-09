from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, IntegerField, SelectField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo


class ApplicationForm(FlaskForm):
    """Form for potential customers to apply for MCA"""
    # Business Information
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=200)])
    business_legal_name = StringField('Legal Business Name', validators=[Optional(), Length(max=200)])
    ein = StringField('EIN', validators=[Optional(), Length(max=20)])
    business_type = SelectField('Business Type', 
                               choices=[('', 'Select...'), ('LLC', 'LLC'), ('Corporation', 'Corporation'), 
                                       ('Sole Proprietorship', 'Sole Proprietorship'), ('Partnership', 'Partnership')],
                               validators=[DataRequired()])
    industry = StringField('Industry', validators=[DataRequired(), Length(max=100)])
    years_in_business = FloatField('Years in Business', validators=[DataRequired(), NumberRange(min=0)])
    
    business_address = StringField('Business Address', validators=[DataRequired(), Length(max=200)])
    business_city = StringField('City', validators=[DataRequired(), Length(max=100)])
    business_state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    business_zip = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    business_phone = StringField('Business Phone', validators=[DataRequired(), Length(max=20)])
    
    # Financial Information
    monthly_revenue = FloatField('Average Monthly Revenue', validators=[DataRequired(), NumberRange(min=0)])
    annual_revenue = FloatField('Annual Revenue', validators=[DataRequired(), NumberRange(min=0)])
    average_monthly_bank_balance = FloatField('Average Monthly Bank Balance', validators=[DataRequired(), NumberRange(min=0)])
    existing_debt = FloatField('Existing Debt', validators=[Optional(), NumberRange(min=0)])
    credit_score = IntegerField('Credit Score', validators=[Optional(), NumberRange(min=300, max=850)])
    requested_amount = FloatField('Requested Funding Amount', validators=[DataRequired(), NumberRange(min=0)])
    purpose_of_funding = TextAreaField('Purpose of Funding', validators=[DataRequired()])
    
    # Owner Information
    owner_first_name = StringField('Owner First Name', validators=[DataRequired(), Length(max=100)])
    owner_last_name = StringField('Owner Last Name', validators=[DataRequired(), Length(max=100)])
    owner_email = StringField('Owner Email', validators=[DataRequired(), Email(), Length(max=120)])
    owner_phone = StringField('Owner Phone', validators=[DataRequired(), Length(max=20)])
    owner_ssn_last_4 = StringField('Last 4 Digits of SSN', validators=[DataRequired(), Length(min=4, max=4)])
    owner_date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    owner_address = StringField('Owner Address', validators=[DataRequired(), Length(max=200)])
    owner_city = StringField('City', validators=[DataRequired(), Length(max=100)])
    owner_state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    owner_zip = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    ownership_percentage = FloatField('Ownership Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    
    # Banking Information
    bank_name = StringField('Bank Name', validators=[DataRequired(), Length(max=100)])
    bank_account_type = SelectField('Account Type', 
                                   choices=[('', 'Select...'), ('Checking', 'Checking'), ('Savings', 'Savings')],
                                   validators=[DataRequired()])
    time_with_bank = FloatField('Years with Bank', validators=[DataRequired(), NumberRange(min=0)])
    average_daily_balance = FloatField('Average Daily Balance', validators=[DataRequired(), NumberRange(min=0)])
    number_of_nsf_last_3_months = IntegerField('NSF Occurrences (Last 3 Months)', validators=[Optional(), NumberRange(min=0)], default=0)
    
    # Additional Information
    has_merchant_account = BooleanField('Do you have a merchant account?')
    monthly_card_sales = FloatField('Monthly Credit Card Sales', validators=[Optional(), NumberRange(min=0)])
    uses_online_sales = BooleanField('Do you sell online?')
    online_sales_percentage = FloatField('Online Sales Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    has_previous_mca = BooleanField('Have you had a previous MCA?')
    previous_mca_details = TextAreaField('Previous MCA Details', validators=[Optional()])
    
    submit = SubmitField('Submit Application')


class LoginForm(FlaskForm):
    """Login form for admins, reps, and customers"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CreateUserForm(FlaskForm):
    """Form for admin to create users (reps or other admins)"""
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('rep', 'Rep'), ('admin', 'Admin')], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Create User')


class LineOfCreditForm(FlaskForm):
    """Form for admin to create/edit line of credit"""
    approved_amount = FloatField('Approved Credit Line Amount', validators=[DataRequired(), NumberRange(min=0)])
    used_amount = FloatField('Amount Used/Drawn', validators=[DataRequired(), NumberRange(min=0)])
    interest_rate = FloatField('Interest Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    factor_rate = FloatField('Factor Rate (optional)', validators=[Optional(), NumberRange(min=1)])
    payment_frequency = SelectField('Payment Frequency', 
                                   choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')],
                                   validators=[DataRequired()])
    payment_amount = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    term_months = IntegerField('Term (months)', validators=[DataRequired(), NumberRange(min=1)])
    first_payment_date = DateField('First Payment Date', validators=[Optional()])
    maturity_date = DateField('Maturity Date', validators=[Optional()])
    status = SelectField('Status', 
                        choices=[('active', 'Active'), ('paid_off', 'Paid Off'), 
                                ('defaulted', 'Defaulted'), ('suspended', 'Suspended')],
                        validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Line of Credit')


class AssignRepForm(FlaskForm):
    """Form for admin to assign rep to a deal"""
    rep_id = SelectField('Assign to Rep', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Rep')


class CustomerPasswordForm(FlaskForm):
    """Form for creating customer login credentials"""
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Customer Login')
