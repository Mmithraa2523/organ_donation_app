from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db
from models import User, OrganDonation, OrganRequest, BloodDonation, BloodRequest
from forms import OrganDonationForm, OrganRequestForm, BloodDonationForm, BloodRequestForm, ProfileUpdateForm, OTPVerificationForm
from utils import save_otp, send_otp_email, verify_otp
from datetime import datetime
import logging

user_bp = Blueprint('user', __name__, url_prefix='/user')

# User access decorator
def user_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.get_role() != 'user':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    
    # Preserve the function name of the decorated function
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def dashboard():
    # Get user's donations and requests
    organ_donations = OrganDonation.query.filter_by(user_id=current_user.id).all()
    organ_requests = OrganRequest.query.filter_by(user_id=current_user.id).all()
    blood_donations = BloodDonation.query.filter_by(user_id=current_user.id).all()
    blood_requests = BloodRequest.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/dashboard.html', 
                          title='User Dashboard',
                          organ_donations=organ_donations,
                          organ_requests=organ_requests,
                          blood_donations=blood_donations,
                          blood_requests=blood_requests)

@user_bp.route('/donate-organ', methods=['GET', 'POST'])
@user_required
def donate_organ():
    form = OrganDonationForm()
    
    if form.validate_on_submit():
        donation = OrganDonation(
            user_id=current_user.id,
            organ_type=form.organ_type.data,
            blood_group=form.blood_group.data,
            additional_info=form.additional_info.data,
            status='pending'
        )
        
        db.session.add(donation)
        db.session.commit()
        
        flash('Your organ donation has been registered successfully. Admin will review your donation.', 'success')
        return redirect(url_for('user.my_donations'))
    
    return render_template('user/donate_organ.html', title='Donate Organ', form=form)

@user_bp.route('/request-organ', methods=['GET', 'POST'])
@user_required
def request_organ():
    form = OrganRequestForm()
    
    if form.validate_on_submit():
        organ_request = OrganRequest(
            user_id=current_user.id,
            organ_type=form.organ_type.data,
            blood_group=form.blood_group.data,
            urgency_level=form.urgency_level.data,
            additional_info=form.additional_info.data,
            status='pending'
        )
        
        db.session.add(organ_request)
        db.session.commit()
        
        flash('Your organ request has been submitted successfully. Admin will review your request.', 'success')
        return redirect(url_for('user.my_requests'))
    
    return render_template('user/request_organ.html', title='Request Organ', form=form)

@user_bp.route('/donate-blood', methods=['GET', 'POST'])
@user_required
def donate_blood():
    form = BloodDonationForm()
    
    if form.validate_on_submit():
        donation = BloodDonation(
            user_id=current_user.id,
            blood_group=form.blood_group.data,
            quantity_ml=form.quantity_ml.data,
            additional_info=form.additional_info.data,
            status='pending'
        )
        
        db.session.add(donation)
        db.session.commit()
        
        flash('Your blood donation has been registered successfully. Admin will review your donation.', 'success')
        return redirect(url_for('user.my_donations'))
    
    return render_template('user/donate_blood.html', title='Donate Blood', form=form)

@user_bp.route('/request-blood', methods=['GET', 'POST'])
@user_required
def request_blood():
    form = BloodRequestForm()
    
    if form.validate_on_submit():
        blood_request = BloodRequest(
            user_id=current_user.id,
            blood_group=form.blood_group.data,
            quantity_ml=form.quantity_ml.data,
            urgency_level=form.urgency_level.data,
            additional_info=form.additional_info.data,
            status='pending'
        )
        
        db.session.add(blood_request)
        db.session.commit()
        
        flash('Your blood request has been submitted successfully. Admin will review your request.', 'success')
        return redirect(url_for('user.my_requests'))
    
    return render_template('user/request_blood.html', title='Request Blood', form=form)

@user_bp.route('/my-donations')
@user_required
def my_donations():
    organ_donations = OrganDonation.query.filter_by(user_id=current_user.id).all()
    blood_donations = BloodDonation.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/my_donations.html', 
                          title='My Donations',
                          organ_donations=organ_donations,
                          blood_donations=blood_donations)

@user_bp.route('/my-requests')
@user_required
def my_requests():
    organ_requests = OrganRequest.query.filter_by(user_id=current_user.id).all()
    blood_requests = BloodRequest.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/my_requests.html', 
                          title='My Requests',
                          organ_requests=organ_requests,
                          blood_requests=blood_requests)

@user_bp.route('/profile', methods=['GET', 'POST'])
@user_required
def profile():
    form = ProfileUpdateForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
    
    if form.validate_on_submit():
        # Check if username is taken by another user
        if form.username.data != current_user.username:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('Username already taken. Please choose another one.', 'danger')
                return render_template('user/profile.html', title='My Profile', form=form)
        
        # Check if email is taken by another user
        if form.email.data != current_user.email:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('Email already registered. Please use another one.', 'danger')
                return render_template('user/profile.html', title='My Profile', form=form)
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        
        db.session.commit()
        
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/profile.html', title='My Profile', form=form)
