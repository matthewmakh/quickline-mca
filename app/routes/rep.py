from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import LineOfCredit, User
from functools import wraps

bp = Blueprint('rep', __name__, url_prefix='/rep')


def rep_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'rep':
            flash('You need rep privileges to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@login_required
@rep_required
def dashboard():
    """Rep dashboard - shows only their assigned deals"""
    # Get all deals assigned to this rep
    assigned_deals = LineOfCredit.query.filter_by(rep_id=current_user.id).order_by(LineOfCredit.created_at.desc()).all()
    
    # Calculate statistics
    active_deals = [deal for deal in assigned_deals if deal.status == 'active']
    total_credit_managed = sum(deal.approved_amount for deal in active_deals)
    total_outstanding = sum(deal.outstanding_balance for deal in active_deals)
    
    return render_template('rep/dashboard.html',
                         assigned_deals=assigned_deals,
                         active_count=len(active_deals),
                         total_credit_managed=total_credit_managed,
                         total_outstanding=total_outstanding)


@bp.route('/deal/<int:id>')
@login_required
@rep_required
def view_deal(id):
    """View deal details (only if assigned to this rep)"""
    loc = LineOfCredit.query.get_or_404(id)
    
    # Ensure this deal is assigned to the current rep
    if loc.rep_id != current_user.id:
        flash('You do not have access to this deal.', 'error')
        return redirect(url_for('rep.dashboard'))
    
    return render_template('rep/view_deal.html', loc=loc)
