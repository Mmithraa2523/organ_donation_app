from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_login import login_required, current_user
from app import db
from models import User, Doctor, OrganDonation, OrganRequest, BloodDonation, BloodRequest
from forms import UpdateRequestStatusForm, OTPCollectionForm
from utils import verify_otp, generate_otp, send_otp_email, send_status_notification
from datetime import datetime
import logging

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

# Doctor access decorator
def doctor_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.get_role() != 'doctor':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    
    # Preserve the function name of the decorated function
    decorated_function.__name__ = f.__name__
    return decorated_function

@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get assigned organ requests
    organ_requests = OrganRequest.query.filter_by(assigned_doctor_id=doctor.id).all()
    new_requests_count = len([r for r in organ_requests if r.status == 'pending'])
    
    # Get assigned organ collections
    organ_collections = OrganDonation.query.filter_by(collection_doctor_id=doctor.id).all()
    pending_organ_collections_count = len([d for d in organ_collections if d.status == 'approved' and not d.otp_verified])
    
    # Get blood donations ready for collection
    blood_collections = BloodDonation.query.filter_by(status='approved').all()
    pending_blood_collections_count = len([d for d in blood_collections if not d.otp_verified])
    
    # Total pending collections
    pending_collections_count = pending_organ_collections_count + pending_blood_collections_count
    
    return render_template('doctor/dashboard.html', 
                          title='Doctor Dashboard',
                          doctor=doctor,
                          new_requests_count=new_requests_count,
                          pending_collections_count=pending_collections_count,
                          pending_organ_collections_count=pending_organ_collections_count,
                          pending_blood_collections_count=pending_blood_collections_count,
                          organ_requests=organ_requests,
                          organ_collections=organ_collections,
                          blood_collections=blood_collections)

@doctor_bp.route('/organ-requests')
@doctor_required
def organ_requests():
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get assigned organ requests
    organ_requests = OrganRequest.query.filter_by(assigned_doctor_id=doctor.id).all()
    
    return render_template('doctor/organ_requests.html', 
                          title='Assigned Organ Requests',
                          organ_requests=organ_requests)

@doctor_bp.route('/organ-requests/<int:request_id>/update', methods=['GET', 'POST'])
@doctor_required
def update_request_status(request_id):
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get the organ request
    organ_request = OrganRequest.query.get_or_404(request_id)
    
    # Check if doctor is authorized
    if organ_request.assigned_doctor_id != doctor.id:
        flash('You are not authorized to update this request.', 'danger')
        return redirect(url_for('doctor.organ_requests'))
    
    form = UpdateRequestStatusForm()
    
    if form.validate_on_submit():
        old_status = organ_request.status
        new_status = form.status.data
        organ_request.status = new_status
        db.session.commit()
        
        # Send notification email to the requester
        requester = User.query.get(organ_request.user_id)
        additional_details = None
        
        if new_status == 'approved':
            additional_details = f"Your organ request for a {organ_request.organ_type} has been approved. A medical coordinator will contact you about next steps."
        elif new_status == 'unavailable':
            additional_details = f"We're still searching for a matching {organ_request.organ_type} donation. We'll update you as soon as a match is found."
        elif new_status == 'fulfilled':
            additional_details = f"Your {organ_request.organ_type} transplant request has been fulfilled. Your medical team will provide further details."
            
        # Send the email notification
        send_status_notification(
            requester, 
            f'organ request for {organ_request.organ_type}', 
            new_status, 
            additional_details
        )
        
        flash(f'Organ request status has been updated from {old_status} to {new_status}. A notification email has been sent to the requester.', 'success')
        return redirect(url_for('doctor.organ_requests'))
    
    # Pre-populate form
    form.status.data = organ_request.status
    
    return render_template('doctor/update_request_status.html', 
                          title='Update Request Status',
                          form=form,
                          request=organ_request)

@doctor_bp.route('/organ-collections')
@doctor_required
def organ_collections():
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    logging.debug(f"Doctor collections page accessed by: {doctor.user.username}, ID: {doctor.id}")
    
    # Get assigned organ collections
    organ_collections = OrganDonation.query.filter_by(collection_doctor_id=doctor.id).all()
    logging.debug(f"Found {len(organ_collections)} assigned collections")
    
    # Generate OTPs for any approved collections that don't have them
    for donation in organ_collections:
        if donation.status == 'approved' and not donation.otp_verified and not donation.otp:
            otp = generate_otp()
            donation.otp = otp
            db.session.commit()
            
            # Send OTP to donor
            donor = User.query.get(donation.user_id)
            send_otp_email(donor, otp, 'donation')
            
            flash(f'An OTP has been generated for donation #{donation.id} and sent to the donor.', 'info')
        
        logging.debug(f"Donation ID: {donation.id}, Status: {donation.status}, " 
                     f"OTP: {donation.otp}, Verified: {donation.otp_verified}, "
                     f"Donor: {donation.donor.username if donation.donor else 'Unknown'}")
    
    # Create OTP collection form for the modal
    form = OTPCollectionForm()
    
    return render_template('doctor/organ_collections.html', 
                          title='Organ Collections',
                          organ_collections=organ_collections,
                          form=form)

@doctor_bp.route('/organ-collections/<int:donation_id>/verify', methods=['GET', 'POST'])
@doctor_required
def verify_collection(donation_id):
    logging.debug(f"Starting verify_collection for donation_id: {donation_id}")
    
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    logging.debug(f"Doctor handling verification: {doctor.user.username}, ID: {doctor.id}")
    
    # Get the organ donation
    donation = OrganDonation.query.get_or_404(donation_id)
    logging.debug(f"Found donation: {donation.id}, status: {donation.status}, OTP: {donation.otp}, verified: {donation.otp_verified}")
    
    # Check if doctor is authorized
    if donation.collection_doctor_id != doctor.id:
        logging.warning(f"Unauthorized doctor {doctor.id} attempted to verify donation {donation_id}")
        flash('You are not authorized to verify this collection.', 'danger')
        return redirect(url_for('doctor.organ_collections'))
    
    form = OTPCollectionForm()
    
    # Generate a new OTP and send it by email when the verify page is loaded (GET request)
    if request.method == 'GET' and donation.status == 'approved' and not donation.otp_verified:
        logging.debug("Generating new OTP for donation")
        otp = generate_otp()
        donation.otp = otp
        db.session.commit()
        
        # Send OTP to donor
        donor = User.query.get(donation.user_id)
        send_result = send_otp_email(donor, otp, 'donation')
        logging.debug(f"OTP email send result: {send_result}")
        
        if send_result:
            flash('An OTP has been generated and sent to the donor\'s email.', 'success')
        else:
            flash('Failed to send OTP email to the donor. Please try again or contact support.', 'danger')
        
        # Add email status to session for display in the template
        session['email_sent_success'] = send_result
        return render_template('doctor/verify_collection.html', 
                              title='Verify Organ Collection',
                              donation=donation,
                              form=form,
                              donor=donor)
    
    # Handle form submission
    if form.validate_on_submit():
        logging.debug(f"Form validated, OTP entered: {form.otp.data}")
        # Verify OTP
        if donation.otp and donation.otp == form.otp.data:
            logging.debug("OTP match successful!")
            donation.otp_verified = True
            donation.collection_date = datetime.utcnow()
            donation.status = 'collected'
            db.session.commit()
            
            # Send notification email to the donor
            donor = User.query.get(donation.user_id)
            additional_details = f"Your donation of {donation.organ_type} has been successfully collected and verified by Dr. {doctor.user.username} at {doctor.hospital.name}. Thank you for your noble gesture."
            
            # Send the email notification
            send_status_notification(
                donor, 
                f'organ donation of {donation.organ_type}', 
                'collected', 
                additional_details
            )
            
            flash('Organ collection has been verified successfully. A confirmation email has been sent to the donor.', 'success')
            return redirect(url_for('doctor.organ_collections'))
        else:
            logging.debug(f"OTP mismatch: Expected {donation.otp or 'None'}, got {form.otp.data}")
            flash('Invalid OTP. Please try again.', 'danger')
            
            # Get the donor for template
            donor = User.query.get(donation.user_id)
            return render_template('doctor/verify_collection.html', 
                                  title='Verify Organ Collection',
                                  donation=donation,
                                  form=form,
                                  donor=donor)
    
    # If form validation failed on POST
    if request.method == 'POST':
        logging.debug(f"Form validation failed: {form.errors}")
        flash('Please enter a valid OTP.', 'warning')
        
        # Get the donor for template
        donor = User.query.get(donation.user_id)
        return render_template('doctor/verify_collection.html', 
                              title='Verify Organ Collection',
                              donation=donation,
                              form=form,
                              donor=donor)
    
    # Default fallback (shouldn't normally reach here)
    logging.debug("Redirecting to organ_collections")
    return redirect(url_for('doctor.organ_collections'))

@doctor_bp.route('/blood-collections')
@doctor_required
def blood_collections():
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    logging.debug(f"Doctor blood collections page accessed by: {doctor.user.username}, ID: {doctor.id}")
    
    # Get all approved blood donations
    blood_collections = BloodDonation.query.filter_by(status='approved').all()
    logging.debug(f"Found {len(blood_collections)} blood collections")
    
    # Generate OTPs for any approved collections that don't have them
    for donation in blood_collections:
        if donation.status == 'approved' and not donation.otp_verified and not donation.otp:
            otp = generate_otp()
            donation.otp = otp
            db.session.commit()
            
            # Send OTP to donor
            donor = User.query.get(donation.user_id)
            send_otp_email(donor, otp, 'blood_donation')
            
            flash(f'An OTP has been generated for blood donation #{donation.id} and sent to the donor.', 'info')
        
        logging.debug(f"Blood Donation ID: {donation.id}, Status: {donation.status}, " 
                     f"OTP: {donation.otp}, Verified: {donation.otp_verified}, "
                     f"Donor: {donation.donor.username if donation.donor else 'Unknown'}")
    
    # Create OTP collection form for the modal
    form = OTPCollectionForm()
    
    return render_template('doctor/blood_collections.html', 
                          title='Blood Collections',
                          blood_collections=blood_collections,
                          form=form)

@doctor_bp.route('/blood-collections/<int:donation_id>/verify', methods=['GET', 'POST'])
@doctor_required
def verify_blood_collection(donation_id):
    logging.debug(f"Starting verify_blood_collection for donation_id: {donation_id}")
    
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    logging.debug(f"Doctor handling verification: {doctor.user.username}, ID: {doctor.id}")
    
    # Get the blood donation
    donation = BloodDonation.query.get_or_404(donation_id)
    logging.debug(f"Found blood donation: {donation.id}, status: {donation.status}, OTP: {donation.otp}, verified: {donation.otp_verified}")
    
    form = OTPCollectionForm()
    
    # Generate a new OTP and send it by email when the verify page is loaded (GET request)
    if request.method == 'GET' and donation.status == 'approved' and not donation.otp_verified:
        logging.debug("Generating new OTP for blood donation")
        otp = generate_otp()
        donation.otp = otp
        db.session.commit()
        
        # Send OTP to donor
        donor = User.query.get(donation.user_id)
        send_result = send_otp_email(donor, otp, 'blood_donation')
        logging.debug(f"OTP email send result: {send_result}")
        
        if send_result:
            flash('An OTP has been generated and sent to the donor\'s email.', 'success')
        else:
            flash('Failed to send OTP email to the donor. Please try again or contact support.', 'danger')
        
        # Add email status to session for display in the template
        session['email_sent_success'] = send_result
        return render_template('doctor/verify_blood_collection.html', 
                              title='Verify Blood Collection',
                              donation=donation,
                              form=form,
                              donor=donor)
    
    # Handle form submission
    if form.validate_on_submit():
        logging.debug(f"Form validated, OTP entered: {form.otp.data}")
        # Verify OTP
        if donation.otp and donation.otp == form.otp.data:
            logging.debug("OTP match successful!")
            donation.otp_verified = True
            donation.collection_date = datetime.utcnow()
            donation.status = 'collected'
            db.session.commit()
            
            # Send notification email to the donor
            donor = User.query.get(donation.user_id)
            additional_details = f"Your blood donation ({donation.blood_group}, {donation.quantity_ml}ml) has been successfully collected and verified by Dr. {doctor.user.username}. Thank you for your noble gesture."
            
            # Send the email notification
            send_status_notification(
                donor, 
                'blood donation', 
                'collected', 
                additional_details
            )
            
            flash('Blood collection has been verified successfully. A confirmation email has been sent to the donor.', 'success')
            return redirect(url_for('doctor.blood_collections'))
        else:
            logging.debug(f"OTP mismatch: Expected {donation.otp or 'None'}, got {form.otp.data}")
            flash('Invalid OTP. Please try again.', 'danger')
            
            # Get the donor for template
            donor = User.query.get(donation.user_id)
            return render_template('doctor/verify_blood_collection.html', 
                                  title='Verify Blood Collection',
                                  donation=donation,
                                  form=form,
                                  donor=donor)
    
    # If form validation failed on POST
    if request.method == 'POST':
        logging.debug(f"Form validation failed: {form.errors}")
        flash('Please enter a valid OTP.', 'warning')
        
        # Get the donor for template
        donor = User.query.get(donation.user_id)
        return render_template('doctor/verify_blood_collection.html', 
                              title='Verify Blood Collection',
                              donation=donation,
                              form=form,
                              donor=donor)
    
    # Default fallback (shouldn't normally reach here)
    logging.debug("Redirecting to blood_collections")
    return redirect(url_for('doctor.blood_collections'))
