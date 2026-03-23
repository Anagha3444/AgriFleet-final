"""
Authentication utilities

Functions for:
- User login/logout
- Session management
- Password handling
- Access control decorators
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from models import User


def login_user_session(user):
    """
    Create a session for logged-in user
    
    Args:
        user: User object from database
    """
    session['user_id'] = user.id
    session['email'] = user.email
    session['role'] = user.role
    session.permanent = True


def logout_user_session():
    """
    Destroy user session
    """
    session.clear()


def get_current_user():
    """
    Get currently logged-in user
    
    Returns:
        User: User object if logged in, None otherwise
    """
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def is_logged_in():
    """
    Check if a user is currently logged in
    
    Returns:
        bool: True if logged in, False otherwise
    """
    return 'user_id' in session


# ==================== Decorators ====================

def login_required(f):
    """
    Decorator to protect routes from unauthenticated users
    
    If user is not logged in, redirect to login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def farmer_required(f):
    """
    Decorator to protect routes for farmer-only access
    
    Only users with role='farmer' can access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        
        user = get_current_user()
        if not user or not user.is_farmer():
            flash('Only farmers can access this page', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def driver_required(f):
    """
    Decorator to protect routes for driver-only access
    
    Only users with role='driver' can access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        
        user = get_current_user()
        if not user or not user.is_driver():
            flash('Only drivers can access this page', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to protect routes for admin-only access
    
    Only users with role='admin' can access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        
        user = get_current_user()
        if not user or not user.is_admin():
            flash('Only admins can access this page', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function