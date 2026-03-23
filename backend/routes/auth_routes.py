"""
Authentication Routes

Handles user registration and login

Routes:
  GET  /auth/login          - Login page
  POST /auth/login          - Process login
  GET  /auth/signup         - Signup page
  POST /auth/signup         - Process signup
  GET  /auth/logout         - Logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from auth import login_user_session, logout_user_session, get_current_user

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and handler
    
    GET:  Show login form
    POST: Process login credentials
    """
    
    if request.method == 'GET':
        # Show login form
        return render_template('auth/login.html')
    
    # Handle POST request (form submission)
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    # Validate inputs
    if not email or not password:
        flash('Email and password are required', 'danger')
        return redirect(url_for('auth.login'))
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    # Verify password
    if not user or not user.check_password(password):
        flash('Invalid email or password', 'danger')
        return redirect(url_for('auth.login'))
    
    # Login successful - create session
    login_user_session(user)
    flash(f'Welcome back, {user.full_name}!', 'success')
    
    # Redirect to appropriate dashboard based on role
    if user.is_farmer():
        return redirect(url_for('farmer.dashboard'))
    elif user.is_driver():
        return redirect(url_for('driver.dashboard'))
    elif user.is_admin():
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User registration page and handler
    
    GET:  Show signup form
    POST: Create new user account
    """
    
    if request.method == 'GET':
        # Show signup form
        return render_template('auth/signup.html')
    
    # Handle POST request (form submission)
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    full_name = request.form.get('full_name', '').strip()
    phone_number = request.form.get('phone_number', '').strip()
    role = request.form.get('role', 'farmer')  # farmer or driver
    
    # Validation
    errors = []
    
    if not email:
        errors.append('Email is required')
    elif User.query.filter_by(email=email).first():
        errors.append('Email already registered')
    
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters')
    
    if password != confirm_password:
        errors.append('Passwords do not match')
    
    if not full_name:
        errors.append('Full name is required')
    
    if role not in ['farmer', 'driver']:
        errors.append('Invalid role selected')
    
    # If validation failed, show errors
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.signup'))
    
    # Create new user
    user = User(
        email=email,
        full_name=full_name,
        phone_number=phone_number,
        role=role
    )
    
    # Hash password
    user.set_password(password)
    
    # Save to database
    db.session.add(user)
    db.session.commit()
    
    flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """
    Logout current user and destroy session
    """
    current_user = get_current_user()
    if current_user:
        logout_user_session()
        flash('You have been logged out', 'info')
    
    return redirect(url_for('index'))