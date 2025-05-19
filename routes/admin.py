from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db
from models import User, Doctor, Hospital, OrganDonation, OrganRequest, BloodDonation, BloodRequest, Role
from forms import DoctorForm, HospitalForm, AssignDoctorForm, UpdateRequestStatusForm
from werkzeug.security import generate_password_hash
from utils import find_organ_matches, find_blood_matches, generate_otp, send_otp_email
from sqlalchemy import desc
import logging
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin access decorator
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.get_role() != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    
    # Preserve the function name of the decorated function
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get counts for dashboard
    users_count = User.query.filter(User.role_id!=Role.query.filter_by(name='admin').first().id).count()
    doctors_count = Doctor.query.count()
    hospitals_count = Hospital.query.count()
    
    organ_donations_count = OrganDonation.query.count()
    organ_requests_count = OrganRequest.query.count()
    blood_donations_count = BloodDonation.query.count()
    blood_requests_count = BloodRequest.query.count()
    
    # Get recent activities
    recent_organ_donations = OrganDonation.query.order_by(desc(OrganDonation.date_added)).limit(5).all()
    recent_organ_requests = OrganRequest.query.order_by(desc(OrganRequest.date_requested)).limit(5).all()
    recent_blood_donations = BloodDonation.query.order_by(desc(BloodDonation.date_added)).limit(5).all()
    recent_blood_requests = BloodRequest.query.order_by(desc(BloodRequest.date_requested)).limit(5).all()
    
    # Find matches
    organ_matches = find_organ_matches()
    blood_matches = find_blood_matches()
    matches_count = len(organ_matches) + len(blood_matches)
    
    return render_template('admin/dashboard.html', 
                          title='Admin Dashboard',
                          users_count=users_count,
                          doctors_count=doctors_count,
                          hospitals_count=hospitals_count,
                          organ_donations_count=organ_donations_count,
                          organ_requests_count=organ_requests_count,
                          blood_donations_count=blood_donations_count,
                          blood_requests_count=blood_requests_count,
                          recent_organ_donations=recent_organ_donations,
                          recent_organ_requests=recent_organ_requests,
                          recent_blood_donations=recent_blood_donations,
                          recent_blood_requests=recent_blood_requests,
                          matches_count=matches_count)

@admin_bp.route('/doctors')
@admin_required
def doctors():
    doctors = Doctor.query.all()
    return render_template('admin/doctors.html', title='Manage Doctors', doctors=doctors)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    form = DoctorForm()
    
    # Populate hospital choices
    hospitals = Hospital.query.all()
    form.hospital.choices = [(h.id, h.name) for h in hospitals]
    
    if form.validate_on_submit():
        # Get the doctor role
        doctor_role = Role.query.filter_by(name='doctor').first()
        
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            phone=form.phone.data,
            role_id=doctor_role.id,
            is_verified=True
        )
        
        db.session.add(user)
        db.session.flush()  # This gives user.id without committing
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            hospital_id=form.hospital.data,
            specialization=form.specialization.data,
            license_number=form.license_number.data
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        flash(f'Doctor {form.username.data} has been added successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/add_doctor.html', title='Add Doctor', form=form)

@admin_bp.route('/hospitals')
@admin_required
def hospitals():
    hospitals = Hospital.query.all()
    form = HospitalForm()
    return render_template('admin/hospitals.html', title='Manage Hospitals', hospitals=hospitals, form=form)

@admin_bp.route('/hospitals/add', methods=['GET', 'POST'])
@admin_required
def add_hospital():
    form = HospitalForm()
    
    if form.validate_on_submit():
        hospital = Hospital(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            phone=form.phone.data
        )
        
        db.session.add(hospital)
        db.session.commit()
        
        flash(f'Hospital {form.name.data} has been added successfully!', 'success')
        return redirect(url_for('admin.hospitals'))
    
    return render_template('admin/hospitals.html', title='Add Hospital', form=form, add_mode=True)

@admin_bp.route('/users')
@admin_required
def users():
    users = User.query.filter(User.role_id==Role.query.filter_by(name='user').first().id).all()
    return render_template('admin/users.html', title='User Details', users=users)

@admin_bp.route('/organ-donations')
@admin_required
def organ_donations():
    donations = OrganDonation.query.order_by(desc(OrganDonation.date_added)).all()
    return render_template('admin/organ_donations.html', title='Organ Donations', donations=donations)

@admin_bp.route('/organ-donations/<int:donation_id>/assign-doctor', methods=['GET', 'POST'])
@admin_required
def assign_doctor_to_donation(donation_id):
    donation = OrganDonation.query.get_or_404(donation_id)
    form = AssignDoctorForm()
    
    # Populate doctor choices
    doctors = Doctor.query.all()
    form.doctor.choices = [(d.id, f"Dr. {d.user.username} - {d.specialization} - {d.hospital.name}") for d in doctors]
    
    if form.validate_on_submit():
        # Assign doctor and change status
        donation.collection_doctor_id = form.doctor.data
        donation.status = 'approved'
        
        # Generate OTP for donation verification
        otp = generate_otp()
        donation.otp = otp
        
        # Save to database
        db.session.commit()
        
        # Send OTP to donor
        donor = User.query.get(donation.user_id)
        send_otp_email(donor, otp, 'donation')
        
        flash('Doctor has been assigned for organ collection and OTP has been sent to donor.', 'success')
        return redirect(url_for('admin.organ_donations'))
    
    return render_template('admin/assign_doctor.html', 
                          title='Assign Doctor for Organ Collection',
                          form=form,
                          donation=donation)

@admin_bp.route('/organ-requests')
@admin_required
def organ_requests():
    requests = OrganRequest.query.order_by(desc(OrganRequest.date_requested)).all()
    return render_template('admin/organ_requests.html', title='Organ Requests', requests=requests)

@admin_bp.route('/organ-requests/<int:request_id>/assign-doctor', methods=['GET', 'POST'])
@admin_required
def assign_doctor_to_request(request_id):
    organ_request = OrganRequest.query.get_or_404(request_id)
    form = AssignDoctorForm()
    
    # Populate doctor choices
    doctors = Doctor.query.all()
    form.doctor.choices = [(d.id, f"Dr. {d.user.username} - {d.specialization} - {d.hospital.name}") for d in doctors]
    
    if form.validate_on_submit():
        organ_request.assigned_doctor_id = form.doctor.data
        db.session.commit()
        
        flash('Doctor has been assigned for organ request.', 'success')
        return redirect(url_for('admin.organ_requests'))
    
    return render_template('admin/assign_doctor.html', 
                          title='Assign Doctor for Organ Request',
                          form=form,
                          request=organ_request)

@admin_bp.route('/blood-donations', methods=['GET', 'POST'])
@admin_required
def blood_donations():
    # Handle POST requests to approve donations
    if request.method == 'POST':
        donation_id = request.form.get('donation_id')
        if donation_id:
            try:
                donation = BloodDonation.query.get_or_404(int(donation_id))
                donation.status = 'approved'
                db.session.commit()
                flash('Blood donation has been approved successfully.', 'success')
            except Exception as e:
                logging.error(f"Error updating blood donation: {str(e)}")
                flash('An error occurred while updating the donation.', 'danger')
        return redirect(url_for('admin.blood_donations'))
        
    # GET request - show all donations
    donations = BloodDonation.query.order_by(desc(BloodDonation.date_added)).all()
    return render_template('admin/blood_donations.html', title='Blood Donations', donations=donations)

@admin_bp.route('/blood-requests', methods=['GET', 'POST'])
@admin_required
def blood_requests():
    # Handle POST requests to update request status
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        status = request.form.get('status')
        
        if request_id and status:
            try:
                blood_req = BloodRequest.query.get_or_404(int(request_id))
                blood_req.status = status
                db.session.commit()
                flash(f'Blood request status has been updated to {status}.', 'success')
            except Exception as e:
                logging.error(f"Error updating blood request: {str(e)}")
                flash('An error occurred while updating the request.', 'danger')
        return redirect(url_for('admin.blood_requests'))
    
    # GET request - show all requests
    requests = BloodRequest.query.order_by(desc(BloodRequest.date_requested)).all()
    return render_template('admin/blood_requests.html', title='Blood Requests', requests=requests)

@admin_bp.route('/matching')
@admin_required
def matching():
    try:
        organ_matches = find_organ_matches()
        blood_matches = find_blood_matches()
        
        # Log the match counts for debugging
        logging.debug(f"Found {len(organ_matches)} organ matches and {len(blood_matches)} blood matches")
        
        return render_template('admin/matching.html', 
                              title='Donation Matching',
                              organ_matches=organ_matches or [],
                              blood_matches=blood_matches or [])
    except Exception as e:
        logging.error(f"Error in matching route: {str(e)}")
        flash('An error occurred while finding matches. Please try again later.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/match-organ/<int:request_id>/<int:donation_id>', methods=['POST'])
@admin_required
def match_organ(request_id, donation_id):
    organ_request = OrganRequest.query.get_or_404(request_id)
    organ_donation = OrganDonation.query.get_or_404(donation_id)
    
    # Update status and link them
    organ_request.status = 'approved'
    organ_request.matched_donation_id = donation_id
    organ_donation.status = 'approved'
    
    db.session.commit()
    
    flash('Organ donation has been matched with the request successfully!', 'success')
    return redirect(url_for('admin.matching'))

@admin_bp.route('/match-blood/<int:request_id>/<int:donation_id>', methods=['POST'])
@admin_required
def match_blood(request_id, donation_id):
    blood_request = BloodRequest.query.get_or_404(request_id)
    blood_donation = BloodDonation.query.get_or_404(donation_id)
    
    # Update status and link them
    blood_request.status = 'approved'
    blood_request.matched_donation_id = donation_id
    blood_donation.status = 'approved'
    
    db.session.commit()
    
    flash('Blood donation has been matched with the request successfully!', 'success')
    return redirect(url_for('admin.matching'))
