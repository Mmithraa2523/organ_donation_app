from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from models import User, Role, OTPVerification
from forms import LoginForm, RegistrationForm, OTPVerificationForm
from werkzeug.security import check_password_hash, generate_password_hash
from utils import save_otp, send_otp_email, verify_otp
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_verified and user.get_role() == 'user':
                session['user_id'] = user.id
                flash('Please verify your account first.', 'warning')
                return redirect(url_for('auth.verify_account'))
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            flash(f'Welcome, {user.username}!', 'success')
            
            if user.get_role() == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.get_role() == 'doctor':
                return redirect(next_page or url_for('doctor.dashboard'))
            else:
                return redirect(next_page or url_for('user.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get the user role
        user_role = Role.query.filter_by(name='user').first()
        
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            phone=form.phone.data,
            address=form.address.data,
            role_id=user_role.id,
            is_verified=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate and send OTP
        otp = save_otp(user, 'registration')
        send_result = send_otp_email(user, otp, 'registration')
        
        # Store user ID in session for OTP verification
        session['user_id'] = user.id
        session['debug_otp'] = otp  # Store OTP in session for testing purposes
        
        # Store email sending result in session
        session['email_sent_success'] = send_result
        
        if send_result:
            flash('Your account has been created! Please verify your email with the OTP we just sent.', 'success')
        else:
            flash('Your account has been created but we could not send the verification email. Please use the resend option.', 'warning')
        
        return redirect(url_for('auth.verify_account'))
    
    return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify_account():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if 'user_id' not in session:
        flash('Please register or login first.', 'warning')
        return redirect(url_for('auth.login'))
    
    form = OTPVerificationForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        otp = form.otp.data
        
        if verify_otp(user_id, otp, 'registration'):
            # Update user verification status
            user = User.query.get(user_id)
            user.is_verified = True
            db.session.commit()
            
            # Clear session data
            session.pop('user_id', None)
            
            flash('Your account has been verified! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired OTP. Please try again or request a new one.', 'danger')
    
    return render_template('auth/verify_otp.html', form=form, title='Verify Account', purpose='registration')

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    if 'user_id' not in session:
        flash('Please register or login first.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user:
        # Generate and send new OTP
        otp = save_otp(user, 'registration')
        send_result = send_otp_email(user, otp, 'registration')
        
        # Store OTP in session for testing purposes
        session['debug_otp'] = otp
        
        # Store email sending result in session
        session['email_sent_success'] = send_result
        
        if send_result:
            flash('A new OTP has been sent to your email.', 'success')
        else:
            flash('We could not send the email. Please check your internet connection and try again.', 'warning')
    else:
        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('auth.register'))
    
    return redirect(url_for('auth.verify_account'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
