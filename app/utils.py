"""
Helper functions for activity logging
"""
from app import db
from app.models import ActivityLog
from flask_login import current_user
from flask import session
import json


def log_activity(action_type, description, user_id=None, customer_id=None, application_id=None, line_of_credit_id=None, metadata=None):
    """
    Log an activity to the database
    
    Args:
        action_type: Type of action (e.g., 'application_approved', 'password_changed')
        description: Human-readable description of the action
        user_id: ID of user who performed the action (admin/rep)
        customer_id: ID of customer related to the action
        application_id: ID of related application
        line_of_credit_id: ID of related line of credit
        metadata: Dict of additional data to store as JSON
    """
    # Auto-detect current user if not provided
    if user_id is None and hasattr(current_user, 'id') and current_user.is_authenticated:
        user_id = current_user.id
    
    # Auto-detect current customer if not provided
    if customer_id is None and 'customer_id' in session:
        customer_id = session.get('customer_id')
    
    # Convert metadata to JSON string if provided
    extra_data_str = json.dumps(metadata) if metadata else None
    
    log = ActivityLog(
        action_type=action_type,
        description=description,
        user_id=user_id,
        customer_id=customer_id,
        application_id=application_id,
        line_of_credit_id=line_of_credit_id,
        extra_data=extra_data_str
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log
