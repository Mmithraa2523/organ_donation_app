import random
import string
from datetime import datetime, timedelta
from flask_mail import Message
from flask import url_for
from app import mail, db
from models import OTPVerification, OrganDonation, OrganRequest, BloodDonation, BloodRequest
import logging

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_notification(user, subject, body_text, body_html=None):
    """
    General notification function to send emails to users
    
    Args:
        user: User object to send notification to
        subject: Email subject
        body_text: Plain text email content
        body_html: HTML email content (optional)
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    from app import app
    try:
        logging.info(f"Attempting to send notification email to: {user.email}")
        msg = Message(
            subject,
            recipients=[user.email]
        )
        
        # Set email content
        msg.body = body_text
        if body_html:
            msg.html = body_html
        
        # Try to send email
        try:
            mail.send(msg)
            logging.info(f"Successfully sent notification email to: {user.email}")
            return True
        except Exception as mail_error:
            logging.error(f"Mail delivery error: {str(mail_error)}")
            logging.error(f"Email config: Server={app.config.get('MAIL_SERVER')}, Port={app.config.get('MAIL_PORT')}")
            return False
    except Exception as e:
        logging.error(f"Error in notification function: {str(e)}")
        return False

def send_otp_email(user, otp, purpose):
    """Send OTP email to user"""
    # Create appropriate email subject and content based on purpose
    if purpose == 'registration':
        subject = 'OTP Verification - Organ & Blood Donation System'
        body_text = f'''Dear {user.username},

Thank you for registering with the Organ & Blood Donation System.
Your OTP for account verification is: {otp}

This OTP will expire in 10 minutes.

Thank you,
The Organ & Blood Donation Team
'''
        body_html = f'''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2a5885;">Organ & Blood Donation System</h2>
        <p style="font-size: 18px; color: #333;">Account Verification</p>
    </div>
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p>Dear <strong>{user.username}</strong>,</p>
        <p>Thank you for registering with the Organ & Blood Donation System.</p>
        <p>Your OTP for account verification is:</p>
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #2a5885; background-color: #eef2f7; padding: 10px 20px; border-radius: 4px;">{otp}</span>
        </div>
        <p>This OTP will expire in 10 minutes.</p>
    </div>
    <div style="margin-top: 20px; font-size: 12px; color: #777; text-align: center;">
        <p>&copy; Organ & Blood Donation System. All rights reserved.</p>
    </div>
</div>
'''
    elif purpose in ['donation', 'blood_donation']:
        donation_type = 'blood donation' if purpose == 'blood_donation' else 'organ donation'
        subject = f'OTP Verification - {donation_type.capitalize()} - Organ & Blood Donation System'
        body_text = f'''Dear {user.username},

Thank you for your {donation_type}.
Your OTP for verification at the collection center is: {otp}

Please show this OTP to the doctor during collection.

Thank you for your noble gesture,
The Organ & Blood Donation Team
'''
        body_html = f'''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2a5885;">Organ & Blood Donation System</h2>
        <p style="font-size: 18px; color: #333;">Donation Verification</p>
    </div>
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p>Dear <strong>{user.username}</strong>,</p>
        <p>Thank you for your {donation_type}.</p>
        <p>Your OTP for verification at the collection center is:</p>
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #2a5885; background-color: #eef2f7; padding: 10px 20px; border-radius: 4px;">{otp}</span>
        </div>
        <p>Please show this OTP to the doctor during collection.</p>
        <p>Thank you for your noble gesture.</p>
    </div>
    <div style="margin-top: 20px; font-size: 12px; color: #777; text-align: center;">
        <p>&copy; Organ & Blood Donation System. All rights reserved.</p>
    </div>
</div>
'''
    else:
        subject = f'OTP Verification - Organ & Blood Donation System'
        body_text = f'''Dear {user.username},

Your verification OTP is: {otp}

This OTP will expire in 10 minutes.

Thank you,
The Organ & Blood Donation Team
'''
        body_html = None
    
    # For debugging purposes
    logging.info(f"FOR TESTING ONLY - USER: {user.username}, OTP: {otp}")
    
    # Send the notification email
    return send_notification(user, subject, body_text, body_html)

def save_otp(user, purpose, expiry_minutes=10):
    """Generate and save OTP for a user"""
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    verification = OTPVerification(
        user_id=user.id,
        otp=otp,
        purpose=purpose,
        expires_at=expires_at
    )
    
    db.session.add(verification)
    db.session.commit()
    
    return otp

def verify_otp(user_id, otp, purpose):
    """Verify OTP for a user"""
    verification = OTPVerification.query.filter_by(
        user_id=user_id,
        otp=otp,
        purpose=purpose,
        is_used=False
    ).order_by(OTPVerification.created_at.desc()).first()
    
    if not verification:
        return False
    
    if verification.expires_at < datetime.utcnow():
        return False
    
    verification.is_used = True
    db.session.commit()
    
    return True

def get_blood_compatibility():
    """Return blood compatibility mapping for matching"""
    return {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
    }

def calculate_hla_match_score(donor_hla, recipient_hla):
    """Calculate HLA match score between donor and recipient
    Returns a score from 0 (no match) to 6 (perfect match)
    """
    if not donor_hla or not recipient_hla:
        return 3  # Middle score if either HLA is unknown
        
    # Common HLA types
    hla_types = ['A1', 'A2', 'B7', 'B8', 'DR1', 'DR2']
    
    # Mock scoring based on partial string match
    # In a real system, this would be much more complex medical analysis
    if donor_hla == recipient_hla:
        return 6  # Perfect match
    elif donor_hla.startswith(recipient_hla[:1]) or recipient_hla.startswith(donor_hla[:1]):
        return 4  # Partial match
    else:
        return 1  # Poor match

def calculate_geographic_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two geographic coordinates using Haversine formula
    Returns distance in kilometers
    """
    import math
    
    # If any coordinates are missing, return a large distance
    if not all([lat1, lng1, lat2, lng2]):
        return 10000  # Large distance (10,000 km)
    
    # Earth radius in kilometers
    R = 6371
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def calculate_size_match_score(donor_age, recipient_age, organ_type):
    """Calculate size match score based on age difference and organ type
    Returns a score from 0 (poor match) to 10 (excellent match)
    """
    if donor_age is None or recipient_age is None:
        return 5  # Middle score if either age is unknown
    
    age_difference = abs(donor_age - recipient_age)
    
    # Different organs have different size matching requirements
    if organ_type in ['heart', 'lungs', 'liver']:
        # These organs are more size-sensitive
        if age_difference <= 5:
            return 10
        elif age_difference <= 10:
            return 8
        elif age_difference <= 15:
            return 6
        elif age_difference <= 20:
            return 4
        else:
            return 2
    else:
        # Kidneys, corneas, etc. are less size-sensitive
        if age_difference <= 10:
            return 10
        elif age_difference <= 20:
            return 8
        elif age_difference <= 30:
            return 6
        else:
            return 4

def calculate_urgency_score(request):
    """Calculate an urgency score for an organ request
    Returns a score from 0 (low urgency) to 100 (highest urgency)
    """
    base_score = 0
    
    # Factor 1: Explicitly set medical urgency score (if available)
    if request.medical_urgency_score:
        base_score = request.medical_urgency_score
    
    # Factor 2: Urgency level from the form
    urgency_multiplier = 1.0
    if request.urgency_level == 'normal':
        urgency_multiplier = 1.0
    elif request.urgency_level == 'urgent':
        urgency_multiplier = 1.5
    elif request.urgency_level == 'critical':
        urgency_multiplier = 2.0
    
    # Factor 3: Waiting time (days)
    waiting_time_score = 0
    if request.waiting_time_days:
        waiting_time_score = min(20, request.waiting_time_days / 30 * 10)  # Max 20 points for waiting time
    
    # Factor 4: Previous transplants
    previous_transplant_score = 0
    if request.previous_transplants:
        previous_transplant_score = min(10, request.previous_transplants * 5)  # Max 10 points
    
    # Calculate final score with a cap at 100
    final_score = min(100, (base_score * urgency_multiplier) + waiting_time_score + previous_transplant_score)
    
    return final_score

def calculate_total_match_score(request, donation):
    """Calculate an overall match score between request and donation
    Returns a total score from 0 (poor match) to 100 (perfect match)
    """
    scores = {}
    
    # 1. Blood compatibility (basic requirement) - 20 points
    blood_compatibility = get_blood_compatibility()
    compatible_blood_groups = blood_compatibility.get(request.blood_group, [])
    
    if donation.blood_group in compatible_blood_groups:
        if donation.blood_group == request.blood_group:
            scores['blood'] = 20  # Exact match
        else:
            scores['blood'] = 15  # Compatible but not exact
    else:
        scores['blood'] = 0  # Not compatible
        return 0  # Immediate disqualification
    
    # 2. HLA matching - 25 points
    hla_score = calculate_hla_match_score(
        donation.hla_type, 
        request.hla_type
    )
    scores['hla'] = (hla_score / 6) * 25  # Scale from 0-6 to 0-25
    
    # 3. Geographic distance - 15 points
    # Closer is better for time-sensitive organs
    distance = calculate_geographic_distance(
        donation.location_lat, donation.location_lng,
        request.location_lat, request.location_lng
    )
    
    # Time-sensitive organs have higher geographic weight
    if request.organ_type in ['heart', 'lungs', 'liver']:
        if distance <= 50:  # Within 50km
            scores['distance'] = 15
        elif distance <= 100:
            scores['distance'] = 12
        elif distance <= 250:
            scores['distance'] = 8
        elif distance <= 500:
            scores['distance'] = 4
        else:
            scores['distance'] = 2
    else:
        # Less time-sensitive organs
        if distance <= 100:
            scores['distance'] = 15
        elif distance <= 250:
            scores['distance'] = 12
        elif distance <= 500:
            scores['distance'] = 10
        elif distance <= 1000:
            scores['distance'] = 8
        else:
            scores['distance'] = 5
    
    # 4. Size/age matching - 20 points
    size_score = calculate_size_match_score(
        donation.donor_age,
        request.patient_age,
        request.organ_type
    )
    scores['size'] = (size_score / 10) * 20  # Scale from 0-10 to 0-20
    
    # 5. Special factors - 20 points
    special_score = 0
    
    # Living donor bonus for applicable organs
    if donation.is_living_donor and request.organ_type in ['kidney', 'liver']:
        special_score += 10
    
    # Medical conditions matching
    if donation.medical_condition and request.medical_condition:
        if donation.medical_condition == request.medical_condition:
            special_score += 5
    else:
        special_score += 5  # No medical conditions or matching
    
    # Tissue crossmatch (crucial for transplant success)
    if donation.tissue_crossmatch == 'negative':  # Negative crossmatch is good
        special_score += 5
    
    scores['special'] = special_score
    
    # Calculate total score (0-100)
    total_score = sum(scores.values())
    
    return total_score

def find_organ_matches():
    """Find potential organ donation and request matches using advanced algorithm"""
    # Get all pending organ requests
    pending_requests = OrganRequest.query.filter_by(status='pending').order_by(
        OrganRequest.urgency_level.desc(),
        OrganRequest.date_requested
    ).all()
    
    matches = []
    
    for request in pending_requests:
        # Find compatible donations (same organ type and potentially compatible blood group)
        compatible_donations = OrganDonation.query.filter_by(
            organ_type=request.organ_type,
            status='approved'
        ).all()
        
        blood_compatibility = get_blood_compatibility()
        compatible_blood_groups = blood_compatibility.get(request.blood_group, [])
        
        # Calculate urgency score for this request
        urgency_score = calculate_urgency_score(request)
        
        request_matches = []
        for donation in compatible_donations:
            # Check basic blood compatibility
            if donation.blood_group in compatible_blood_groups:
                # Calculate match score using our advanced algorithm
                match_score = calculate_total_match_score(request, donation)
                
                # Categorize compatibility based on score
                compatibility = 'poor'
                if match_score >= 80:
                    compatibility = 'excellent'
                elif match_score >= 65:
                    compatibility = 'very good'
                elif match_score >= 50:
                    compatibility = 'good'
                elif match_score >= 35:
                    compatibility = 'fair'
                
                # Only include matches with at least fair compatibility
                if match_score >= 35:
                    request_matches.append({
                        'request': request,
                        'donation': donation,
                        'compatibility': compatibility,
                        'match_score': match_score,
                        'urgency_score': urgency_score
                    })
        
        # Sort matches for this request by match score (highest first)
        request_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add to overall matches
        matches.extend(request_matches)
    
    # Sort all matches by urgency (highest first), then by match score (highest first)
    matches.sort(key=lambda x: (x['urgency_score'], x['match_score']), reverse=True)
    
    logging.debug(f"Advanced matching algorithm found {len(matches)} potential organ matches")
    return matches

def send_status_notification(user, item_type, status, additional_details=None):
    """
    Send a notification email when a donation or request status is updated
    
    Args:
        user: User object to send notification to
        item_type: Type of item (organ donation, blood donation, organ request, blood request)
        status: New status of the item
        additional_details: Any additional details to include in the notification
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    subject = f'Status Update - {item_type.capitalize()} - Organ & Blood Donation System'
    
    status_messages = {
        'pending': 'is being reviewed by our team',
        'approved': 'has been approved',
        'unavailable': 'is currently unavailable',
        'fulfilled': 'has been successfully fulfilled',
        'rejected': 'could not be processed at this time'
    }
    
    status_colors = {
        'pending': '#3498db',  # Blue
        'approved': '#2ecc71',  # Green
        'unavailable': '#e74c3c',  # Red
        'fulfilled': '#27ae60',  # Dark Green
        'rejected': '#c0392b'   # Dark Red
    }
    
    status_message = status_messages.get(status, 'has been updated')
    status_color = status_colors.get(status, '#7f8c8d')  # Default gray
    
    body_text = f'''Dear {user.username},

Your {item_type} {status_message}.

'''
    
    if additional_details:
        body_text += f"Additional information: {additional_details}\n\n"
    
    body_text += '''Thank you for using the Organ & Blood Donation System.

Regards,
The Organ & Blood Donation Team
'''
    
    body_html = f'''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2a5885;">Organ & Blood Donation System</h2>
        <p style="font-size: 18px; color: #333;">Status Update</p>
    </div>
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p>Dear <strong>{user.username}</strong>,</p>
        <p>Your {item_type} <span style="color: {status_color}; font-weight: bold;">{status_message}</span>.</p>
'''
    
    if additional_details:
        body_html += f'''
        <div style="background-color: #f0f0f0; padding: 10px; border-left: 3px solid {status_color}; margin: 15px 0;">
            <p style="margin: 0;"><strong>Additional information:</strong> {additional_details}</p>
        </div>
'''
    
    body_html += '''
        <p>Thank you for using the Organ & Blood Donation System.</p>
    </div>
    <div style="margin-top: 20px; font-size: 12px; color: #777; text-align: center;">
        <p>&copy; Organ & Blood Donation System. All rights reserved.</p>
    </div>
</div>
'''
    
    return send_notification(user, subject, body_text, body_html)

def find_blood_matches():
    """Find potential blood donation and request matches"""
    # Get all pending blood requests
    pending_requests = BloodRequest.query.filter_by(status='pending').order_by(
        BloodRequest.urgency_level.desc(),
        BloodRequest.date_requested
    ).all()
    
    matches = []
    
    for request in pending_requests:
        # Find compatible donations (compatible blood group with sufficient quantity)
        blood_compatibility = get_blood_compatibility()
        compatible_blood_groups = blood_compatibility.get(request.blood_group, [])
        
        compatible_donations = BloodDonation.query.filter(
            BloodDonation.blood_group.in_(compatible_blood_groups),
            BloodDonation.status=='approved',
            BloodDonation.quantity_ml >= request.quantity_ml
        ).all()
        
        for donation in compatible_donations:
            matches.append({
                'request': request,
                'donation': donation,
                'compatibility': 'full'
            })
    
    return matches
